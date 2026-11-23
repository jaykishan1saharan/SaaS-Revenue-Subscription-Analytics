"""Conservative churn-event, account, reactivation and churned-MRR analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = ROOT_DIR / "data/raw/ravenstack_churn_events.csv"
DEFAULT_SUBSCRIPTIONS = ROOT_DIR / "data/raw/ravenstack_subscriptions.csv"
DEFAULT_OUTPUT = ROOT_DIR / "data/processed/churn"

EVENT_COLUMNS = {
    "churn_event_id", "account_id", "churn_date", "is_reactivation"
}
SUBSCRIPTION_COLUMNS = {
    "subscription_id", "account_id", "start_date", "end_date", "mrr_amount"
}


def require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}")


def parse_dates(frame: pd.DataFrame, column: str, nullable: bool) -> pd.Series:
    raw = frame[column]
    parsed = pd.to_datetime(raw, errors="coerce").dt.normalize()
    invalid = raw.notna() & parsed.isna()
    if invalid.any():
        raise ValueError(f"{column} contains invalid dates")
    if not nullable and parsed.isna().any():
        raise ValueError(f"{column} contains missing dates")
    return parsed


def parse_boolean(values: pd.Series, column: str) -> pd.Series:
    if pd.api.types.is_bool_dtype(values.dtype):
        return values.astype(bool)
    parsed = values.astype(str).str.strip().str.lower().map({
        "true": True, "false": False, "1": True, "0": False,
        "yes": True, "no": False,
    })
    if values.isna().any() or parsed.isna().any():
        raise ValueError(f"{column} contains missing or unsupported boolean values")
    return parsed.astype(bool)


def load_sources(
    events_path: str | Path = DEFAULT_EVENTS,
    subscriptions_path: str | Path = DEFAULT_SUBSCRIPTIONS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    return pd.read_csv(events_path), pd.read_csv(subscriptions_path)


def prepare_events(events: pd.DataFrame) -> pd.DataFrame:
    require_columns(events, EVENT_COLUMNS, "churn_events")
    prepared = events.copy()
    if prepared.churn_event_id.isna().any() or prepared.churn_event_id.duplicated().any():
        raise ValueError("churn_event_id must be non-null and unique")
    if prepared.account_id.isna().any():
        raise ValueError("churn_events contains missing account_id values")
    prepared["churn_date"] = parse_dates(prepared, "churn_date", nullable=False)
    prepared["is_reactivation"] = parse_boolean(
        prepared["is_reactivation"], "is_reactivation"
    )
    return prepared


def prepare_subscriptions(subscriptions: pd.DataFrame) -> pd.DataFrame:
    require_columns(subscriptions, SUBSCRIPTION_COLUMNS, "subscriptions")
    prepared = subscriptions.copy()
    if prepared.subscription_id.isna().any() or prepared.subscription_id.duplicated().any():
        raise ValueError("subscription_id must be non-null and unique")
    if prepared.account_id.isna().any():
        raise ValueError("subscriptions contains missing account_id values")
    prepared["start_date"] = parse_dates(prepared, "start_date", nullable=False)
    prepared["end_date"] = parse_dates(prepared, "end_date", nullable=True)
    prepared["mrr_amount"] = pd.to_numeric(prepared["mrr_amount"], errors="coerce")
    if prepared.mrr_amount.isna().any():
        raise ValueError("mrr_amount contains missing or non-numeric values")
    if (prepared.mrr_amount < 0).any():
        raise ValueError("mrr_amount contains negative values")
    reversed_dates = prepared.end_date.notna() & (
        prepared.end_date < prepared.start_date
    )
    if reversed_dates.any():
        raise ValueError("subscription end_date precedes start_date")
    return prepared


def classify_event_sequences(events: pd.DataFrame) -> pd.DataFrame:
    events = prepare_events(events)
    daily = (
        events.groupby(["account_id", "churn_date"], as_index=False)
        .agg(
            same_day_event_count=("churn_event_id", "size"),
            has_candidate_churn=("is_reactivation", lambda values: (~values).any()),
            has_reactivation=("is_reactivation", "any"),
        )
        .sort_values(["account_id", "churn_date"])
    )
    daily["previous_event_count"] = daily.groupby("account_id")[
        "same_day_event_count"
    ].shift()
    daily["previous_has_candidate_churn"] = daily.groupby("account_id")[
        "has_candidate_churn"
    ].shift()
    daily["previous_has_reactivation"] = daily.groupby("account_id")[
        "has_reactivation"
    ].shift()

    unambiguous_candidate = (
        daily["has_candidate_churn"] & daily["same_day_event_count"].eq(1)
    )
    prior_candidate = (
        unambiguous_candidate.groupby(daily["account_id"]).cumsum()
        - unambiguous_candidate.astype(int)
    )
    daily["prior_candidate_churn_exists"] = prior_candidate.gt(0)

    result = events.merge(
        daily, on=["account_id", "churn_date"], how="left", validate="many_to_one"
    )

    def assess(row: pd.Series) -> str:
        if row.same_day_event_count > 1:
            return "same_day_order_ambiguous"
        if pd.isna(row.previous_event_count):
            return "reactivation_without_prior_event" if row.is_reactivation else "initial_candidate_churn"
        if row.previous_event_count > 1:
            return "previous_same_day_order_ambiguous"
        if row.is_reactivation:
            if row.previous_has_candidate_churn:
                return "reactivation_after_candidate_churn"
            return "reactivation_after_reactivation"
        if row.previous_has_reactivation:
            if row.prior_candidate_churn_exists:
                return "possible_repeated_churn_reactivation_cycle"
            return "candidate_churn_after_reactivation"
        return "repeated_candidate_churn_without_reactivation"

    result["sequence_assessment"] = result.apply(assess, axis=1)
    result["sequence_supported_reactivation"] = result.sequence_assessment.eq(
        "reactivation_after_candidate_churn"
    )
    return result.sort_values(
        ["account_id", "churn_date", "churn_event_id"]
    ).reset_index(drop=True)


def map_churn_events(
    churn_events: pd.DataFrame, subscriptions: pd.DataFrame
) -> pd.DataFrame:
    events = prepare_events(churn_events)
    subs = prepare_subscriptions(subscriptions)
    result = classify_event_sequences(events)

    event_day_counts = events.groupby(["account_id", "churn_date"]).agg(
        same_day_event_count=("churn_event_id", "size")
    ).reset_index()

    candidates = events.loc[~events.is_reactivation].merge(
        subs[["subscription_id", "account_id", "start_date", "end_date", "mrr_amount"]],
        left_on=["account_id", "churn_date"],
        right_on=["account_id", "end_date"],
        how="left",
        validate="many_to_many",
    )
    candidates = candidates.loc[
        candidates.subscription_id.isna()
        | candidates.start_date.le(candidates.churn_date)
    ]
    candidates = candidates.rename(columns={
        "mrr_amount": "candidate_subscription_mrr",
    })

    match_counts = candidates.groupby("churn_event_id").agg(
        exact_subscription_match_count=("subscription_id", "nunique")
    ).reset_index()
    unique_matches = candidates.loc[
        candidates.subscription_id.notna()
    ].merge(
        match_counts.loc[
            match_counts.exact_subscription_match_count.eq(1),
            ["churn_event_id"],
        ],
        on="churn_event_id",
        how="inner",
        validate="many_to_one",
    ).merge(
        event_day_counts.loc[
            event_day_counts.same_day_event_count.eq(1),
            ["account_id", "churn_date"],
        ],
        on=["account_id", "churn_date"],
        how="inner",
        validate="many_to_one",
    ).drop_duplicates("churn_event_id").set_index("churn_event_id")

    result = result.merge(
        match_counts, on="churn_event_id", how="left", validate="one_to_one"
    )
    result["exact_subscription_match_count"] = result[
        "exact_subscription_match_count"
    ].fillna(0).astype(int)

    def status(row: pd.Series) -> str:
        if row.is_reactivation:
            return "reactivation_not_mapped"
        if row.same_day_event_count > 1:
            return "ambiguous_multiple_events_same_account_date"
        if row.exact_subscription_match_count == 0:
            return "no_exact_same_account_end_date_match"
        if row.exact_subscription_match_count > 1:
            return "ambiguous_multiple_subscription_matches"
        return "unique_same_account_end_date_candidate"

    result["mapping_status"] = result.apply(status, axis=1)
    result["candidate_subscription_id"] = result.churn_event_id.map(
        unique_matches.subscription_id
    )
    result["candidate_subscription_mrr"] = result.churn_event_id.map(
        unique_matches.candidate_subscription_mrr
    )

    other_counts = []
    for index, row in result.iterrows():
        if row.mapping_status != "unique_same_account_end_date_candidate":
            other_counts.append(pd.NA)
            continue
        candidate_id = row.candidate_subscription_id
        other = subs.loc[
            subs.account_id.eq(row.account_id)
            & subs.start_date.le(row.churn_date)
            & subs.subscription_id.ne(candidate_id)
            & (subs.end_date.isna() | subs.end_date.gt(row.churn_date))
        ]
        other_counts.append(len(other))
    result["other_not_ended_subscription_count"] = pd.array(other_counts, dtype="Int64")
    eligible = (
        result.mapping_status.eq("unique_same_account_end_date_candidate")
        & result.other_not_ended_subscription_count.eq(0)
    )
    result["candidate_account_churned_mrr"] = pd.NA
    result.loc[eligible, "candidate_account_churned_mrr"] = result.loc[
        eligible, "candidate_subscription_mrr"
    ].astype(float)
    return result.sort_values(
        ["account_id", "churn_date", "churn_event_id"]
    ).reset_index(drop=True)


def monthly_churn_summary(mapped: pd.DataFrame) -> pd.DataFrame:
    result = mapped.copy()
    result["churn_month"] = result.churn_date.dt.to_period("M").dt.to_timestamp()
    candidate = result.loc[~result.is_reactivation].copy()
    event_summary = candidate.groupby("churn_month").agg(
        candidate_churn_event_rows=("churn_event_id", "size"),
        unique_accounts_with_churn_events=("account_id", "nunique"),
    ).reset_index()

    account_month = candidate.groupby(["churn_month", "account_id"]).agg(
        candidate_event_count=("churn_event_id", "size"),
        churned_mrr=("candidate_account_churned_mrr", "sum"),
        eligible_mrr_count=("candidate_account_churned_mrr", lambda values: values.notna().sum()),
    ).reset_index()
    account_summary = account_month.groupby("churn_month").agg(
        unique_candidate_churn_accounts=("account_id", "nunique"),
        repeat_event_accounts=("candidate_event_count", lambda values: values.gt(1).sum()),
        matched_churned_mrr_accounts=("eligible_mrr_count", lambda values: values.gt(0).sum()),
    ).reset_index()
    monthly_mrr = account_month.loc[
        account_month.candidate_event_count.eq(1)
        & account_month.eligible_mrr_count.eq(1)
    ].groupby("churn_month").agg(
        unique_churned_accounts=("account_id", "nunique"),
        churned_mrr=("churned_mrr", "sum"),
    ).reset_index()

    return (
        event_summary.merge(account_summary, on="churn_month", how="left")
        .merge(monthly_mrr, on="churn_month", how="left")
        .infer_objects(copy=False)
        .fillna({"unique_churned_accounts": 0, "churned_mrr": 0.0})
    )


def run_pipeline(
    events_path: str | Path = DEFAULT_EVENTS,
    subscriptions_path: str | Path = DEFAULT_SUBSCRIPTIONS,
    output_dir: str | Path = DEFAULT_OUTPUT,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    events, subscriptions = load_sources(events_path, subscriptions_path)
    mapped = map_churn_events(events, subscriptions)
    monthly = monthly_churn_summary(mapped)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    event_file = output_dir / "churn_event_analysis.csv"
    monthly_file = output_dir / "monthly_churn_summary.csv"
    mapped.to_csv(event_file, index=False, date_format="%Y-%m-%d")
    monthly.to_csv(monthly_file, index=False, date_format="%Y-%m-%d")

    print("Churn analysis completed")
    print(f"Recorded event rows: {len(mapped)}")
    print(f"Candidate churn event rows: {(~mapped.is_reactivation).sum()}")
    print(f"Reactivation event rows: {mapped.is_reactivation.sum()}")
    print(f"Sequence-supported reactivations: {mapped.sequence_supported_reactivation.sum()}")
    print(f"Unique accounts with churn events: "
          f"{mapped.loc[~mapped.is_reactivation, 'account_id'].nunique()}")
    print(f"Monthly churned MRR: {monthly.churned_mrr.sum():.2f}")
    print(f"Saved: {event_file}")
    print(f"Saved: {monthly_file}")
    return mapped, monthly


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--subscriptions", type=Path, default=DEFAULT_SUBSCRIPTIONS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run_pipeline(args.events, args.subscriptions, args.output_dir)


if __name__ == "__main__":
    main()
