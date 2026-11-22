# Subscriptions Dataset – Data Quality Findings

**Project:** SaaS Revenue & Subscription Analytics  
**Dataset:** RavenStack  
**Dataset Owner:** Meghana  
**Reviewed By:** Jaykishan  
**Audit Phase:** Day 2 – EDA and Data Quality Audit  
**Status:** Initial Audit Completed – Business Validation Pending

---

## 1. Dataset Overview

Source file: `ravenstack_subscriptions.csv`

| Metric | Result |
|---|---:|
| Total Rows | 5,000 |
| Total Columns | 14 |
| Completely Duplicate Rows | 0 |
| Missing Cells | 4,514 |
| Unique Subscription IDs | 5,000 |
| Null Subscription IDs | 0 |
| Repeated Subscription IDs | 0 |

The Subscriptions dataset contains 5,000 records and 14 columns.

The main data quality concern is the large number of missing `end_date` values.

---

## 2. Column-Level Data Quality Findings

| Column | Observation | Status |
|---|---|---|
| subscription_id | 5,000 unique values, no nulls | Passed |
| account_id | All references matched Accounts | Passed |
| start_date | 5,000 dates successfully parsed | Passed |
| end_date | 4,514 missing values | Review Required |
| plan_tier | No missing values | Passed |
| seats | Values range from 1 to 189 | Review Required |
| mrr_amount | Values range from 0 to 33,830 | Review Required |
| arr_amount | Values range from 0 to 405,960 | Review Required |
| is_trial | No missing values | Passed |
| upgrade_flag | No missing values | Passed |
| downgrade_flag | No missing values | Passed |
| churn_flag | No missing values | Passed |
| billing_frequency | No missing values | Review Required |
| auto_renew_flag | No missing values | Passed |

---

## 3. Primary Key Validation

**Candidate Primary Key:** `subscription_id`

| Validation | Result |
|---|---:|
| Total Records | 5,000 |
| Null IDs | 0 |
| Unique IDs | 5,000 |
| Repeated IDs | 0 |

**Finding:** The `subscription_id` column passes the initial uniqueness and null checks and is suitable as the proposed primary key.

---

## 4. Missing Value Analysis

The initial audit identified 4,514 missing cells, all in the `end_date` column.

| Metric | Count |
|---|---:|
| Total Records | 5,000 |
| Missing end_date | 4,514 |
| Non-missing end_date | 486 |
| Missing Percentage | 90.28% |

### Important Investigation: Missing End Dates

The missing end dates were examined against subscription status and trial status.

| churn_flag | is_trial | Total Subscriptions | Missing end_date |
|---|---|---:|---:|
| False | False | 3,814 | 3,814 |
| False | True | 700 | 700 |
| True | False | 408 | 0 |
| True | True | 78 | 0 |
| **Total** | | **5,000** | **4,514** |

### Finding

- All 4,514 subscriptions with missing end dates have `churn_flag = False`.
- All subscriptions with `churn_flag = True` have an end date.
- The missing dates may represent ongoing subscriptions.

However, this interpretation requires business confirmation.

### Proposed Decision

1. Preserve missing `end_date` values as NULL.
2. Do not fill missing dates with the current date.
3. Do not delete subscriptions because their end dates are missing.
4. Confirm the meaning of missing end dates with the project team.
5. Use the confirmed business definition when calculating active subscriptions and subscription duration.

**Status:** Under Review.

---

## 5. Duplicate Record Analysis

| Validation | Result |
|---|---:|
| Completely Duplicate Rows | 0 |
| Repeated subscription_id Values | 0 |
| Null subscription_id Values | 0 |

**Finding:** No duplicate rows or repeated subscription identifiers were identified.

No record deletion is required based on the current duplicate checks.

---

## 6. Date Validation

### start_date

| Validation | Result |
|---|---:|
| Total Records Checked | 5,000 |
| Successfully Parsed | 5,000 |
| Parsing Failures | 0 |

### end_date

| Validation | Result |
|---|---:|
| Non-null Dates Checked | 486 |
| Successfully Parsed | 486 |
| Parsing Failures | 0 |
| Missing Dates | 4,514 |

**Proposed Decision:**
- Convert `start_date` to PostgreSQL DATE.
- Convert non-null `end_date` values to DATE.
- Preserve legitimate missing end dates as NULL.

The date ordering and subscription period rules still require validation.

---

## 7. Subscription Status Analysis

The subscription status and trial combinations were reviewed.

| churn_flag | is_trial | Total Subscriptions |
|---|---|---:|
| False | False | 3,814 |
| False | True | 700 |
| True | False | 408 |
| True | True | 78 |

Total subscriptions: 5,000.

These combinations should be retained for further analysis.

The team should confirm whether trial subscriptions marked as churned follow the same business definition as paid subscriptions marked as churned.

---

## 8. Numeric and Pricing Field Review

### Seats

| Metric | Value |
|---|---:|
| Minimum | 1 |
| Maximum | 189 |

Proposed data type: INTEGER.

### MRR Amount

| Metric | Value |
|---|---:|
| Minimum | 0 |
| Maximum | 33,830 |

Proposed data type: NUMERIC(12,2).

### ARR Amount

| Metric | Value |
|---|---:|
| Minimum | 0 |
| Maximum | 405,960 |

Proposed data type: NUMERIC(12,2).

### Pricing Validation

The relationship between MRR and ARR needs further investigation.

A simple check is:

ARR = MRR × 12

However, this relationship must be interpreted using the subscription's billing frequency and the dataset's revenue definitions.

**Proposed Decision:**
- Preserve the original MRR and ARR values.
- Do not automatically overwrite mismatching values.
- Investigate mismatches using billing frequency.
- Confirm the expected calculation rules before final revenue analysis.

**Status:** Pending Verification.

---

## 9. Referential Integrity Validation

**Relationship Tested:**

`subscriptions.account_id` → `accounts.account_id`

| Validation | Result |
|---|---:|
| Subscription Records Checked | 5,000 |
| Non-null Account References | 5,000 |
| Unmatched References | 0 |

**Finding:** All subscription account references matched existing account records.

The relationship is supported by the initial audit.

**Proposed Database Relationship:**

One account can have multiple subscriptions.

---

## 10. Proposed Cleaning Decisions

| Issue | Proposed Action | Status |
|---|---|---|
| Missing end_date | Preserve NULL until business meaning is confirmed | Under Review |
| Duplicate rows | No deletion required | Approved based on audit |
| subscription_id | Retain as primary key candidate | Approved based on audit |
| account_id | Retain as foreign key candidate | Approved based on audit |
| start_date | Standardize as DATE | Proposed |
| end_date | Standardize non-null values as DATE | Proposed |
| MRR and ARR | Validate using billing frequency | Pending |
| Seats | Preserve numeric values | Proposed |
| Boolean flags | Standardize as BOOLEAN | Proposed |
| Subscription date chronology | Validate date ordering and business rules | Pending |

---

## 11. Final Findings

The initial audit indicates:

1. The dataset contains 5,000 subscription records.
2. No completely duplicated rows were identified.
3. All subscription IDs are unique.
4. No subscription IDs are missing.
5. 4,514 records have missing end dates.
6. All missing end dates belong to records with `churn_flag = False`.
7. All churned subscriptions have non-missing end dates.
8. All account references matched existing Accounts records.
9. Start dates and non-null end dates passed initial parsing checks.
10. MRR/ARR consistency and subscription date chronology still require validation.

---

## 12. Conclusion

The Subscriptions dataset passed its initial primary key, duplicate-row, account-reference and date-parsing checks.

The main issue requiring business validation is the interpretation of missing subscription end dates.

Pricing consistency and date chronology must also be reviewed before final schema approval and revenue analysis.

The original raw CSV must remain unchanged. Any cleaned output should be stored separately as `subscriptions_clean.csv`.

**Prepared by:** Meghana  
**Reviewed by:** Jaykishan  
**Final Approval:** Approved