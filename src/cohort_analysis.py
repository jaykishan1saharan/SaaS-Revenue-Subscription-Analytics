"""
Week 3 Day 11: Customer cohort creation and customer-month activity.

Cohort definition:
- Qualifying paid subscription = is_trial is False and mrr_amount > 0.
- Account cohort month = month of its earliest qualifying paid subscription.
- One cohort assignment per account, even when it has multiple subscriptions.

Activity definition:
- Paid subscriptions are evaluated at calendar month-end.
- Provisional Week 2 predicate:
    start_date <= month_end
    AND (end_date IS NULL OR end_date >= month_end)
- Active paid subscription also requires is_trial=False and mrr_amount > 0.
- Activity output is one row per account_id x activity_month.
- Subscription MRR is summed after subscription eligibility is evaluated;
  distinct customer counts must use account_id, not subscription_id.

Run from the repository root:
    python src/cohort_analysis.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_ACCOUNTS = ROOT_DIR / "data/raw/ravenstack_accounts.csv"
DEFAULT_SUBSCRIPTIONS = ROOT_DIR / "data/raw/ravenstack_subscriptions.csv"
DEFAULT_OUTPUT = ROOT_DIR / "data/processed/week3"

ACCOUNT_COLUMNS = {"account_id"}
SUBSCRIPTION_COLUMNS = {
    "subscription_id", "account_id", "start_date", "end_date",
    "mrr_amount", "is_trial"
}


def require_columns(df: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}")


def parse_dates(df: pd.DataFrame, column: str, nullable: bool) -> pd.Series:
    raw = df[column]
    parsed = pd.to_datetime(raw, errors="coerce").dt.normalize()
    invalid = raw.notna() & parsed.isna()
    if invalid.any():
        examples = raw.loc[invalid].astype(str).head(5).tolist()
        raise ValueError(f"{column} has invalid date values, examples: {examples}")
    if not nullable and parsed.isna().any():
        raise ValueError(f"{column} contains missing dates.")
    return parsed


def parse_boolean(series: pd.Series, column: str) -> pd.Series:
    if series.isna().any():
        raise ValueError(f"{column} contains missing values.")
    if pd.api.types.is_bool_dtype(series.dtype):
        return series.astype(bool)
    mapping = {
        "true": True, "false": False, "1": True, "0": False,
        "yes": True, "no": False
    }
    parsed = series.astype(str).str.strip().str.lower().map(mapping)
    if parsed.isna().any():
        raise ValueError(f"{column} contains unsupported boolean values.")
    return parsed.astype(bool)


def load_source_data(
    accounts_path: str | Path = DEFAULT_ACCOUNTS,
    subscriptions_path: str | Path = DEFAULT_SUBSCRIPTIONS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load source CSVs; raw files are never modified."""
    return pd.read_csv(accounts_path), pd.read_csv(subscriptions_path)


def validate_source_data(
    accounts: pd.DataFrame, subscriptions: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Validate source schema, keys, dates, MRR and account references."""
    require_columns(accounts, ACCOUNT_COLUMNS, "accounts")
    require_columns(subscriptions, SUBSCRIPTION_COLUMNS, "subscriptions")

    accounts = accounts.copy()
    subscriptions = subscriptions.copy()

    if accounts.account_id.isna().any() or accounts.account_id.duplicated().any():
        raise ValueError("accounts.account_id must be non-null and unique.")
    if subscriptions.subscription_id.isna().any():
        raise ValueError("subscriptions.subscription_id contains null values.")
    if subscriptions.subscription_id.duplicated().any():
        raise ValueError("subscriptions.subscription_id must be unique.")
    if subscriptions.account_id.isna().any():
        raise ValueError("subscriptions.account_id contains null values.")

    subscriptions["start_date"] = parse_dates(
        subscriptions, "start_date", nullable=False
    )
    subscriptions["end_date"] = parse_dates(
        subscriptions, "end_date", nullable=True
    )
    subscriptions["mrr_amount"] = pd.to_numeric(
        subscriptions["mrr_amount"], errors="coerce"
    )
    if subscriptions.mrr_amount.isna().any():
        raise ValueError("mrr_amount contains missing or non-numeric values.")
    if (subscriptions.mrr_amount < 0).any():
        raise ValueError("mrr_amount contains negative values.")

    subscriptions["is_trial"] = parse_boolean(
        subscriptions["is_trial"], "is_trial"
    )

    reversed_dates = (
        subscriptions.end_date.notna()
        & (subscriptions.end_date < subscriptions.start_date)
    )
    if reversed_dates.any():
        ids = subscriptions.loc[reversed_dates, "subscription_id"].head(5).tolist()
        raise ValueError(f"end_date precedes start_date for subscriptions: {ids}")

    unknown_accounts = ~subscriptions.account_id.isin(accounts.account_id)
    if unknown_accounts.any():
        ids = subscriptions.loc[unknown_accounts, "subscription_id"].head(5).tolist()
        raise ValueError(f"Unknown account_id references in subscriptions: {ids}")

    return accounts, subscriptions


def create_cohort_assignments(subscriptions: pd.DataFrame) -> pd.DataFrame:
    """Assign each paid account to its earliest qualifying paid start month."""
    paid = subscriptions.loc[
        (~subscriptions.is_trial) & (subscriptions.mrr_amount > 0)
    ].copy()

    columns = [
        "account_id", "first_paid_subscription_id",
        "first_paid_start_date", "cohort_month", "cohort_size"
    ]
    if paid.empty:
        return pd.DataFrame(columns=columns)

    paid = paid.sort_values(
        ["account_id", "start_date", "subscription_id"], kind="stable"
    )
    first_paid = paid.drop_duplicates("account_id", keep="first").copy()

    cohorts = first_paid[
        ["account_id", "subscription_id", "start_date"]
    ].rename(columns={
        "subscription_id": "first_paid_subscription_id",
        "start_date": "first_paid_start_date"
    })
    cohorts["cohort_month"] = (
        cohorts.first_paid_start_date.dt.to_period("M").dt.to_timestamp()
    )
    sizes = cohorts.groupby("cohort_month").account_id.nunique().rename("cohort_size")
    cohorts = cohorts.merge(sizes, on="cohort_month", validate="many_to_one")
    cohorts = cohorts[columns].sort_values(
        ["cohort_month", "account_id"]
    ).reset_index(drop=True)

    if cohorts.account_id.duplicated().any():
        raise AssertionError("More than one cohort assignment exists for an account.")
    return cohorts


def create_customer_month_activity(
    subscriptions: pd.DataFrame, cohorts: pd.DataFrame
) -> pd.DataFrame:
    """
    Emit active paid account-month rows only.
    Absence of a row for a month means no qualifying paid subscription was
    active at that month's end; downstream retention code can treat it as
    inactive, while months beyond observation must be treated as unavailable.
    """
    columns = [
        "account_id", "cohort_month", "activity_month", "cohort_age_month",
        "active_customer", "active_paid_subscription_count", "customer_mrr"
    ]
    if cohorts.empty:
        return pd.DataFrame(columns=columns)

    paid = subscriptions.loc[
        (~subscriptions.is_trial) & (subscriptions.mrr_amount > 0)
    ].merge(
        cohorts[["account_id", "cohort_month"]],
        on="account_id", how="inner", validate="many_to_one"
    )

    observed_dates = pd.concat(
        [subscriptions.start_date, subscriptions.end_date], ignore_index=True
    ).dropna()
    if observed_dates.empty:
        return pd.DataFrame(columns=columns)

    first_month = cohorts.cohort_month.min()
    last_month = observed_dates.max().to_period("M").to_timestamp()
    month_starts = pd.date_range(first_month, last_month, freq="MS")

    monthly_parts = []
    for month_start in month_starts:
        month_end = month_start + pd.offsets.MonthEnd(0)
        active_subs = paid.loc[
            (paid.start_date <= month_end)
            & (paid.end_date.isna() | (paid.end_date >= month_end))
        ]

        if active_subs.empty:
            continue

        # Aggregate at account-month after applying subscription-level rule.
        account_month = active_subs.groupby(
            ["account_id", "cohort_month"], as_index=False
        ).agg(
            active_paid_subscription_count=("subscription_id", "nunique"),
            customer_mrr=("mrr_amount", "sum")
        )
        account_month["activity_month"] = month_start
        account_month["cohort_age_month"] = (
            (account_month.activity_month.dt.year - account_month.cohort_month.dt.year) * 12
            + account_month.activity_month.dt.month
            - account_month.cohort_month.dt.month
        )
        account_month["active_customer"] = True
        monthly_parts.append(account_month[columns])

    if not monthly_parts:
        return pd.DataFrame(columns=columns)

    activity = pd.concat(monthly_parts, ignore_index=True)
    activity = activity.sort_values(
        ["cohort_month", "activity_month", "account_id"]
    ).reset_index(drop=True)

    if activity.duplicated(["account_id", "activity_month"]).any():
        raise AssertionError("Duplicate account_id x activity_month records found.")
    if (activity.active_paid_subscription_count < 1).any():
        raise AssertionError("Active customer row has no eligible paid subscription.")
    if (activity.cohort_age_month < 0).any():
        raise AssertionError("Activity exists before the assigned cohort month.")
    return activity


def run_pipeline(
    accounts_path: str | Path = DEFAULT_ACCOUNTS,
    subscriptions_path: str | Path = DEFAULT_SUBSCRIPTIONS,
    output_dir: str | Path = DEFAULT_OUTPUT,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    accounts, subscriptions = load_source_data(accounts_path, subscriptions_path)
    accounts, subscriptions = validate_source_data(accounts, subscriptions)

    cohorts = create_cohort_assignments(subscriptions)
    activity = create_customer_month_activity(subscriptions, cohorts)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cohort_file = output_dir / "customer_cohort_assignments.csv"
    activity_file = output_dir / "customer_month_activity.csv"

    cohorts.to_csv(cohort_file, index=False, date_format="%Y-%m-%d")
    activity.to_csv(activity_file, index=False, date_format="%Y-%m-%d")
    retention_matrix, retention_by_plan = save_retention_outputs(
        cohorts, subscriptions, activity, output_dir
    )

    print("Cohort and retention pipeline completed.")
    print(f"Eligible cohort accounts: {cohorts.account_id.nunique()}")
    print(f"Cohort months: {cohorts.cohort_month.nunique()}")
    print(f"Customer-month rows: {len(activity)}")
    print(f"Unique active accounts in activity: {activity.account_id.nunique()}")
    print(f"Saved: {cohort_file}")
    print(f"Saved: {activity_file}")

    return cohorts, activity


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accounts", type=Path, default=DEFAULT_ACCOUNTS)
    parser.add_argument("--subscriptions", type=Path, default=DEFAULT_SUBSCRIPTIONS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run_pipeline(args.accounts, args.subscriptions, args.output_dir)


# ---------------------------------------------------------------------------
# Week 3 Day 12: reusable cohort retention calculations
# ---------------------------------------------------------------------------

def create_retention_matrix(
    cohorts: pd.DataFrame,
    customer_month_activity: pd.DataFrame,
    last_observed_month: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Return one row per cohort and one retention_pct column per cohort age.

    A missing cohort-age observation is NULL (NaN), not zero. An observed
    month with no active customers is 0%. Customer counts use account_id.
    """
    required_cohorts = {"account_id", "cohort_month"}
    required_activity = {"account_id", "cohort_month", "activity_month", "active_customer"}
    require_columns(cohorts, required_cohorts, "cohorts")
    require_columns(customer_month_activity, required_activity, "customer_month_activity")
    c = cohorts.copy()
    a = customer_month_activity.copy()
    c["cohort_month"] = pd.to_datetime(c["cohort_month"]).dt.to_period("M").dt.to_timestamp()
    a["cohort_month"] = pd.to_datetime(a["cohort_month"]).dt.to_period("M").dt.to_timestamp()
    a["activity_month"] = pd.to_datetime(a["activity_month"]).dt.to_period("M").dt.to_timestamp()
    if c.account_id.duplicated().any():
        raise ValueError("cohorts must contain one row per account_id")
    if a.duplicated(["account_id", "activity_month"]).any():
        raise ValueError("activity must be unique at account_id x activity_month")
    if last_observed_month is None:
        last_observed_month = a.activity_month.max()
    last_observed_month = pd.Timestamp(last_observed_month).to_period("M").to_timestamp()
    sizes = c.groupby("cohort_month").account_id.nunique()
    active = a.loc[a.active_customer.astype(bool)].groupby(
        ["cohort_month", "activity_month"]
    ).account_id.nunique()
    max_age = max((last_observed_month.year - c.cohort_month.min().year) * 12
                  + last_observed_month.month - c.cohort_month.min().month, 0)
    rows = []
    for cohort_month, size in sizes.items():
        row = {"cohort_month": cohort_month, "cohort_size": int(size)}
        for age in range(max_age + 1):
            target = cohort_month + pd.DateOffset(months=age)
            if target > last_observed_month:
                row[f"month_{age}"] = np.nan
            else:
                count = int(active.get((cohort_month, target), 0))
                row[f"month_{age}"] = round(count / size * 100, 4) if size else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values("cohort_month").reset_index(drop=True)


def create_retention_by_plan(
    cohorts: pd.DataFrame,
    subscriptions: pd.DataFrame,
    customer_month_activity: pd.DataFrame,
    last_observed_month: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Retention by first qualifying paid plan; plan changes do not reassign cohort."""
    require_columns(subscriptions, {"account_id", "subscription_id", "start_date", "plan_tier", "mrr_amount", "is_trial"}, "subscriptions")
    first_paid = subscriptions.loc[(~subscriptions.is_trial.astype(bool)) & (pd.to_numeric(subscriptions.mrr_amount) > 0)].copy()
    first_paid["start_date"] = pd.to_datetime(first_paid.start_date)
    first_paid = first_paid.sort_values(["account_id", "start_date", "subscription_id"], kind="stable").drop_duplicates("account_id")
    plan = first_paid[["account_id", "plan_tier"]].rename(columns={"plan_tier": "cohort_plan_tier"})
    c = cohorts.merge(plan, on="account_id", how="left", validate="one_to_one")
    a = customer_month_activity.merge(c[["account_id", "cohort_plan_tier"]], on="account_id", how="left", validate="many_to_one")
    if last_observed_month is None:
        last_observed_month = pd.to_datetime(a.activity_month).max()
    last_observed_month = pd.Timestamp(last_observed_month).to_period("M").to_timestamp()
    c["cohort_month"] = pd.to_datetime(c.cohort_month).dt.to_period("M").dt.to_timestamp()
    a["cohort_month"] = pd.to_datetime(a.cohort_month).dt.to_period("M").dt.to_timestamp()
    a["activity_month"] = pd.to_datetime(a.activity_month).dt.to_period("M").dt.to_timestamp()
    sizes = c.groupby(["cohort_month", "cohort_plan_tier"]).account_id.nunique().rename("cohort_size")
    active = a.loc[a.active_customer.astype(bool)].groupby(
        ["cohort_month", "cohort_plan_tier", "activity_month"]
    ).account_id.nunique()
    max_age = max((last_observed_month.year - c.cohort_month.min().year) * 12
                  + last_observed_month.month - c.cohort_month.min().month, 0)
    rows = []
    for (cohort_month, plan_tier), size in sizes.items():
        row = {"cohort_month": cohort_month, "cohort_plan_tier": plan_tier, "cohort_size": int(size)}
        for age in range(max_age + 1):
            target = cohort_month + pd.DateOffset(months=age)
            if target > last_observed_month:
                row[f"month_{age}"] = np.nan
            else:
                count = int(active.get((cohort_month, plan_tier, target), 0))
                row[f"month_{age}"] = round(count / size * 100, 4) if size else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["cohort_month", "cohort_plan_tier"]).reset_index(drop=True)


def save_retention_outputs(cohorts, subscriptions, customer_month_activity, output_dir=DEFAULT_OUTPUT):
    """Save Day 12 overall and first-paid-plan cohort retention CSVs."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    last_month = pd.to_datetime(customer_month_activity.activity_month).max()
    matrix = create_retention_matrix(cohorts, customer_month_activity, last_month)
    by_plan = create_retention_by_plan(cohorts, subscriptions, customer_month_activity, last_month)
    matrix.to_csv(output_dir / "cohort_retention_matrix.csv", index=False, date_format="%Y-%m-%d")
    by_plan.to_csv(output_dir / "cohort_retention_by_plan.csv", index=False, date_format="%Y-%m-%d")
    return matrix, by_plan


if __name__ == "__main__":
    main()
