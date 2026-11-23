# RavenStack Cleaned CSV Preparation Log

## Scope
Prepared five standardized CSV exports from the uploaded RavenStack raw dataset ZIP for the Day 4 Supabase import.

## Cleaning approach
- Preserved all source records; no rows were deleted.
- Preserved original column names and column order.
- Trimmed leading/trailing whitespace in text values.
- Standardized date columns to `YYYY-MM-DD`.
- Standardized support ticket timestamps to `YYYY-MM-DD HH:MM:SS`.
- Preserved genuine missing values as blank CSV fields (import as SQL NULL).
- Converted nullable `satisfaction_score` values to integer representation (3, 4, 5), retaining missing values.
- Did not invent values, fill missing dates, alter MRR/ARR, or deduplicate source events.

## Important findings retained for review
1. `subscriptions.end_date` is missing in 4,514 of 5,000 rows. The source README describes this field as nullable for active plans; values were preserved as NULL.
2. `churn_events.feedback_text` is missing in 148 of 600 rows; preserved as NULL.
3. `support_tickets.satisfaction_score` is missing in 825 of 2,000 rows; preserved as NULL.
4. `feature_usage.usage_id` has 21 repeated identifier values affecting 42 rows, despite the source README describing it as a unique usage event ID. No records or identifiers were changed. Use a separate database-generated surrogate primary key for feature usage, retaining `usage_id` as the source identifier.
5. Referential integrity checks found zero unmatched references for subscriptions → accounts, churn events → accounts, support tickets → accounts, and feature usage → subscriptions.
6. Date chronology check found 19,142 feature usage rows dated before their linked subscription's `start_date`, and 290 dated after a non-null subscription `end_date`. These were not altered or deleted; investigate with the dataset owner before using usage-to-subscription lifecycle metrics.
7. No exact duplicate rows were found in any of the five raw datasets.
8. `arr_amount` equalled `mrr_amount * 12` for all 5,000 subscriptions in the source data.

## Output validation

| File | Rows | Columns | Exact duplicate rows | Missing cells |
|---|---:|---:|---:|---:|
| accounts_clean.csv | 500 | 10 | 0 | 0 |
| subscriptions_clean.csv | 5000 | 14 | 0 | 4514 |
| churn_events_clean.csv | 600 | 9 | 0 | 148 |
| feature_usage_clean.csv | 25000 | 8 | 0 | 0 |
| support_tickets_clean.csv | 2000 | 9 | 0 | 825 |

All five outputs retain the original source row counts and column structure. These are standardized import-ready exports, not a claim that every business-rule anomaly has been resolved.
