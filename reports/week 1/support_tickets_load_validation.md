# Support Tickets Load Validation
## SaaS Revenue & Subscription Analytics

**Dataset:** RavenStack Support Tickets  
**Source File:** support_tickets_clean.csv  
**Target Table:** public.support_tickets  
**Expected Rows:** 2,000  
**Actual Loaded Rows:** 2,000  
**Status:** Loaded and Validated

---

## 1. Objective

Validate the support tickets dataset after loading it into Supabase PostgreSQL. Verify row counts, primary key uniqueness, foreign key relationships, missing values, and ticket chronology.

## 2. Load Summary

| Metric | Result |
|---|---:|
| Expected Rows | 2,000 |
| Actual Loaded Rows | 2,000 |
| Difference | 0 |
| Duplicate Rows (Day 2 Audit) | 0 |
| Missing Cells (Day 2 Audit) | 825 |
| Load Status | Passed |

## 3. Primary Key Validation

| Column | Constraint | Result |
|---|---|---|
| ticket_id | Primary Key | Verified |
| Duplicate ticket_id values | 0 | Passed |

## 4. Missing Value Validation

| Column | Missing Count | Percentage |
|---|---:|---:|
| satisfaction_score | 825 | 41.25% |

Missing satisfaction scores were preserved as NULL.

## 5. Foreign Key Validation

| Child Table | Foreign Key | Parent Table | Orphan Count |
|---|---|---|---:|
| support_tickets | account_id | accounts | 0 |

All tested account references were valid.

## 6. Ticket Date Chronology

| Validation | Invalid Records | Status |
|---|---:|---|
| closed_at earlier than submitted_at | 0 | Passed |

## 7. Numeric Range Review

| Column | Minimum | Maximum |
|---|---:|---:|
| resolution_time_hours | 1 | 72 |
| first_response_time_minutes | 1 | 180 |
| satisfaction_score | 3 | 5 |

The observed satisfaction score range is 3–5. Missing scores remain NULL.

## 8. Final Validation Summary

| Check | Status |
|---|---|
| Row Count | Passed |
| Primary Key | Passed |
| Missing Value Reconciliation | Completed |
| Foreign Key Relationship | Passed |
| Ticket Chronology | Passed |
| Numeric Range Review | Reviewed |

## 9. Conclusion

All 2,000 support ticket records were loaded successfully into Supabase PostgreSQL.

Primary key uniqueness and account relationships were verified. No invalid ticket date sequences were identified.

The 825 missing satisfaction scores were preserved as NULL.

**Overall Status:** Loaded and Validated
