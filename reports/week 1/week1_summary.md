# Week 1 Summary — SaaS Revenue & Subscription Analytics

## 1. Project Overview

**Project:** SaaS Revenue & Subscription Analytics  
**Dataset:** RavenStack  
**Database:** Supabase PostgreSQL  
**Week:** Week 1 — Project Setup, Data Understanding, Cleaning Preparation, Database Design and Data Loading  
**Team Member:** Jaykishan

### Objective

Build an end-to-end SaaS analytics project to understand subscription performance, recurring revenue, customer churn, product usage, and support operations.

The project aims to develop reliable data foundations before calculating business KPIs and creating analytical outputs.

---

## 2. Dataset Overview

The project uses five RavenStack CSV datasets.

| Dataset | Rows Loaded | Columns |
|---|---:|---:|
| Accounts | 500 | 10 |
| Churn Events | 600 | 9 |
| Feature Usage | 25,000 | 8 |
| Subscriptions | 5,000 | 14 |
| Support Tickets | 2,000 | 9 |
| **Total** | **33,100** | **50** |

### Dataset Files

- `ravenstack_accounts.csv`
- `ravenstack_churn_events.csv`
- `ravenstack_feature_usage.csv`
- `ravenstack_subscriptions.csv`
- `ravenstack_support_tickets.csv`

---

## 3. Week 1 Work Completed

### Day 1 — Project Setup and Repository Structure

- Established the GitHub project repository.
- Created the project folder structure.
- Configured `.gitignore` to exclude environment files, virtual environments, and raw/interim/processed datasets.
- Prepared `requirements.txt` and the initial README.
- Established the team Git workflow using personal branches and pull requests.

### Day 2 — Dataset Audit and Initial Data Understanding

- Inspected all five raw CSV datasets.
- Generated dataset-level row, column, duplicate, and missing-value summaries.
- Reviewed candidate primary key columns.
- Identified missing values and repeated source identifiers.
- Recorded initial data-quality observations.

### Day 3 — Data Cleaning Decisions and Documentation

Prepared the following documentation:

- `docs/cleaning_decision_log.md`
- `docs/data_dictionary.md`

These documents record the proposed cleaning rules, field meanings, and data interpretation decisions for team review.

### Day 4 — Supabase Database Setup and Data Loading

- Created the five project tables in Supabase PostgreSQL.
- Loaded all five datasets into the database.
- Verified primary key constraints.
- Verified foreign key relationships.
- Checked database row counts against the expected dataset sizes.
- Performed additional data-quality checks.
- Prepared individual dataset load-validation reports.
- Prepared `sql/03_initial_exploration.sql` for initial SQL exploration.

### Day 5 — Final Review and Week 2 Handover

- Consolidated Week 1 project documentation.
- Prepared the Week 1 summary.
- Prepared the Week 2 handover document.
- Updated the project README.
- Reviewed database validation results and outstanding items.

---

## 4. Database Validation Results

### 4.1 Database Row Counts

| Table | Expected Rows | Loaded Rows | Status |
|---|---:|---:|---|
| accounts | 500 | 500 | Passed |
| churn_events | 600 | 600 | Passed |
| feature_usage | 25,000 | 25,000 | Passed |
| subscriptions | 5,000 | 5,000 | Passed |
| support_tickets | 2,000 | 2,000 | Passed |
| **Total** | **33,100** | **33,100** | **Passed** |

### 4.2 Primary Key Validation

All five tables have primary key constraints.

- Duplicate primary key checks returned zero duplicates.
- The `feature_usage` table uses a generated `usage_record_id` as its database primary key.
- The original `usage_id` is retained as a source identifier and is not unique across all 25,000 records.

**Result:** 5 out of 5 primary key checks passed.

### 4.3 Foreign Key Validation

The following relationships were verified:

| Child Table | Foreign Key | Referenced Table | Orphan Records |
|---|---|---|---:|
| subscriptions | account_id | accounts | 0 |
| churn_events | account_id | accounts | 0 |
| feature_usage | subscription_id | subscriptions | 0 |
| support_tickets | account_id | accounts | 0 |

**Result:** 4 out of 4 foreign key checks passed. No orphan records were found.

### 4.4 Additional Data Quality Checks

| Validation | Result |
|---|---:|
| Subscription end date earlier than start date | 0 |
| Ticket closed before submission | 0 |
| Churn event before account signup | 0 |
| MRR/ARR mismatches under tested ARR = MRR × 12 rule | 0 |
| Exact duplicate rows in source audit | 0 |

### 4.5 Missing Values Identified

| Dataset | Column | Missing Values | Percentage |
|---|---|---:|---:|
| Churn Events | feedback_text | 148 | 24.67% |
| Subscriptions | end_date | 4,514 | 90.28% |
| Support Tickets | satisfaction_score | 825 | 41.25% |
| **Total** | | **5,487** | |

Missing values have not been automatically replaced.

Important interpretation notes:

- Missing subscription end dates may represent ongoing subscriptions. This requires confirmation before using the field in churn or active-subscription calculations.
- Missing churn feedback should remain NULL unless a documented business rule says otherwise.
- Missing support satisfaction scores should not be replaced with an assumed score.

---

## 5. Week 1 Deliverables

| Deliverable | Status |
|---|---|
| GitHub repository and folder structure | Completed |
| `.gitignore` and requirements setup | Completed |
| Dataset inventory and audit outputs | Completed |
| Cleaning decision log | Prepared |
| Data dictionary | Prepared |
| Supabase database tables | Created |
| Five dataset loads | Completed |
| Primary key validation | Passed |
| Foreign key validation | Passed |
| Database load log | Updated |
| Individual dataset validation reports | Prepared |
| Initial exploration SQL | Prepared |
| Week 1 summary | Prepared |
| Week 2 handover | Prepared |
| README update | Prepared |

---

## 6. Important Outstanding Items

The following items must be carried into Week 2 or completed before final analytical sign-off:

1. Execute `sql/03_initial_exploration.sql` in Supabase and record the actual query results.
2. Review the cleaning decision log and data dictionary with the team.
3. Confirm the business meaning of NULL subscription end dates.
4. Define the active-subscription rule before calculating MRR.
5. Define how monthly and annual billing frequencies will be normalized.
6. Define churn, reactivation, upgrade, and downgrade calculation rules.
7. Confirm that the analytical SQL uses the correct date and subscription logic.

---

## 7. Week 1 Final Status

Week 1 established the project repository, dataset documentation, Supabase database, five loaded tables, and core relational constraints.

**Database loading:** 5 of 5 datasets loaded successfully.  
**Rows loaded:** 33,100.  
**Primary key validation:** 5 of 5 passed.  
**Foreign key validation:** 4 of 4 passed.  
**Orphan records:** 0.

The database foundation is ready for initial exploration and analytical development. Business-rule validation and execution of the initial exploration SQL remain important next steps.

---

**Prepared by:** Jaykishan  
**Project:** SaaS Revenue & Subscription Analytics