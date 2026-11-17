# Data Dictionary
## SaaS Revenue & Subscription Analytics

**Project:** SaaS Revenue & Subscription Analytics  
**Dataset:** RavenStack  
**Prepared by:** Jaykishan  
**Phase:** Day 3 – Schema Design  
**Status:** Draft – Pending Team Validation

---

## 1. Purpose

This data dictionary documents the columns, descriptions, proposed PostgreSQL data types, nullability and key relationships of the five RavenStack datasets.

It will be used as a common reference for:
- Data cleaning
- Database schema creation
- SQL analysis
- KPI development
- Power BI dashboard development

---

## 2. Dataset Overview

| Table | Source File | Rows | Columns |
|---|---|---:|---:|
| accounts | ravenstack_accounts.csv | 500 | 10 |
| churn_events | ravenstack_churn_events.csv | 600 | 9 |
| feature_usage | ravenstack_feature_usage.csv | 25,000 | 8 |
| subscriptions | ravenstack_subscriptions.csv | 5,000 | 14 |
| support_tickets | ravenstack_support_tickets.csv | 2,000 | 9 |

Total: 33,100 rows and 50 columns.

---

## 3. Accounts

**Source:** `ravenstack_accounts.csv`

| Column Name | Proposed PostgreSQL Type | Nullable? | Description | Key |
|---|---|---|---|---|
| account_id | VARCHAR(50) | No | Unique identifier of an account | PK |
| account_name | TEXT | No | Name of the customer account | |
| industry | TEXT | No | Industry associated with the account | |
| country | TEXT | No | Country associated with the account | |
| signup_date | DATE | No | Date the account registered | |
| referral_source | TEXT | No | Source through which the account was acquired | |
| plan_tier | TEXT | No | Plan tier associated with the account | |
| seats | INTEGER | No | Number of seats associated with the account | |
| is_trial | BOOLEAN | No | Indicates whether the account is on a trial | |
| churn_flag | BOOLEAN | No | Indicates the account-level churn status | |

**Candidate primary key:** `account_id`

---

## 4. Churn Events

**Source:** `ravenstack_churn_events.csv`

| Column Name | Proposed PostgreSQL Type | Nullable? | Description | Key |
|---|---|---|---|---|
| churn_event_id | VARCHAR(50) | No | Unique identifier of a churn event | PK |
| account_id | VARCHAR(50) | No | Account associated with the churn event | FK |
| churn_date | DATE | No | Date of the churn event | |
| reason_code | TEXT | No | Coded reason for churn | |
| refund_amount_usd | NUMERIC(12,2) | No | Refund amount in USD | |
| preceding_upgrade_flag | BOOLEAN | No | Indicates an upgrade before the churn event | |
| preceding_downgrade_flag | BOOLEAN | No | Indicates a downgrade before the churn event | |
| is_reactivation | BOOLEAN | No | Indicates whether the event is associated with reactivation | |
| feedback_text | TEXT | Yes | Customer feedback associated with churn | |

**Primary key:** `churn_event_id`

**Foreign key:** `account_id` references `accounts(account_id)`.

---

## 5. Feature Usage

**Source:** `ravenstack_feature_usage.csv`

| Column Name | Proposed PostgreSQL Type | Nullable? | Description | Key |
|---|---|---|---|---|
| usage_id | VARCHAR(50) | No | Source identifier of a feature usage record | Under review |
| subscription_id | VARCHAR(50) | No | Subscription associated with the usage record | FK |
| usage_date | DATE | No | Date of feature usage | |
| feature_name | TEXT | No | Name of the feature used | |
| usage_count | INTEGER | No | Number of feature usage actions | |
| usage_duration_secs | INTEGER | No | Duration of usage in seconds | |
| error_count | INTEGER | No | Number of errors recorded during usage | |
| is_beta_feature | BOOLEAN | No | Indicates whether the feature is a beta feature | |

**Identifier warning:**

`usage_id` has 21 repeated values affecting 42 rows. It must not be declared as a primary key until the issue is resolved.

A database-generated surrogate key may be considered for uniquely identifying imported rows. The source `usage_id` should still be retained for traceability.

**Foreign key:** `subscription_id` references `subscriptions(subscription_id)`.

---

## 6. Subscriptions

**Source:** `ravenstack_subscriptions.csv`

| Column Name | Proposed PostgreSQL Type | Nullable? | Description | Key |
|---|---|---|---|---|
| subscription_id | VARCHAR(50) | No | Unique identifier of a subscription | PK |
| account_id | VARCHAR(50) | No | Account associated with the subscription | FK |
| start_date | DATE | No | Subscription start date | |
| end_date | DATE | Yes | Subscription end date; missing values require business interpretation | |
| plan_tier | TEXT | No | Subscription plan tier | |
| seats | INTEGER | No | Number of seats in the subscription | |
| mrr_amount | NUMERIC(12,2) | No | Monthly recurring revenue amount | |
| arr_amount | NUMERIC(12,2) | No | Annual recurring revenue amount | |
| is_trial | BOOLEAN | No | Indicates whether the subscription is a trial | |
| upgrade_flag | BOOLEAN | No | Indicates an upgrade | |
| downgrade_flag | BOOLEAN | No | Indicates a downgrade | |
| churn_flag | BOOLEAN | No | Indicates subscription churn status | |
| billing_frequency | TEXT | No | Subscription billing frequency | |
| auto_renew_flag | BOOLEAN | No | Indicates whether automatic renewal is enabled | |

**Primary key:** `subscription_id`

**Foreign key:** `account_id` references `accounts(account_id)`.

**Important:** The 4,514 missing `end_date` values must remain NULL until the business meaning is confirmed.

---

## 7. Support Tickets

**Source:** `ravenstack_support_tickets.csv`

| Column Name | Proposed PostgreSQL Type | Nullable? | Description | Key |
|---|---|---|---|---|
| ticket_id | VARCHAR(50) | No | Unique identifier of a support ticket | PK |
| account_id | VARCHAR(50) | No | Account associated with the support ticket | FK |
| submitted_at | TIMESTAMP | No | Date and time when the ticket was submitted | |
| closed_at | TIMESTAMP | No | Date and time when the ticket was closed | |
| resolution_time_hours | NUMERIC(10,2) | No | Time taken to resolve the ticket in hours | |
| priority | TEXT | No | Priority assigned to the support ticket | |
| first_response_time_minutes | NUMERIC(10,2) | No | Time taken for the first response in minutes | |
| satisfaction_score | INTEGER | Yes | Customer satisfaction rating | |
| escalation_flag | BOOLEAN | No | Indicates whether the ticket was escalated | |

**Primary key:** `ticket_id`

**Foreign key:** `account_id` references `accounts(account_id)`.

**Note:** `closed_at` nullability must be revisited if the team confirms that unresolved tickets can exist. The initial audit showed no missing cells in this column.

---

## 8. Proposed Table Relationships

| Parent Table | Parent Column | Child Table | Child Column | Relationship |
|---|---|---|---|---|
| accounts | account_id | subscriptions | account_id | One-to-Many |
| accounts | account_id | churn_events | account_id | One-to-Many |
| accounts | account_id | support_tickets | account_id | One-to-Many |
| subscriptions | subscription_id | feature_usage | subscription_id | One-to-Many |

All four reference checks returned zero unmatched references during the Day 2 audit.

These relationships are proposed for the database schema and should be confirmed during final ERD review.

---

## 9. PostgreSQL Naming and Data Type Standards

| Standard | Convention |
|---|---|
| Table names | lowercase snake_case |
| Column names | lowercase snake_case |
| Primary keys | Explicitly named primary key constraints |
| Foreign keys | Explicitly named foreign key constraints |
| Date-only values | DATE |
| Date and time values | TIMESTAMP |
| Boolean values | BOOLEAN |
| Whole numbers | INTEGER |
| Monetary values | NUMERIC(12,2) |
| Descriptive text | TEXT |
| Missing values | NULL where permitted |

Use NUMERIC for financial values rather than FLOAT to avoid floating-point precision issues.

Use TIMESTAMP only for fields containing date and time information.

---

## 10. Important Database Rules

1. Preserve all source identifiers.
2. Do not create a primary key using a column that contains repeated values.
3. Validate uniqueness before applying primary key constraints.
4. Validate references before applying foreign key constraints.
5. Allow NULL only where the data and business rules permit it.
6. Do not replace missing values with arbitrary defaults.
7. Do not assume that account-level and subscription-level churn flags have identical meanings.
8. Keep the raw CSV files unchanged.
9. Maintain traceability between raw and cleaned records.
10. Revisit proposed types if source-value validation reveals a mismatch.

---

## 11. Validation Status

| Validation Item | Status |
|---|---|
| Accounts primary key uniqueness | Passed |
| Churn events primary key uniqueness | Passed |
| Subscriptions primary key uniqueness | Passed |
| Support tickets primary key uniqueness | Passed |
| Feature usage source ID uniqueness | Failed – investigation required |
| Account foreign key references | Passed |
| Subscription foreign key references | Passed |
| Missing-value interpretation | Pending business review |
| MRR/ARR consistency | Pending validation |
| Support ticket timestamp chronology | Pending validation |
| Final PostgreSQL schema approval | Pending |

---

## 12. Final Note

This data dictionary is a proposed schema reference, not the final database implementation.

The data types, nullability and relationships must be checked against the actual source values and approved business rules before creating final PostgreSQL constraints.