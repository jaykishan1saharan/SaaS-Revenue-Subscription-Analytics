# Accounts Dataset – Data Quality Findings

**Project:** SaaS Revenue & Subscription Analytics  
**Dataset:** RavenStack  
**Dataset Owner:** Yash  
**Reviewed By:** Jaykishan  
**Audit Phase:** Day 2 – EDA and Data Quality Audit  
**Status:** Initial Audit Completed – Distribution Review Pending

---

## 1. Dataset Overview

Source file: `ravenstack_accounts.csv`

| Metric | Result |
|---|---:|
| Total Rows | 500 |
| Total Columns | 10 |
| Completely Duplicate Rows | 0 |
| Missing Cells | 0 |
| Unique Account IDs | 500 |
| Null Account IDs | 0 |
| Repeated Account IDs | 0 |

The Accounts dataset contains 500 records and 10 columns. No completely duplicated rows or missing cells were identified during the initial audit.

---

## 2. Column-Level Data Quality Findings

| Column | Observation | Status |
|---|---|---|
| account_id | 500 unique values, no nulls | Passed |
| account_name | No missing values | Passed |
| industry | No missing values | Passed |
| country | No missing values | Passed |
| signup_date | 500 dates successfully parsed during initial audit | Passed |
| referral_source | No missing values | Passed |
| plan_tier | No missing values | Passed |
| seats | Values range from 1 to 163 | Review Required |
| is_trial | No missing values | Passed |
| churn_flag | No missing values | Passed |

---

## 3. Primary Key Validation

**Candidate Primary Key:** `account_id`

| Validation | Result |
|---|---:|
| Total Records | 500 |
| Null IDs | 0 |
| Unique IDs | 500 |
| Repeated IDs | 0 |

**Finding:** The `account_id` column satisfies the initial uniqueness and null checks and is suitable as the proposed primary key.

---

## 4. Missing Value Analysis

No missing values were found in the Accounts dataset.

| Metric | Count |
|---|---:|
| Total Cells | 5,000 |
| Missing Cells | 0 |
| Missing Percentage | 0% |

**Decision:** No missing-value treatment is required based on the initial audit.

---

## 5. Duplicate Record Analysis

- Completely duplicated rows: 0
- Repeated `account_id` values: 0

**Finding:** No duplicate records or duplicate account identifiers were identified.

No records should be removed based on the current duplicate checks.

---

## 6. Numeric Value Review

### Seats

| Metric | Value |
|---|---:|
| Minimum | 1 |
| Maximum | 163 |

The number of seats varies across accounts.

These values should be reviewed for unusual business cases, but they should not automatically be classified as invalid.

**Proposed Decision:**
- Preserve the original seat counts.
- Use an INTEGER data type.
- Investigate unusual values only if business rules identify a valid upper limit.

---

## 7. Date Validation

The `signup_date` column was checked during the initial date audit.

| Validation | Result |
|---|---:|
| Total Records Checked | 500 |
| Successfully Parsed | 500 |
| Parsing Failures | 0 |

**Proposed Decision:** Convert `signup_date` to the PostgreSQL DATE data type.

---

## 8. Account Distribution Analysis

The following distributions should be reviewed by the dataset owner:

- Accounts by industry
- Accounts by country
- Accounts by plan tier
- Accounts by referral source
- Trial versus non-trial accounts
- Churned versus non-churned accounts
- Distribution of seats

**Status:** Detailed distribution counts and charts have not yet been included in the central audit results. They must be generated and reviewed before this section is marked complete.

---

## 9. Proposed Cleaning Decisions

| Issue | Proposed Action | Status |
|---|---|---|
| Missing values | No treatment required | Approved based on audit |
| Duplicate rows | No deletion required | Approved based on audit |
| Account ID | Retain as primary key candidate | Approved based on audit |
| Signup date | Standardize as DATE | Proposed |
| Seats | Preserve numeric values | Proposed |
| Text columns | Preserve source categories and values | Proposed |
| Account distributions | Generate distribution summaries | Pending |

---

## 10. Final Findings

The initial audit indicates that the Accounts dataset has good structural quality.

Key findings:

1. 500 account records were identified.
2. No missing cells were found.
3. No completely duplicated rows were found.
4. All 500 account IDs are unique.
5. No null account IDs were found.
6. Signup dates passed the initial parsing check.
7. Seat values range from 1 to 163 and require business-context review.
8. Detailed account distributions still need to be documented.

---

## 11. Conclusion

The Accounts dataset passed the initial missing-value, duplicate-row and account identifier checks.

The dataset can proceed to the approved cleaning stage after distribution analysis and final team review.

The original raw CSV must remain unchanged. Any cleaned output should be stored separately as `accounts_clean.csv`.

**Prepared by:** Yash  
**Reviewed by:** Jaykishan  
**Final Approval:** Approved