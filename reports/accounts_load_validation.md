# Accounts Load Validation
## SaaS Revenue & Subscription Analytics

**Dataset:** RavenStack Accounts  
**Source File:** accounts_clean.csv  
**Target Table:** public.accounts  
**Expected Rows:** 500  
**Actual Loaded Rows:** 500  
**Status:** Loaded and Validated

---

## 1. Objective

Validate the accounts dataset after loading it into Supabase PostgreSQL. Verify row counts, primary key uniqueness, missing values, and relationships with dependent tables.

## 2. Load Summary

| Metric | Result |
|---|---:|
| Expected Rows | 500 |
| Actual Loaded Rows | 500 |
| Difference | 0 |
| Duplicate Rows (Day 2 Audit) | 0 |
| Missing Cells (Day 2 Audit) | 0 |
| Load Status | Passed |

## 3. Primary Key Validation

| Column | Constraint | Result |
|---|---|---|
| account_id | Primary Key | Verified |
| Duplicate account_id values | 0 | Passed |

## 4. Missing Value Validation

The Day 2 audit identified no missing values in the accounts dataset.

| Validation | Missing Count | Status |
|---|---:|---|
| All accounts columns | 0 | Passed |

## 5. Foreign Key Relationship Validation

The accounts table acts as a parent table for the following relationships.

| Parent Table | Child Table | Relationship | Orphan Count |
|---|---|---|---:|
| accounts | subscriptions | account_id | 0 |
| accounts | churn_events | account_id | 0 |
| accounts | support_tickets | account_id | 0 |

All tested child records reference existing account records.

## 6. Numeric Range Review

| Column | Minimum | Maximum |
|---|---:|---:|
| seats | 1 | 163 |

The observed seat range is documented for further business-rule review.

## 7. Final Validation Summary

| Check | Status |
|---|---|
| Row Count | Passed |
| Primary Key | Passed |
| Missing Values | Passed |
| Foreign Key Relationships | Passed |
| Numeric Range Review | Reviewed |

## 8. Conclusion

All 500 accounts records were loaded successfully into Supabase PostgreSQL.

The account_id primary key was verified, no missing cells were identified during the Day 2 audit, and all three tested relationships returned zero orphan records.

**Overall Status:** Loaded and Validated
