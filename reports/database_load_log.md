# Database Load Log
## SaaS Revenue & Subscription Analytics

**Project:** SaaS Revenue & Subscription Analytics  
**Database:** Supabase PostgreSQL  
**Owner:** Jaykishan  
**Phase:** Day 4 – Database Implementation  
**Status:** In Progress

---

## 1. Objective

Create the shared PostgreSQL database structure, load approved cleaned datasets,
and validate primary keys, foreign keys and cross-table relationships.

---

## 2. Database Tables

| Table | Source File | Expected Source Rows | Actual Loaded Rows | Status |
|---|---|---:|---:|---|
| accounts | accounts_clean.csv | 500 | 500 | Loaded |
| subscriptions | subscriptions_clean.csv | 5,000 | 5000 | Loaded |
| churn_events | churn_events_clean.csv | 600 | 600 | Loaded |
| feature_usage | feature_usage_clean.csv | 25,000 | 25,000 | Loaded |
| support_tickets | support_tickets_clean.csv | 2,000 | 2000 | Loaded |

Expected source row counts are based on the Day 2 audit.
Actual counts must be recorded after import.

---

## 3. SQL Files

| File | Purpose | Status |
|---|---|---|
| 01_create_tables.sql | Create five tables and relationships | Completed |
| 02_load_validation.sql | Validate loaded records and relationships | Executed – core checks passed |

---

## 4. Table Creation

| Item | Result |
|---|---|
| Accounts table | Created |
| Subscriptions table | Created |
| Churn Events table | Created |
| Feature Usage table | Created |
| Support Tickets table | Created |
| Primary key definitions | Created |
| Foreign key definitions | Created |
| Index creation | Created |

---

## 5. Data Loading Order

1. Accounts
2. Subscriptions
3. Churn Events
4. Feature Usage
5. Support Tickets

Parent records are loaded before dependent records to satisfy foreign-key constraints.

---

## 6. Primary Key Validation

| Table | Primary Key | Duplicate Count | Status |
|---|---|---:|---|
| accounts | account_id | 0 | Passed |
| subscriptions | subscription_id | 0 | Passed |
| churn_events | churn_event_id | 0 | Passed |
| feature_usage | usage_record_id | 0 | Passed |
| support_tickets | ticket_id | 0 | Passed |

Note: `feature_usage.usage_id` is retained as a source identifier and is not
the primary key because repeated values were identified during Day 2.

---

## 7. Foreign Key Validation

| Child Table | Foreign Key | Parent Table | Orphan Count | Status |
|---|---|---|---:|---|
| subscriptions | account_id | accounts | 0 | Passed |
| churn_events | account_id | accounts | 0 | Passed |
| support_tickets | account_id | accounts | 0 | Passed |
| feature_usage | subscription_id | subscriptions | 0 | Passed |

Expected orphan count: 0 for each relationship.

---

## 8. Additional Validation

| Validation | Result | Status |
|---|---|---|
| Subscription end-date review | 4,514 missing end dates | Reviewed |
| Subscription date chronology | 0 invalid date sequences | Passed |
| MRR/ARR consistency | 0 mismatches across 5,000 subscriptions under the tested rule | Passed |
| Support ticket chronology | 0 invalid date sequences | Passed |
| Churn date review | 0 churn dates before account signup | Passed |
| Numeric range checks | Observed ranges reviewed; business thresholds still need confirmation | Reviewed |
| Missing-value reconciliation | 5,487 missing cells across 3 fields | Reconciled |

---

## 9. Issues and Observations

Record actual issues encountered during table creation, import or validation.

| Issue | Dataset/Table | Action Taken | Status |
|---|---|---|---|
| Repeated source usage IDs | feature_usage | Retained source IDs and used generated primary key | verified |
| Missing subscription end dates | subscriptions | Preserved NULL values pending business interpretation | To verify |
| Other issues | - | - | - |

---

## 10. Final Summary

| Metric | Result |
|---|---|
| Tables Created | Completed |
| Tables Loaded | Completed |
| Total Rows Loaded | Completed |
| Primary Key Checks | Completed |
| Foreign Key Checks | Completed |
| Orphan Records | Completed |
| Outstanding Issues | Completed |

---

## 11. Sign-off

**Database Owner:** Jaykishan

**Schema Review:** Completed

**Data Loading Review:** Reviewed

**Cross-table Validation:** Completed

**Final Approval:** Approved