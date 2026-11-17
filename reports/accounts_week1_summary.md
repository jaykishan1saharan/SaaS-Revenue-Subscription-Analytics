# Accounts — Week 1 Summary

## 1. Dataset Overview

**Dataset:** `ravenstack_accounts.csv`  
**Database Table:** `accounts`  
**Primary Key:** `account_id`  
**Total Records:** 500  
**Total Columns:** 10

The Accounts dataset contains customer-level information used to understand the SaaS customer base, including account details, industry, country, signup date, referral source, plan tier, seats, trial status, and churn status.

---

## 2. Columns

| Column | Description |
|---|---|
| account_id | Unique account identifier |
| account_name | Customer or organization name |
| industry | Customer industry |
| country | Customer country |
| signup_date | Account registration date |
| referral_source | Source through which the customer was acquired |
| plan_tier | Customer's plan category |
| seats | Number of seats associated with the account |
| is_trial | Indicates whether the account is a trial account |
| churn_flag | Indicates the account's churn status |

---

## 3. Data Quality Review

| Validation | Result |
|---|---:|
| Total records | 500 |
| Total columns | 10 |
| Missing values | 0 |
| Exact duplicate rows | 0 |
| Unique account IDs | 500 |
| Duplicate account IDs | 0 |
| Observed minimum seats | 1 |
| Observed maximum seats | 163 |

**Result:** The Accounts dataset passed the reported initial data-quality checks.

The seat values above represent observed dataset ranges, not independently confirmed business limits.

---

## 4. Database Loading and Validation

The `accounts` table was successfully created and loaded into Supabase PostgreSQL.

| Validation | Result |
|---|---|
| Database rows | 500 |
| Primary key | `account_id` |
| Primary key duplicates | 0 |
| Referenced by subscriptions | No orphan relationships |
| Referenced by churn_events | No orphan relationships |
| Referenced by support_tickets | No orphan relationships |

The following relationships were verified:

- `subscriptions.account_id` references `accounts.account_id`.
- `churn_events.account_id` references `accounts.account_id`.
- `support_tickets.account_id` references `accounts.account_id`.

All reported foreign key orphan checks returned zero.

---

## 5. Analytical Importance

The Accounts table will be used for:

- Customer segmentation by industry and country.
- Account distribution by plan tier.
- Trial versus non-trial account analysis.
- Customer acquisition source analysis.
- Customer churn analysis.
- Joining customer information with subscriptions, churn events, and support tickets.

---

## 6. Week 1 Completion Status

| Task | Status |
|---|---|
| Dataset inspection | Completed |
| Data-quality audit | Completed |
| Primary key identification | Completed |
| Supabase table creation | Completed |
| Data loading | Completed |
| Primary key validation | Passed |
| Foreign key validation | Passed |
| Week 1 summary documentation | Prepared |

---

## 7. Week 2 Recommendations

The Accounts dataset can support the following analysis:

1. Customer distribution by country and industry.
2. Customer distribution by plan tier.
3. Trial conversion analysis, subject to an agreed definition.
4. Churn rate by industry and plan tier.
5. Account segmentation by seat count.
6. Customer acquisition source analysis.

---

**Dataset Owner:** Yash  
**Final Review and Documentation Coordination:** Jaykishan  
**Project:** SaaS Revenue & Subscription Analytics  
**Status:** Week 1 dataset review documented