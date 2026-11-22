# Subscriptions Load Validation
## SaaS Revenue & Subscription Analytics

**Dataset:** RavenStack Subscriptions  
**Source File:** subscriptions_clean.csv  
**Target Table:** public.subscriptions  
**Expected Rows:** 5,000  
**Actual Loaded Rows:** 5,000  
**Status:** Loaded and Validated

---

## 1. Objective

Validate the subscriptions dataset after loading it into Supabase PostgreSQL. Verify row counts, primary key uniqueness, foreign key relationships, missing values, subscription dates, and revenue consistency.

## 2. Load Summary

| Metric | Result |
|---|---:|
| Expected Rows | 5,000 |
| Actual Loaded Rows | 5,000 |
| Difference | 0 |
| Duplicate Rows (Day 2 Audit) | 0 |
| Missing Cells (Day 2 Audit) | 4,514 |
| Load Status | Passed |

## 3. Primary Key Validation

| Column | Constraint | Result |
|---|---|---|
| subscription_id | Primary Key | Verified |
| Duplicate subscription_id values | 0 | Passed |

## 4. Missing Value Validation

| Column | Missing Count | Percentage |
|---|---:|---:|
| end_date | 4,514 | 90.28% |

Missing end_date values were preserved as NULL.

## 5. Subscription End-Date Review

| churn_flag | is_trial | Total Records | Missing end_date |
|---|---|---:|---:|
| false | false | 3,814 | 3,814 |
| false | true | 700 | 700 |
| true | false | 408 | 0 |
| true | true | 78 | 0 |
| **Total** | | **5,000** | **4,514** |

The missing end dates occur in records where churn_flag is false.

These records may represent ongoing subscriptions, but this interpretation requires business confirmation.

No missing end dates were automatically replaced with artificial dates.

## 6. Foreign Key Validation

| Child Table | Foreign Key | Parent Table | Orphan Count |
|---|---|---|---:|
| subscriptions | account_id | accounts | 0 |

All tested account references were valid.

## 7. Subscription Date Chronology

| Validation | Invalid Records | Status |
|---|---:|---|
| end_date earlier than start_date | 0 | Passed |

## 8. MRR and ARR Consistency

| Metric | Result |
|---|---:|
| Total Subscriptions | 5,000 |
| MRR/ARR Mismatches | 0 |

No mismatches were identified under the tested ARR = MRR × 12 rule.

## 9. Numeric Range Review

| Column | Minimum | Maximum |
|---|---:|---:|
| seats | 1 | 189 |
| mrr_amount | 0.00 | 33,830.00 |
| arr_amount | 0.00 | 405,960.00 |

The observed ranges are documented for business-rule review.

## 10. Final Validation Summary

| Check | Status |
|---|---|
| Row Count | Passed |
| Primary Key | Passed |
| Missing Value Reconciliation | Completed |
| Foreign Key Relationship | Passed |
| Date Chronology | Passed |
| MRR/ARR Consistency | Passed |
| Numeric Range Review | Reviewed |

## 11. Conclusion

All 5,000 subscription records were loaded successfully into Supabase PostgreSQL.

Primary key uniqueness, account relationships, date chronology, and the tested MRR/ARR consistency rule passed validation.

The 4,514 missing end_date values were preserved as NULL pending confirmation of their business meaning.

**Overall Status:** Loaded and Validated – Business Interpretation Pending
