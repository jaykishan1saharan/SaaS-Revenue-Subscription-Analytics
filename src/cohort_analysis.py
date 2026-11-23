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

    print("Cohort pipeline completed.")
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


if __name__ == "__main__":
    main()
