# Churn Events and Feature Usage Load Validation
## SaaS Revenue & Subscription Analytics

---

# Part A: Churn Events

**Source File:** churn_events_clean.csv  
**Target Table:** public.churn_events  
**Expected Rows:** 600  
**Actual Loaded Rows:** 600  
**Status:** Loaded and Validated

## 1. Load Summary

| Metric | Result |
|---|---:|
| Expected Rows | 600 |
| Actual Loaded Rows | 600 |
| Difference | 0 |
| Duplicate Rows (Day 2 Audit) | 0 |
| Missing Cells (Day 2 Audit) | 148 |
| Load Status | Passed |

## 2. Primary Key Validation

| Column | Constraint | Result |
|---|---|---|
| churn_event_id | Primary Key | Verified |
| Duplicate churn_event_id values | 0 | Passed |

## 3. Missing Value Validation

| Column | Missing Count | Percentage |
|---|---:|---:|
| feedback_text | 148 | 24.67% |

Missing feedback text values were preserved as NULL.

## 4. Foreign Key Validation

| Child Table | Foreign Key | Parent Table | Orphan Count |
|---|---|---|---:|
| churn_events | account_id | accounts | 0 |

## 5. Numeric Range Review

| Column | Minimum | Maximum |
|---|---:|---:|
| refund_amount_usd | 0.00 | 392.92 |

## 6. Date Validation

No churn events were found with churn dates earlier than the associated account signup dates.

| Validation | Invalid Records | Status |
|---|---:|---|
| Churn date before account signup | 0 | Passed |

## 7. Churn Events Conclusion

All 600 churn event records were loaded successfully.

Primary key uniqueness and account relationships were verified. Missing feedback text was preserved as NULL.

---

# Part B: Feature Usage

**Source File:** feature_usage_clean.csv  
**Target Table:** public.feature_usage  
**Expected Rows:** 25,000  
**Actual Loaded Rows:** 25,000  
**Status:** Loaded and Validated

## 1. Load Summary

| Metric | Result |
|---|---:|
| Expected Rows | 25,000 |
| Actual Loaded Rows | 25,000 |
| Difference | 0 |
| Duplicate Rows (Day 2 Audit) | 0 |
| Missing Cells (Day 2 Audit) | 0 |
| Load Status | Passed |

## 2. Primary Key Validation

| Column | Constraint | Result |
|---|---|---|
| usage_record_id | Generated Primary Key | Verified |
| Duplicate usage_record_id values | 0 | Passed |

The source usage_id column is retained separately because repeated source identifiers were identified during the Day 2 audit.

## 3. Source Identifier Review

| Metric | Result |
|---|---:|
| Total Records | 25,000 |
| Unique Source IDs | 24,979 |
| Repeated ID Excess | 21 |

A database-generated usage_record_id is used as the primary key. The original usage_id is retained for source traceability.

## 4. Missing Value Validation

| Validation | Missing Count | Status |
|---|---:|---|
| All feature_usage columns | 0 | Passed |

## 5. Foreign Key Validation

| Child Table | Foreign Key | Parent Table | Orphan Count |
|---|---|---|---:|
| feature_usage | subscription_id | subscriptions | 0 |

## 6. Numeric Range Review

| Column | Minimum | Maximum |
|---|---:|---:|
| usage_count | 0 | 26 |
| error_count | 0 | 8 |

## 7. Feature Usage Conclusion

All 25,000 feature usage records were loaded successfully.

The generated usage_record_id primary key was verified. Repeated source usage_id values were retained without being used as the primary key.

All tested subscription relationships returned zero orphan records.

---

## Final Combined Summary

| Dataset | Expected Rows | Actual Rows | Status |
|---|---:|---:|---|
| Churn Events | 600 | 600 | Passed |
| Feature Usage | 25,000 | 25,000 | Passed |
| Total | 25,600 | 25,600 | Passed |

**Overall Status:** Loaded and Validated
