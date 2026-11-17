# Accounts — Week 1 Summary

**Prepared by:** Yashashvi Yash  
**Date:** 2026-11-17  
**Dataset:** `ravenstack_accounts.csv`  
**Cleaned output:** `accounts_clean.csv`  
**Scope:** Accounts dataset preparation, cleaning, documentation, and pre-load validation.

## 1. Objective

Prepare a reliable account-level dataset for the SaaS Revenue & Subscription Analytics project. The work focused on inspecting the source data, preserving the raw file, producing a cleaned CSV, documenting the transformations, and validating the output before database loading.

## 2. Source dataset overview

The accounts source file contains **500 rows and 10 columns**. Each row represents one account.

The fields are:

- `account_id`
- `account_name`
- `industry`
- `country`
- `signup_date`
- `referral_source`
- `plan_tier`
- `seats`
- `is_trial`
- `churn_flag`

The observed categories include five industries (EdTech, FinTech, DevTools, HealthTech, Cybersecurity), seven country codes (US, IN, UK, CA, DE, AU, FR), five referral sources (partner, other, organic, event, ads), and three plan tiers (Basic, Pro, Enterprise).

## 3. Work completed

### A. Data inspection

- Reviewed the accounts file structure, row and column counts, field names, data types, and observed values.
- Checked missing cells and exact duplicate rows.
- Checked the uniqueness and completeness of `account_id`.
- Reviewed `signup_date` formatting and date coverage.

### B. Data cleaning

Created `accounts_clean.csv` as a separate output while preserving the original raw CSV.

Transformations performed:
1. Trimmed surrounding whitespace from column names.
2. Standardized column names to lowercase with underscores.
3. Trimmed leading and trailing whitespace from text values.
4. Parsed `signup_date` using the `YYYY-MM-DD` format and retained the ISO date representation in the CSV.
5. Preserved all records; no rows were intentionally deleted and no values were imputed.

No business categories were remapped, and no outlier removal or business-rule changes were applied.

### C. Documentation

Created the following supporting files:

- `reports/accounts_quality_findings.md` — records the accounts and subscription dataset quality observations, including the account/subscription relationship and issues relevant to downstream analysis.
- `reports/accounts_cleaning_log.md` — records the accounts cleaning steps, input/output details, and validation results.
- `reports/accounts_load_validation.md` — records pre-load file validation and provides SQL checks to run after database loading.

## 4. Cleaning and validation results

| Check | Result |
|---|---:|
| Rows in cleaned dataset | 500 |
| Columns in cleaned dataset | 10 |
| Missing cells | 0 |
| Exact duplicate rows | 0 |
| Null `account_id` values | 0 |
| Duplicate `account_id` values | 0 |
| Invalid non-empty `signup_date` values | 0 |
| `signup_date` coverage | 2023-01-02 to 2024-12-31 |

**File-level result:** All recorded validation checks passed. The cleaned output retains all 500 account records.

## 5. Data structure and downstream use

`account_id` is the account-level identifier and is suitable for joining the accounts dataset to the supplied subscriptions dataset. The observed relationship is one-to-many: multiple subscription records can belong to one account.

For downstream analysis:
- Keep account-level metrics at account grain.
- Aggregate subscription-level data before calculating account-level totals to avoid double-counting after joins.
- Use `signup_date` as a date field for time-based analysis; cast it to a database `DATE` type when loading.
- Treat `plan_tier`, `industry`, `country`, `referral_source`, `is_trial`, and `churn_flag` as segmentation fields.

## 6. Database load status

The cleaned CSV has been validated before loading. **A database load has not been confirmed by this work.**

After importing `accounts_clean.csv` into the target `accounts` table, run the SQL checks in `accounts_load_validation.md` to verify:
- Loaded row count equals 500.
- `account_id` contains no nulls.
- `account_id` contains no duplicates.
- Required account fields have no unexpected null values.
- `signup_date` is stored using a date-compatible database type.

## 7. Deliverables

| Deliverable | Purpose |
|---|---|
| `accounts_clean.csv` | Cleaned account-level dataset |
| `accounts_quality_findings.md` | Dataset quality observations and handling recommendations |
| `accounts_cleaning_log.md` | Record of transformations and cleaning checks |
| `accounts_load_validation.md` | Pre-load results and post-load SQL validation checklist |
| `accounts_week1_summary.md` | Summary of the accounts work completed |

## 8. Handover / next steps

1. Place `accounts_clean.csv` in the project's `data/clean/` directory.
2. Place the Markdown reports in `reports/`.
3. Load the cleaned CSV into the target database table.
4. Execute the post-load SQL checks and update the validation status with the actual database results.
5. Continue with the subscriptions dataset and validate the `account_id` relationship before building combined analytical tables.

## 9. Overall conclusion

The accounts dataset has been inspected, cleaned, documented, and passed the recorded file-level validation checks. The cleaned file contains 500 rows and 10 columns, with no missing cells, duplicate rows, null account IDs, duplicate account IDs, or invalid non-empty signup dates. The raw source remains separate and unchanged. Database load validation is still pending and must be completed after the CSV is imported.
