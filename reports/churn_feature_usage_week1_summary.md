# Churn Events & Feature Usage — Week 1 Summary

## 1. Overview

This document summarizes the Week 1 audit, database loading, and validation of the Churn Events and Feature Usage datasets.

These datasets help understand why customers leave, how customers return, and how they interact with the SaaS product.

---

# Part A — Churn Events

## 2. Dataset Overview

**Source File:** `ravenstack_churn_events.csv`  
**Database Table:** `churn_events`  
**Primary Key:** `churn_event_id`  
**Total Records:** 600  
**Total Columns:** 9

### Columns

| Column | Description |
|---|---|
| churn_event_id | Unique churn event identifier |
| account_id | Related customer account |
| churn_date | Date of churn event |
| reason_code | Recorded reason for churn |
| refund_amount_usd | Refund amount in USD |
| preceding_upgrade_flag | Indicates an upgrade before the event |
| preceding_downgrade_flag | Indicates a downgrade before the event |
| is_reactivation | Indicates whether the event represents a reactivation |
| feedback_text | Customer feedback associated with the event |

## 3. Data Quality Review

| Validation | Result |
|---|---:|
| Total records | 600 |
| Total columns | 9 |
| Missing feedback_text | 148 |
| Missing feedback percentage | 24.67% |
| Exact duplicate rows | 0 |
| Unique churn_event_id values | 600 |
| Duplicate primary key values | 0 |
| Observed minimum refund | $0.00 |
| Observed maximum refund | $392.92 |
| Churn events before account signup | 0 |

Missing feedback values are retained as NULL. They should not be replaced with assumed customer feedback.

## 4. Database Loading and Relationships

The `churn_events` table was successfully loaded into Supabase PostgreSQL.

| Validation | Result |
|---|---|
| Database rows | 600 |
| Primary key | `churn_event_id` |
| Primary key duplicates | 0 |
| Foreign key | `account_id` |
| Referenced table | `accounts` |
| Orphan account references | 0 |

**Relationship:** Each churn event belongs to an account through `account_id`.

## 5. Analytical Importance

The Churn Events dataset will support:

- Churn reason analysis.
- Refund analysis.
- Customer churn trend analysis.
- Reactivation analysis.
- Upgrade and downgrade activity before churn.
- Customer feedback analysis.

A churn event must not automatically be treated as one permanently churned customer. Reactivations and repeated events must be considered when defining customer churn.

---

# Part B — Feature Usage

## 6. Dataset Overview

**Source File:** `ravenstack_feature_usage.csv`  
**Database Table:** `feature_usage`  
**Database Primary Key:** `usage_record_id`  
**Total Records:** 25,000  
**Total Columns:** 8

### Columns

| Column | Description |
|---|---|
| usage_id | Source record identifier |
| subscription_id | Related subscription identifier |
| usage_date | Date of product usage |
| feature_name | Name of the feature used |
| usage_count | Number of recorded uses |
| usage_duration_secs | Usage duration in seconds |
| error_count | Number of recorded errors |
| is_beta_feature | Indicates whether the feature is in beta |

## 7. Data Quality Review

| Validation | Result |
|---|---:|
| Total records | 25,000 |
| Total columns | 8 |
| Missing values | 0 |
| Exact duplicate rows | 0 |
| Unique source usage_id values | 24,979 |
| Repeated source ID excess | 21 |
| Observed usage_count range | 0–26 |
| Observed error_count range | 0–8 |

### Primary Key Decision

The source `usage_id` contains repeated values, so it is not suitable as a unique primary key for all 25,000 rows.

The database uses:

`usage_record_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY`

The original `usage_id` remains in the table as a source identifier.

## 8. Database Loading and Relationships

The `feature_usage` table was successfully loaded into Supabase PostgreSQL.

| Validation | Result |
|---|---|
| Database rows | 25,000 |
| Primary key | `usage_record_id` |
| Primary key duplicates | 0 |
| Foreign key | `subscription_id` |
| Referenced table | `subscriptions` |
| Orphan subscription references | 0 |

**Relationship:** Each feature usage record references a subscription through `subscription_id`.

## 9. Analytical Importance

The Feature Usage dataset will support:

- Feature adoption analysis.
- Usage frequency analysis.
- Feature popularity comparisons.
- Beta feature usage analysis.
- Usage duration analysis.
- Product engagement analysis.
- Error frequency analysis.

---

## 10. Week 1 Completion Status

| Task | Churn Events | Feature Usage |
|---|---|---|
| Dataset audit | Completed | Completed |
| Missing-value review | Completed | Completed |
| Identifier review | Completed | Completed |
| Supabase table creation | Completed | Completed |
| Data loading | Completed | Completed |
| Primary key validation | Passed | Passed |
| Foreign key validation | Passed | Passed |
| Week 1 summary | Prepared | Prepared |

---

## 11. Week 2 Recommendations

### Churn Events

1. Analyze churn reasons and their frequency.
2. Analyze refunds by churn reason.
3. Examine customer reactivation patterns.
4. Compare churn activity across plan tiers.
5. Explore customer feedback where available.

### Feature Usage

1. Rank features by total usage.
2. Compare usage across subscription plans.
3. Analyze feature usage trends over time.
4. Compare beta and non-beta feature adoption.
5. Investigate feature error rates.
6. Explore usage patterns associated with churn, using an appropriate account/subscription-level analysis.

---

**Dataset Owner:** Madhupriya  
**Final Review and Documentation Coordination:** Jaykishan  
**Project:** SaaS Revenue & Subscription Analytics  
**Status:** Week 1 dataset review documented