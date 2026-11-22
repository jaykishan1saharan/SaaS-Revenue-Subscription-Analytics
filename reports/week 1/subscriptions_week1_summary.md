# Subscriptions — Week 1 Summary

## 1. Dataset Overview

**Source File:** `ravenstack_subscriptions.csv`  
**Database Table:** `subscriptions`  
**Primary Key:** `subscription_id`  
**Total Records:** 5,000  
**Total Columns:** 14

The Subscriptions dataset contains subscription-level information, including customer relationships, plan tiers, subscription dates, seats, recurring revenue, billing frequency, and subscription status flags.

---

## 2. Columns

| Column | Description |
|---|---|
| subscription_id | Unique subscription identifier |
| account_id | Related customer account |
| start_date | Subscription start date |
| end_date | Subscription end date, when available |
| plan_tier | Subscription plan category |
| seats | Number of seats in the subscription |
| mrr_amount | Monthly recurring revenue amount |
| arr_amount | Annual recurring revenue amount |
| is_trial | Indicates whether the subscription is a trial |
| upgrade_flag | Indicates an upgrade |
| downgrade_flag | Indicates a downgrade |
| churn_flag | Indicates churn status |
| billing_frequency | Billing interval |
| auto_renew_flag | Indicates automatic renewal status |

---

## 3. Data Quality Review

| Validation | Result |
|---|---:|
| Total records | 5,000 |
| Total columns | 14 |
| Missing end_date values | 4,514 |
| Missing end_date percentage | 90.28% |
| Exact duplicate rows | 0 |
| Unique subscription_id values | 5,000 |
| Duplicate subscription IDs | 0 |
| Observed minimum seats | 1 |
| Observed maximum seats | 189 |
| Observed minimum MRR | $0 |
| Observed maximum MRR | $33,830 |
| Observed minimum ARR | $0 |
| Observed maximum ARR | $405,960 |

The observed ranges are descriptive dataset statistics, not independently approved business limits.

---

## 4. Missing End Date Analysis

A large proportion of subscription records have NULL `end_date` values.

| churn_flag | is_trial | Total Records | Missing end_date |
|---|---|---:|---:|
| false | false | 3,814 | 3,814 |
| false | true | 700 | 700 |
| true | false | 408 | 0 |
| true | true | 78 | 0 |
| **Total** | | **5,000** | **4,514** |

### Important Interpretation

Missing end dates may indicate ongoing subscriptions, but this interpretation must be confirmed as a business rule.

For now:

- Preserve NULL end dates.
- Do not replace them with the current date.
- Do not assume a NULL end date automatically means an active subscription.
- Consider `churn_flag`, `is_trial`, start date, end date, and the reporting date when defining subscription status.

---

## 5. Revenue Validation

The dataset contains both `mrr_amount` and `arr_amount`.

A validation was performed using the tested relationship:

`ARR = MRR × 12`

| Validation | Result |
|---|---:|
| Total subscriptions checked | 5,000 |
| MRR/ARR mismatches | 0 |

This confirms consistency under the tested formula. It does not by itself establish the final business treatment of annual billing, discounts, refunds, or active subscription status.

---

## 6. Database Loading and Relationships

The `subscriptions` table was successfully loaded into Supabase PostgreSQL.

| Validation | Result |
|---|---|
| Database rows | 5,000 |
| Primary key | `subscription_id` |
| Primary key duplicates | 0 |
| Foreign key | `account_id` |
| Referenced table | `accounts` |
| Orphan account references | 0 |
| End date earlier than start date | 0 |

**Relationship:** Each subscription belongs to an account through `account_id`.

---

## 7. Analytical Importance

The Subscriptions table is the primary source for:

- Monthly Recurring Revenue (MRR).
- Annual Recurring Revenue (ARR).
- Subscription plan analysis.
- Billing frequency analysis.
- Customer subscription history.
- Upgrade and downgrade analysis.
- Trial subscription analysis.
- Subscription churn analysis.

---

## 8. Week 1 Completion Status

| Task | Status |
|---|---|
| Dataset inspection | Completed |
| Data-quality audit | Completed |
| Missing-value review | Completed |
| Primary key identification | Completed |
| Supabase table creation | Completed |
| Data loading | Completed |
| Primary key validation | Passed |
| Foreign key validation | Passed |
| MRR/ARR consistency check | Passed under tested rule |
| Week 1 summary documentation | Prepared |

---

## 9. Week 2 Recommendations

1. Define the active subscription rule.
2. Confirm how annual and monthly billing should be normalized.
3. Calculate MRR using an agreed reporting-date definition.
4. Analyze ARR by plan tier.
5. Analyze subscription growth and historical trends.
6. Analyze upgrades and downgrades.
7. Analyze trial versus paid subscriptions.
8. Develop customer and revenue churn metrics.
9. Review subscription status using documented business rules.

---

**Dataset Owner:** Meghana  
**Final Review and Documentation Coordination:** Jaykishan  
**Project:** SaaS Revenue & Subscription Analytics  
**Status:** Week 1 dataset review documented