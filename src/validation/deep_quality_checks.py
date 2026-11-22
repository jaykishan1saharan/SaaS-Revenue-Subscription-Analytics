from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "reports" / "day2_audit"

OUT.mkdir(parents=True, exist_ok=True)


def load(name):
    df = pd.read_csv(RAW / name, encoding="utf-8-sig")
    # Treat whitespace-only strings as missing for these checks
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].map(
            lambda x: x.strip() if isinstance(x, str) else x
        )
        df[col] = df[col].replace("", pd.NA)
    return df


def save_check(name, rows):
    result = pd.DataFrame(rows)
    result.to_csv(OUT / name, index=False)
    print(f"Saved: {name}")
    return result


accounts = load("ravenstack_accounts.csv")
churn = load("ravenstack_churn_events.csv")
usage = load("ravenstack_feature_usage.csv")
subs = load("ravenstack_subscriptions.csv")
tickets = load("ravenstack_support_tickets.csv")

print("\nRAVENSTACK — DEEP DATA QUALITY CHECKS")
print("=" * 55)

# 1. Candidate ID duplicate checks
id_checks = []

for df, dataset, column in [
    (accounts, "accounts", "account_id"),
    (churn, "churn_events", "churn_event_id"),
    (usage, "feature_usage", "usage_id"),
    (subs, "subscriptions", "subscription_id"),
    (tickets, "support_tickets", "ticket_id"),
]:
    duplicate_mask = df[column].duplicated(keep=False)
    duplicate_rows = df.loc[duplicate_mask].copy()

    id_checks.append({
        "dataset": dataset,
        "id_column": column,
        "total_rows": len(df),
        "null_ids": int(df[column].isna().sum()),
        "unique_ids": int(df[column].nunique()),
        "rows_with_repeated_ids": int(duplicate_mask.sum()),
    })

    if not duplicate_rows.empty:
        duplicate_rows.to_csv(
            OUT / f"{dataset}_duplicate_ids.csv", index=False
        )

save_check("candidate_id_validation.csv", id_checks)

# 2. Foreign-key / reference checks
account_ids = set(accounts["account_id"].dropna())
subscription_ids = set(subs["subscription_id"].dropna())

reference_checks = []

for dataset, df, column, valid_ids in [
    ("subscriptions", subs, "account_id", account_ids),
    ("churn_events", churn, "account_id", account_ids),
    ("support_tickets", tickets, "account_id", account_ids),
    ("feature_usage", usage, "subscription_id", subscription_ids),
]:
    values = df[column]
    non_null = values.dropna()
    orphan_mask = ~non_null.isin(valid_ids)
    orphan_values = non_null[orphan_mask]

    reference_checks.append({
        "dataset": dataset,
        "reference_column": column,
        "non_null_references": len(non_null),
        "unmatched_references": len(orphan_values),
        "unique_unmatched_values": orphan_values.nunique(),
    })

    if not orphan_values.empty:
        df.loc[values.isin(set(orphan_values))].to_csv(
            OUT / f"{dataset}_unmatched_references.csv",
            index=False
        )

save_check("reference_integrity_checks.csv", reference_checks)

# 3. Subscription end-date investigation
subs["start_date_parsed"] = pd.to_datetime(
    subs["start_date"], errors="coerce"
)
subs["end_date_parsed"] = pd.to_datetime(
    subs["end_date"], errors="coerce"
)

end_date_summary = (
    subs.groupby(["churn_flag", "is_trial"], dropna=False)
    .agg(
        total_subscriptions=("subscription_id", "count"),
        missing_end_dates=("end_date", lambda x: x.isna().sum()),
    )
    .reset_index()
)

save_check("subscription_end_date_by_status.csv", end_date_summary)

invalid_subscription_dates = subs[
    subs["start_date_parsed"].isna()
    | (
        subs["end_date_parsed"].notna()
        & (subs["end_date_parsed"] < subs["start_date_parsed"])
    )
]

invalid_subscription_dates.to_csv(
    OUT / "invalid_subscription_dates.csv", index=False
)

print(
    "Subscriptions with invalid/missing start dates or end-before-start:",
    len(invalid_subscription_dates)
)

# 4. MRR and ARR consistency
subs["expected_arr"] = subs["mrr_amount"] * 12
subs["arr_difference"] = subs["arr_amount"] - subs["expected_arr"]

revenue_mismatches = subs[
    subs["arr_difference"].abs() > 0.01
]

revenue_mismatches.to_csv(
    OUT / "mrr_arr_mismatches.csv", index=False
)

print("MRR/ARR mismatches:", len(revenue_mismatches))

# 5. Support ticket timestamp validation
tickets["submitted_parsed"] = pd.to_datetime(
    tickets["submitted_at"], errors="coerce"
)
tickets["closed_parsed"] = pd.to_datetime(
    tickets["closed_at"], errors="coerce"
)

invalid_ticket_dates = tickets[
    tickets["submitted_parsed"].isna()
    | (
        tickets["closed_parsed"].notna()
        & (tickets["closed_parsed"] < tickets["submitted_parsed"])
    )
]

invalid_ticket_dates.to_csv(
    OUT / "invalid_ticket_dates.csv", index=False
)

print("Invalid ticket timestamp records:", len(invalid_ticket_dates))

# 6. Churn event date validation
churn["churn_date_parsed"] = pd.to_datetime(
    churn["churn_date"], errors="coerce"
)

invalid_churn_dates = churn[
    churn["churn_date_parsed"].isna()
]

invalid_churn_dates.to_csv(
    OUT / "invalid_churn_dates.csv", index=False
)

print("Invalid churn dates:", len(invalid_churn_dates))

print("\nDEEP VALIDATION COMPLETED")
print("Check the generated CSV reports in:", OUT)
print("No raw data was modified.")
