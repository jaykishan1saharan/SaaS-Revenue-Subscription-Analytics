# Cleaning Decision Log
## SaaS Revenue & Subscription Analytics

**Project:** SaaS Revenue & Subscription Analytics  
**Dataset:** RavenStack  
**Prepared by:** Jaykishan (Team Lead)  
**Phase:** Day 3 – Data Cleaning and Schema Design  
**Status:** Draft – Pending Team Review and Approval

---

## 1. Purpose

This document records the proposed data-cleaning decisions for all five RavenStack datasets.

The objective is to ensure that:
- Original raw datasets remain unchanged.
- Cleaning decisions are consistent across team members.
- Missing values are handled according to business meaning.
- Duplicate records and identifier issues are investigated before removal.
- Data types and naming conventions are standardized.
- Every transformation is documented and reproducible.

**Important:** These are proposed decisions based on the Day 2 audit. Decisions marked Pending must be confirmed before implementation.

---

## 2. Day 2 Data Quality Summary

| Dataset | Rows | Columns | Duplicate Rows | Missing Cells |
|---|---:|---:|---:|---:|
| Accounts | 500 | 10 | 0 | 0 |
| Churn Events | 600 | 9 | 0 | 148 |
| Feature Usage | 25,000 | 8 | 0 | 0 |
| Subscriptions | 5,000 | 14 | 0 | 4,514 |
| Support Tickets | 2,000 | 9 | 0 | 825 |
| **Total** | **33,100** | **50** | **0** | **5,487** |

---

## 3. Proposed Cleaning Decisions

### 3.1 Accounts

| Column | Observation | Proposed Decision | Status |
|---|---|---|---|
| account_id | 500 unique, no nulls | Preserve as account identifier | Approved for schema draft |
| signup_date | No parsing failures in initial audit | Convert to DATE | Proposed |
| seats | Values range from 1 to 163 | Retain numeric values; investigate unusual values with business context | Pending |
| is_trial | Boolean field | Standardize as BOOLEAN | Proposed |
| churn_flag | Boolean field | Standardize as BOOLEAN | Proposed |

No missing values or completely duplicated rows were identified.

**Rule:** Do not remove accounts based only on unusual seat counts or other values without business validation.

### 3.2 Churn Events

| Column | Observation | Proposed Decision | Status |
|---|---|---|---|
| churn_event_id | 600 unique, no nulls | Preserve as primary identifier | Approved for schema draft |
| account_id | All references matched | Preserve account relationship | Approved for schema draft |
| churn_date | No parsing failures in initial audit | Convert to DATE | Proposed |
| feedback_text | 148 missing values (24.67%) | Retain as NULL; do not invent feedback | Proposed |
| refund_amount_usd | Values range from 0 to 392.92 | Use NUMERIC(12,2); validate business rules | Proposed |
| preceding_upgrade_flag | Boolean field | Standardize as BOOLEAN | Proposed |
| preceding_downgrade_flag | Boolean field | Standardize as BOOLEAN | Proposed |
| is_reactivation | Boolean field | Standardize as BOOLEAN | Proposed |

**Rule:** Missing feedback must not be replaced with fabricated text.

### 3.3 Feature Usage

| Column | Observation | Proposed Decision | Status |
|---|---|---|---|
| usage_id | 21 repeated ID values affecting 42 rows | Do not use as a primary key until resolved | Under Review |
| subscription_id | All references matched | Preserve subscription relationship | Approved for schema draft |
| usage_date | No parsing failures in initial audit | Convert to DATE | Proposed |
| feature_name | Text field | Standardize as TEXT; preserve actual feature names | Proposed |
| usage_count | Values range from 0 to 26 | Use INTEGER; investigate negative values if found in later validation | Proposed |
| usage_duration_secs | Values range from 0 to 12,696 | Use INTEGER | Proposed |
| error_count | Values range from 0 to 8 | Use INTEGER | Proposed |
| is_beta_feature | Boolean field | Standardize as BOOLEAN | Proposed |

**Important identifier issue:**

The dataset contains 21 repeated `usage_id` values affecting 42 rows. However, there are zero completely duplicated rows.

Therefore:
- Do not delete these records as duplicate events.
- Do not assume repeated IDs represent identical usage events.
- Investigate the identifier generation issue.
- Do not declare `usage_id` as a primary key until uniqueness is established.
- Consider a database-generated surrogate key if a unique row identifier is needed.

### 3.4 Subscriptions

| Column | Observation | Proposed Decision | Status |
|---|---|---|---|
| subscription_id | 5,000 unique, no nulls | Preserve as primary identifier | Approved for schema draft |
| account_id | All references matched | Preserve account relationship | Approved for schema draft |
| start_date | No parsing failures in initial audit | Convert to DATE | Proposed |
| end_date | 4,514 missing values (90.28%) | Preserve NULL until business meaning is confirmed | Under Review |
| plan_tier | Text field | Standardize as TEXT; preserve source categories | Proposed |
| seats | Values range from 1 to 189 | Use INTEGER; investigate unusual values | Proposed |
| mrr_amount | Values range from 0 to 33,830 | Use NUMERIC(12,2) | Proposed |
| arr_amount | Values range from 0 to 405,960 | Use NUMERIC(12,2) | Proposed |
| is_trial | Boolean field | Standardize as BOOLEAN | Proposed |
| upgrade_flag | Boolean field | Standardize as BOOLEAN | Proposed |
| downgrade_flag | Boolean field | Standardize as BOOLEAN | Proposed |
| churn_flag | Boolean field | Standardize as BOOLEAN | Proposed |
| billing_frequency | Text field | Standardize as TEXT; validate categories | Proposed |
| auto_renew_flag | Boolean field | Standardize as BOOLEAN | Proposed |

**End-date investigation:**

All 4,514 missing end dates belong to records where `churn_flag = False`. All records with `churn_flag = True` have an end date.

These missing dates may represent ongoing subscriptions, but this interpretation requires business confirmation.

Do not fill missing end dates with the current date or an artificial date.

**Revenue validation:**

Validate the relationship between MRR, ARR and billing frequency before assuming that:

ARR = MRR × 12

Any mismatch should be investigated rather than automatically corrected.

### 3.5 Support Tickets

| Column | Observation | Proposed Decision | Status |
|---|---|---|---|
| ticket_id | 2,000 unique, no nulls | Preserve as primary identifier | Approved for schema draft |
| account_id | All references matched | Preserve account relationship | Approved for schema draft |
| submitted_at | Timestamp field | Convert to TIMESTAMP | Proposed |
| closed_at | Timestamp field | Convert to TIMESTAMP; retain NULL if legitimately unresolved | Proposed |
| resolution_time_hours | Values range from 1 to 72 | Use NUMERIC(10,2) or INTEGER after checking source precision | Proposed |
| priority | Text field | Standardize as TEXT; validate categories | Proposed |
| first_response_time_minutes | Values range from 1 to 180 | Use NUMERIC(10,2) or INTEGER after checking source precision | Proposed |
| satisfaction_score | 825 missing values (41.25%) | Retain NULL; do not assign artificial ratings | Proposed |
| escalation_flag | Boolean field | Standardize as BOOLEAN | Proposed |

**Rule:** A missing satisfaction score must not be treated as zero or as a negative customer rating.

---

## 4. General Cleaning Standards

1. Never modify files inside `data/raw/`.
2. Store cleaned outputs inside `data/interim/`.
3. Preserve original column meaning and source identifiers.
4. Use lowercase snake_case for database column names.
5. Use explicit date and numeric types rather than storing everything as text.
6. Preserve legitimate NULL values.
7. Do not remove records without a documented reason.
8. Do not fabricate missing values or business events.
9. Record every cleaning operation in a dataset-specific cleaning log.
10. Validate row counts and key constraints after cleaning.
11. Keep transformations reproducible through Python scripts or notebooks.
12. Confirm all unresolved business rules with the team before final implementation.

---

## 5. Naming Convention

| Object | Convention | Example |
|---|---|---|
| Tables | lowercase snake_case | accounts |
| Columns | lowercase snake_case | account_id |
| Primary keys | table-specific ID | account_id |
| Foreign keys | referenced table ID | account_id |
| Cleaned CSV files | original_name_clean.csv | accounts_clean.csv |
| Python scripts | lowercase snake_case.py | data_quality_audit.py |
| Documentation | lowercase_snake_case.md | data_dictionary.md |

---

## 6. Pending Decisions and Approvals

| Decision | Responsible Person | Status |
|---|---|---|
| Confirm missing subscription end-date meaning | Jaykishan + Meghana | Pending |
| Investigate repeated usage_id values | Jaykishan + Madhupriya | Pending |
| Confirm MRR/ARR consistency rules | Jaykishan + Meghana | Pending |
| Validate support ticket timestamp chronology | Jaykishan + Lav Kumar | Pending |
| Confirm accepted categories for text fields | Relevant dataset owners | Pending |
| Approve final cleaning rules | Jaykishan | Pending |

---

## 7. Approval Record

| Role | Name | Approval Status |
|---|---|---|
| Team Lead | Jaykishan | Pending |
| Accounts | Yash | Pending |
| Churn Events and Feature Usage | Madhupriya | Pending |
| Subscriptions | Meghana | Pending |
| Support Tickets and Schema | Lav Kumar | Pending |

---

## 8. Final Note

This document is a draft of the proposed cleaning standards.

Only decisions that have been reviewed and approved should be implemented in the cleaned datasets.

The original RavenStack CSV files must remain unchanged throughout the project.