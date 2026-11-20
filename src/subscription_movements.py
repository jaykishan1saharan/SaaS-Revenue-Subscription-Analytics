"""Analyze churn-event sequences and conservative subscription MRR matches."""

from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
EVENT_FILE = "ravenstack_churn_events.csv"
SUBSCRIPTION_FILE = "ravenstack_subscriptions.csv"

EVENT_COLUMNS = {
    "churn_event_id",
    "account_id",
    "churn_date",
    "is_reactivation",
}
SUBSCRIPTION_COLUMNS = {
    "subscription_id",
    "account_id",
    "start_date",
    "end_date",
    "mrr_amount",
}


def _require_columns(frame, required, label):
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{label} is missing required columns: {sorted(missing)}")


def _parse_date_column(frame, column, nullable=False):
    raw_values = frame[column]
    parsed = pd.to_datetime(raw_values, errors="coerce").dt.normalize()
    invalid = raw_values.notna() & parsed.isna()
    if invalid.any():
        raise ValueError(f"{column} contains invalid dates")
    if not nullable and parsed.isna().any():
        raise ValueError(f"{column} contains missing dates")
    return parsed


def _parse_boolean_column(values, column):
    if values.isna().any():
        raise ValueError(f"{column} contains missing values")
    if pd.api.types.is_bool_dtype(values.dtype):
        return values.astype(bool)

    normalized = values.astype(str).str.strip().str.lower()
    parsed = normalized.map({"true": True, "false": False})
    if parsed.isna().any():
        raise ValueError(f"{column} contains values other than true or false")
    return parsed.astype(bool)


def _prepare_events(churn_events):
    _require_columns(churn_events, EVENT_COLUMNS, "churn_events")
    events = churn_events.copy()
    if (
        events["churn_event_id"].isna().any()
        or events["churn_event_id"].duplicated().any()
    ):
        raise ValueError("churn_event_id must be non-null and unique")
    if events["account_id"].isna().any():
        raise ValueError("churn_events contains missing account_id values")
    events["churn_date"] = _parse_date_column(events, "churn_date")
    events["is_reactivation"] = _parse_boolean_column(
        events["is_reactivation"], "is_reactivation"
    )
    return events


def _prepare_subscriptions(subscriptions):
    _require_columns(subscriptions, SUBSCRIPTION_COLUMNS, "subscriptions")
    prepared = subscriptions.copy()
    if (
        prepared["subscription_id"].isna().any()
        or prepared["subscription_id"].duplicated().any()
    ):
        raise ValueError("subscription_id must be non-null and unique")
    if prepared["account_id"].isna().any():
        raise ValueError("subscriptions contains missing account_id values")
    prepared["start_date"] = _parse_date_column(prepared, "start_date")
    prepared["end_date"] = _parse_date_column(
        prepared, "end_date", nullable=True
    )
    prepared["mrr_amount"] = pd.to_numeric(
        prepared["mrr_amount"], errors="coerce"
    )
    if prepared["mrr_amount"].isna().any():
        raise ValueError("mrr_amount contains missing or non-numeric values")
    return prepared


def classify_event_sequences(churn_events):
    """Mark sequence evidence without ordering events that share an account/date."""
    events = _prepare_events(churn_events)
    daily = (
        events.groupby(["account_id", "churn_date"], as_index=False)
        .agg(
            same_day_event_count=("churn_event_id", "size"),
            has_candidate_churn=("is_reactivation", lambda values: (~values).any()),
            has_reactivation=("is_reactivation", "any"),
        )
        .sort_values(["account_id", "churn_date"])
        .reset_index(drop=True)
    )
    grouped = daily.groupby("account_id", sort=False)
    daily["previous_event_count"] = grouped["same_day_event_count"].shift()
    daily["previous_has_candidate_churn"] = grouped[
        "has_candidate_churn"
    ].shift()
    daily["previous_has_reactivation"] = grouped["has_reactivation"].shift()
    unambiguous_candidate_churn = (
        daily["has_candidate_churn"] & daily["same_day_event_count"].eq(1)
    )
    churns_before_current_date = (
        unambiguous_candidate_churn.groupby(daily["account_id"], sort=False).cumsum()
        - unambiguous_candidate_churn.astype(int)
    )
    daily["prior_candidate_churn_exists"] = churns_before_current_date.gt(0)

    result = events.merge(
        daily,
        on=["account_id", "churn_date"],
        how="left",
        validate="many_to_one",
    )

    def assessment(row):
        if row["same_day_event_count"] > 1:
            return "same_day_order_ambiguous"
        previous_count = row["previous_event_count"]
        if pd.isna(previous_count):
            return (
                "reactivation_without_prior_event"
                if row["is_reactivation"]
                else "initial_candidate_churn"
            )
        if previous_count > 1:
            return "previous_same_day_order_ambiguous"
        if row["is_reactivation"]:
            if row["previous_has_candidate_churn"]:
                return "reactivation_after_candidate_churn"
            return "reactivation_after_reactivation"
        if row["previous_has_reactivation"]:
            if row["prior_candidate_churn_exists"]:
                return "possible_repeated_churn_reactivation_cycle"
            return "candidate_churn_after_reactivation"
        return "repeated_candidate_churn_without_reactivation"

    result["sequence_assessment"] = result.apply(assessment, axis=1)
    result["sequence_supported_reactivation"] = result[
        "sequence_assessment"
    ].eq("reactivation_after_candidate_churn")
    result["possible_repeated_cycle_churn"] = result[
        "sequence_assessment"
    ].eq("possible_repeated_churn_reactivation_cycle")
    return result.sort_values(
        ["account_id", "churn_date", "churn_event_id"]
    ).reset_index(drop=True)


def map_churn_events_to_subscriptions(churn_events, subscriptions):
    """Map only one-to-one same-account, same-end-date candidate departures."""
    events = _prepare_events(churn_events)
    subs = _prepare_subscriptions(subscriptions)
    result = classify_event_sequences(events)

    event_day_counts = (
        events.groupby(["account_id", "churn_date"])["churn_event_id"]
        .size()
        .rename("same_day_event_count")
        .reset_index()
    )
    candidates = events.loc[~events["is_reactivation"]].merge(
        subs[
            [
                "subscription_id",
                "account_id",
                "start_date",
                "end_date",
                "mrr_amount",
            ]
        ],
        left_on=["account_id", "churn_date"],
        right_on=["account_id", "end_date"],
        how="left",
    )
    candidates = candidates.loc[
        candidates["subscription_id"].isna()
        | (candidates["start_date"] <= candidates["churn_date"])
    ]
    match_summary = (
        candidates.groupby("churn_event_id")
        .agg(
            exact_subscription_match_count=("subscription_id", "nunique"),
        )
        .reset_index()
    )
    unique_matches = candidates.loc[
        candidates["subscription_id"].notna()
    ].merge(
        match_summary.loc[
            match_summary["exact_subscription_match_count"].eq(1),
            ["churn_event_id"],
        ],
        on="churn_event_id",
        how="inner",
        validate="many_to_one",
    )
    unique_matches = unique_matches.merge(
        event_day_counts.loc[
            event_day_counts["same_day_event_count"].eq(1),
            ["account_id", "churn_date"],
        ],
        on=["account_id", "churn_date"],
        how="inner",
        validate="many_to_one",
    )
    unique_matches = unique_matches.drop_duplicates("churn_event_id").set_index(
        "churn_event_id"
    )

    result = result.merge(
        match_summary,
        on="churn_event_id",
        how="left",
        validate="one_to_one",
    )
    result["exact_subscription_match_count"] = (
        result["exact_subscription_match_count"].fillna(0).astype(int)
    )

    def mapping_status(row):
        if row["is_reactivation"]:
            return "reactivation_not_mapped"
        if row["same_day_event_count"] > 1:
            return "ambiguous_multiple_events_same_account_date"
        if row["exact_subscription_match_count"] == 0:
            return "no_exact_same_account_end_date_match"
        if row["exact_subscription_match_count"] > 1:
            return "ambiguous_multiple_subscription_matches"
        return "unique_same_account_end_date_candidate"

    result["mapping_status"] = result.apply(mapping_status, axis=1)
    result["candidate_subscription_id"] = result["churn_event_id"].map(
        unique_matches["subscription_id"]
    )
    result["candidate_departing_subscription_mrr"] = result["churn_event_id"].map(
        unique_matches["mrr_amount"]
    )

    result["other_subscription_rows_not_ended_by_event_date"] = pd.Series(
        pd.NA, index=result.index, dtype="Int64"
    )
    for index, row in result.loc[
        result["mapping_status"].eq("unique_same_account_end_date_candidate")
    ].iterrows():
        other_rows = subs.loc[
            subs["account_id"].eq(row["account_id"])
            & subs["start_date"].le(row["churn_date"])
            & subs["subscription_id"].ne(row["candidate_subscription_id"])
            & (
                subs["end_date"].isna()
                | subs["end_date"].gt(row["churn_date"])
            )
        ]
        result.at[index, "other_subscription_rows_not_ended_by_event_date"] = len(
            other_rows
        )

    result["candidate_account_churned_mrr"] = pd.NA
    account_match = (
        result["mapping_status"].eq("unique_same_account_end_date_candidate")
        & result["other_subscription_rows_not_ended_by_event_date"].eq(0)
    )
    result.loc[account_match, "candidate_account_churned_mrr"] = result.loc[
        account_match, "candidate_departing_subscription_mrr"
    ]
    return result.sort_values(
        ["account_id", "churn_date", "churn_event_id"]
    ).reset_index(drop=True)


def load_sources(raw_dir=RAW_DIR):
    events = pd.read_csv(raw_dir / EVENT_FILE)
    subscriptions = pd.read_csv(raw_dir / SUBSCRIPTION_FILE)
    return events, subscriptions


def main():
    events, subscriptions = load_sources()
    mapped = map_churn_events_to_subscriptions(events, subscriptions)

    print("Recorded churn-event review")
    print(f"Event rows: {len(mapped)}")
    print(f"Accounts with events: {mapped['account_id'].nunique()}")
    print(f"Candidate churn rows: {(~mapped['is_reactivation']).sum()}")
    print(f"Reactivation-flagged rows: {mapped['is_reactivation'].sum()}")
    print(
        "Sequence-supported reactivation rows: "
        f"{mapped['sequence_supported_reactivation'].sum()}"
    )
    print(
        "Possible repeated-cycle churn rows: "
        f"{mapped['possible_repeated_cycle_churn'].sum()}"
    )
    print(
        "Same-day ambiguous event rows: "
        f"{mapped['sequence_assessment'].eq('same_day_order_ambiguous').sum()}"
    )
    print("\nSubscription date-match status:")
    print(mapped["mapping_status"].value_counts().to_string())

    exact_matches = mapped.loc[
        mapped["mapping_status"].eq("unique_same_account_end_date_candidate")
    ]
    if not exact_matches.empty:
        print("\nUnique same-account/end-date candidates (not confirmed event links):")
        print(
            exact_matches[
                [
                    "churn_event_id",
                    "account_id",
                    "churn_date",
                    "candidate_subscription_id",
                    "candidate_departing_subscription_mrr",
                    "other_subscription_rows_not_ended_by_event_date",
                ]
            ].to_string(index=False)
        )
    print(
        "\nAccount-level churned MRR candidates: "
        f"{mapped['candidate_account_churned_mrr'].notna().sum()} rows"
    )


if __name__ == "__main__":
    main()
