from pathlib import Path
import pandas as pd

# Project paths
ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = ROOT / "data/raw/ravenstack_support_tickets.csv"
ACCOUNT_FILE = ROOT / "data/raw/ravenstack_accounts.csv"
OUTPUT_FILE = ROOT / "data/interim/support_tickets_clean.csv"
LOG_FILE = ROOT / "reports/support_tickets_cleaning_log.md"

DATE_COLUMNS = ["submitted_at", "closed_at"]
NUMERIC_COLUMNS = [
    "resolution_time_hours",
    "first_response_time_minutes",
    "satisfaction_score",
]

REQUIRED_COLUMNS = [
    "ticket_id",
    "account_id",
    "submitted_at",
    "closed_at",
    "resolution_time_hours",
    "priority",
    "first_response_time_minutes",
    "satisfaction_score",
    "escalation_flag",
]


def main():
    print("Starting support ticket cleaning...")

    # Read raw files without modifying them
    df = pd.read_csv(RAW_FILE)
    accounts = pd.read_csv(ACCOUNT_FILE)

    original_rows = len(df)
    original_columns = list(df.columns)

    if original_columns != REQUIRED_COLUMNS:
        raise ValueError(
            f"Unexpected source columns or order.\n"
            f"Expected: {REQUIRED_COLUMNS}\n"
            f"Found: {original_columns}"
        )

    raw_missing = df.isna().sum()
    raw_duplicates = int(df.duplicated().sum())

    # Preserve source values while standardizing text whitespace
    text_columns = df.select_dtypes(include=["object", "string"]).columns

    whitespace_changes = {}
    for col in text_columns:
        before = df[col].copy()
        df[col] = df[col].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
        whitespace_changes[col] = int(
            (before.fillna("<NA>") != df[col].fillna("<NA>")).sum()
        )

    # Validate IDs; do not delete duplicates automatically
    if df["ticket_id"].isna().any():
        raise ValueError("Missing ticket IDs found. Cleaning stopped.")

    if df["ticket_id"].duplicated().any():
        raise ValueError("Duplicate ticket IDs found. Cleaning stopped.")

    # Standardize timestamps
    date_results = {}
    for col in DATE_COLUMNS:
        parsed = pd.to_datetime(df[col], errors="coerce")

        invalid = df[col].notna() & parsed.isna()
        if invalid.any():
            raise ValueError(
                f"{invalid.sum()} invalid timestamps found in {col}. "
                "Cleaning stopped."
            )

        if parsed.isna().any():
            raise ValueError(f"Missing timestamps found in {col}.")

        df[col] = parsed.dt.strftime("%Y-%m-%d %H:%M:%S")
        date_results[col] = "Validated and standardized"

    submitted = pd.to_datetime(df["submitted_at"])
    closed = pd.to_datetime(df["closed_at"])

    invalid_sequences = closed < submitted
    if invalid_sequences.any():
        raise ValueError(
            f"{invalid_sequences.sum()} tickets close before submission."
        )

    # Validate numeric fields without imputing missing values
    for col in NUMERIC_COLUMNS:
        original_non_null = df[col].notna()
        converted = pd.to_numeric(df[col], errors="coerce")

        invalid = original_non_null & converted.isna()
        if invalid.any():
            raise ValueError(
                f"Invalid numeric values found in {col}. Cleaning stopped."
            )

        df[col] = converted

    # Business-rule checks
    if (df["resolution_time_hours"].dropna() < 0).any():
        raise ValueError("Negative resolution times found.")

    if (df["first_response_time_minutes"].dropna() < 0).any():
        raise ValueError("Negative first-response times found.")

    invalid_scores = df["satisfaction_score"].dropna().loc[
        lambda s: ~s.between(1, 5)
    ]

    if not invalid_scores.empty:
        raise ValueError("Satisfaction scores outside the 1-5 range.")

    expected_priorities = {"low", "medium", "high", "urgent"}
    actual_priorities = set(
        df["priority"].dropna().str.lower().unique()
    )

    unexpected = actual_priorities - expected_priorities
    if unexpected:
        raise ValueError(f"Unexpected priority categories: {unexpected}")

    # Account reference validation
    account_ids = set(accounts["account_id"].dropna())
    unmatched = ~df["account_id"].isin(account_ids)

    if unmatched.any():
        raise ValueError(
            f"{unmatched.sum()} invalid account references found."
        )

    # Preserve original row count and ticket identity
    if len(df) != original_rows:
        raise AssertionError("Row count changed during cleaning.")

    if not df["ticket_id"].equals(
        pd.read_csv(RAW_FILE)["ticket_id"].reset_index(drop=True)
    ):
        raise AssertionError("Ticket IDs or row ordering changed.")

    # Save a separate interim dataset
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    # Verify the saved output
    cleaned = pd.read_csv(OUTPUT_FILE)

    if len(cleaned) != original_rows:
        raise AssertionError("Saved output row count mismatch.")

    if cleaned["ticket_id"].duplicated().any():
        raise AssertionError("Duplicate ticket IDs in saved output.")

    cleaned_missing = cleaned.isna().sum()

    # Generate cleaning log
    log = [
        "# Support Tickets Cleaning Log",
        "",
        "**Project:** SaaS Revenue & Subscription Analytics",
        "**Owner:** Lav Kumar",
        "**Stage:** Day 3 — Data Cleaning and Schema Design",
        "",
        "## 1. Source and Output",
        "",
        f"- Source: `{RAW_FILE.relative_to(ROOT)}`",
        f"- Output: `{OUTPUT_FILE.relative_to(ROOT)}`",
        f"- Original rows: {original_rows:,}",
        f"- Output rows: {len(cleaned):,}",
        f"- Original columns: {len(original_columns)}",
        f"- Removed rows: {original_rows - len(cleaned):,}",
        "",
        "## 2. Cleaning and Validation Actions",
        "",
        "- Text fields: leading/trailing whitespace standardized.",
        "- Ticket IDs: uniqueness and missing-value checks performed.",
        "- Timestamps: parsed, validated and standardized.",
        "- Numeric fields: type conversion and validation performed.",
        "- Satisfaction scores: original missing values preserved.",
        "- Priority values: checked against low, medium, high and urgent.",
        "- Account references: validated against accounts.account_id.",
        "- Raw CSV: not modified.",
        "",
        "## 3. Whitespace Standardization",
        "",
        "| Column | Values changed |",
        "|---|---:|",
    ]

    for col, count in whitespace_changes.items():
        log.append(f"| `{col}` | {count:,} |")

    log += [
        "",
        "## 4. Missing Values Before and After",
        "",
        "| Column | Before | After |",
        "|---|---:|---:|",
    ]

    for col in original_columns:
        log.append(
            f"| `{col}` | {raw_missing[col]:,} | "
            f"{cleaned_missing[col]:,} |"
        )

    log += [
        "",
        "## 5. Validation Results",
        "",
        f"- Duplicate complete rows before cleaning: {raw_duplicates:,}",
        f"- Duplicate ticket IDs after cleaning: "
        f"{cleaned['ticket_id'].duplicated().sum():,}",
        f"- Invalid timestamp sequences: {int(invalid_sequences.sum()):,}",
        f"- Invalid account references: {int(unmatched.sum()):,}",
        f"- Unexpected priorities: None",
        f"- Satisfaction scores outside 1–5: 0",
        "",
        "## 6. Data Preservation",
        "",
        "- No rows were removed.",
        "- No satisfaction scores were imputed.",
        "- No IDs were regenerated.",
        "- No business values were intentionally changed.",
        "- Original raw data was preserved.",
        "",
        "## 7. Conclusion",
        "",
        "The support ticket dataset was processed into a separate interim "
        "CSV after validation. All 2,000 records were retained. "
        "Missing satisfaction scores were preserved. "
        "See the source quality audit for the original findings.",
        "",
    ]

    LOG_FILE.write_text("\n".join(log), encoding="utf-8")

    print("\n========== CLEANING COMPLETE ==========")
    print("Original records:", original_rows)
    print("Output records:", len(cleaned))
    print("Removed records:", original_rows - len(cleaned))
    print("Missing satisfaction scores:", cleaned_missing["satisfaction_score"])
    print("Duplicate ticket IDs:", cleaned["ticket_id"].duplicated().sum())
    print("Unmatched account references:", unmatched.sum())
    print("Cleaned CSV:", OUTPUT_FILE)
    print("Cleaning log:", LOG_FILE)


if __name__ == "__main__":
    main()
