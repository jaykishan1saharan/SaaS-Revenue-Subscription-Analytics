from pathlib import Path
import pandas as pd

# Project directories
ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
REPORT_DIR = ROOT_DIR / "reports" / "day2_audit"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Actual RavenStack datasets
DATASETS = [
    "ravenstack_accounts.csv",
    "ravenstack_churn_events.csv",
    "ravenstack_feature_usage.csv",
    "ravenstack_subscriptions.csv",
    "ravenstack_support_tickets.csv",
]


def load_dataset(file_path):
    """Load CSV while supporting common encodings."""
    try:
        return pd.read_csv(file_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding="latin-1")


def profile_dataset(file_name):
    file_path = RAW_DIR / file_name

    if not file_path.exists():
        print(f"[MISSING] {file_name}")
        return None, None

    df = load_dataset(file_path)

    row_count, column_count = df.shape

    # General dataset-level summary
    dataset_summary = {
        "dataset": file_name,
        "rows": row_count,
        "columns": column_count,
        "duplicate_rows": int(df.duplicated().sum()),
        "total_missing_cells": int(df.isna().sum().sum()),
    }

    column_profiles = []

    for column in df.columns:
        series = df[column]

        missing_count = int(series.isna().sum())
        non_null = series.dropna()

        profile = {
            "dataset": file_name,
            "column": column,
            "data_type": str(series.dtype),
            "total_rows": row_count,
            "missing_count": missing_count,
            "missing_percentage": round(
                (missing_count / row_count) * 100, 2
            ) if row_count else 0,
            "unique_values": int(series.nunique(dropna=True)),
            "duplicate_values": int(
                non_null.duplicated().sum()
            ),
        }

        # Candidate identifier check:
        # This is only a screening hint, not proof of a primary key.
        if "id" in column.lower():
            profile["candidate_id_nulls"] = missing_count
            profile["candidate_id_duplicate_values"] = int(
                non_null.duplicated().sum()
            )
        else:
            profile["candidate_id_nulls"] = None
            profile["candidate_id_duplicate_values"] = None

        # Date/time screening based on column name
        if any(word in column.lower() for word in
               ["date", "time", "timestamp", "created", "updated"]):
            parsed = pd.to_datetime(series, errors="coerce")
            non_blank_count = int(series.notna().sum())

            profile["date_parse_failures"] = int(
                (parsed.isna() & series.notna()).sum()
            )
            profile["date_values_tested"] = non_blank_count
        else:
            profile["date_parse_failures"] = None
            profile["date_values_tested"] = None

        # Numeric range screening
        if pd.api.types.is_numeric_dtype(series):
            profile["minimum_value"] = series.min()
            profile["maximum_value"] = series.max()
        else:
            profile["minimum_value"] = None
            profile["maximum_value"] = None

        column_profiles.append(profile)

    print(f"[DONE] {file_name}: {row_count} rows, {column_count} columns")

    return dataset_summary, column_profiles


def main():
    all_summaries = []
    all_column_profiles = []

    print("\nRAVENSTACK — DAY 2 DATA QUALITY AUDIT")
    print("=" * 55)

    for file_name in DATASETS:
        summary, profiles = profile_dataset(file_name)

        if summary is not None:
            all_summaries.append(summary)
            all_column_profiles.extend(profiles)

    if not all_summaries:
        print("\nNo datasets were successfully loaded.")
        return

    # Save consolidated dataset summary
    summary_df = pd.DataFrame(all_summaries)
    summary_path = REPORT_DIR / "dataset_audit_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    # Save consolidated column-level profile
    profile_df = pd.DataFrame(all_column_profiles)
    profile_path = REPORT_DIR / "column_audit_profile.csv"
    profile_df.to_csv(profile_path, index=False)

    # Create a readable Markdown report
    report_path = REPORT_DIR / "day2_initial_audit_report.md"

    with open(report_path, "w", encoding="utf-8") as report:
        report.write("# Day 2 — Initial Data Quality Audit\n\n")
        report.write("**Project:** SaaS Revenue & Subscription Analytics\n\n")
        report.write("**Owner:** Jaykishan (Team Lead)\n\n")
        report.write("## Dataset-level summary\n\n")
        report.write(summary_df.to_markdown(index=False))
        report.write("\n\n## Audit notes\n\n")
        report.write(
            "- Raw CSV files were read without modification.\n"
            "- Duplicate rows and missing values were counted.\n"
            "- Columns containing 'id' were screened as possible "
            "identifiers only.\n"
            "- Date-like columns were screened for parsing failures.\n"
            "- No cleaning or deletion was performed.\n"
            "- Candidate keys and relationships require further validation.\n"
        )

    print("\n" + "=" * 55)
    print("AUDIT COMPLETED")
    print(f"Dataset summary: {summary_path}")
    print(f"Column profile: {profile_path}")
    print(f"Markdown report: {report_path}")


if __name__ == "__main__":
    main()
