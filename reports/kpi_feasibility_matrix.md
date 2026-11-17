
# KPI Feasibility Matrix — Week 1

## 1. Purpose

This matrix evaluates whether the five RavenStack datasets contain the fields required to calculate initial SaaS business KPIs.

Classification:
- Supported: Required source fields exist and a defensible calculation is available for the stated scope.
- Partially Supported: Fields exist, but reporting periods, denominators, lifecycle rules or other assumptions need confirmation.
- Not Supported: Required source information is unavailable.

## 2. KPI Feasibility

| KPI | Required fields | Available evidence | Status | Caveats |
|---|---|---|---|---|
| Total accounts | accounts.account_id | 500 unique accounts | Supported | Source count |
| Total subscriptions | subscriptions.subscription_id | 5,000 unique IDs | Supported | Source count |
| MRR | subscriptions.mrr_amount | Sum = 11,338,747 | Partially Supported | Current-period population not established |
| ARR | subscriptions.arr_amount | Sum = 136,064,964 | Partially Supported | Snapshot semantics need confirmation |
| ARR consistency | mrr_amount, arr_amount | ARR = MRR × 12 in 5,000 rows | Supported | Source-level validation |
| Average revenue per account | mrr_amount, account_id | Both fields available | Partially Supported | Period and eligible population required |
| Customer churn rate | churn_flag, churn_date, account_id | Account flags and churn events available | Partially Supported | Cohort denominator and event rules required |
| Subscription churn rate | churn_flag, start_date, end_date | Subscription lifecycle fields available | Partially Supported | 4,514 missing end dates |
| Upgrade count | upgrade_flag | 529 TRUE subscription rows | Supported | Source-record count only |
| Downgrade count | downgrade_flag | 218 TRUE subscription rows | Supported | Source-record count only |
| Trial conversion rate | is_trial and conversion dates | Trial flags available | Not Supported | Conversion timestamps unavailable |
| Reactivation count | is_reactivation | 61 TRUE events | Supported | Event count only |
| Churn reasons | reason_code | Six observed categories | Supported | Unknown category retained |
| Refund amount | refund_amount_usd | Numeric field available | Supported | Not equivalent to recurring revenue loss |
| Feature usage total | usage_count | Sum = 250,525 | Supported | Preserve all records |
| Feature adoption | subscription_id, feature_name | 4,967 distinct subscriptions and 40 features | Partially Supported | Eligible population and period required |
| Feature error rate | error_count, usage_count | Both numeric fields available | Partially Supported | Denominator semantics need confirmation |
| Usage duration | usage_duration_secs | Sum = 76,055,072 seconds | Supported | Recorded duration total |
| Average resolution time | resolution_time_hours | Average = 35.86 hours | Supported | Source-level average |
| Average first response time | first_response_time_minutes | Average = 88.48 minutes | Supported | Source-level average |
| Escalation rate | escalation_flag | 95 of 2,000 tickets escalated | Supported | Source-level rate |
| Average satisfaction | satisfaction_score | 1,175 observed responses; average 3.98 | Partially Supported | 825 missing scores |

## 3. Evidence and Data Quality Caveats

### Accounts
- 500 records.
- account_id is unique.
- All 500 accounts have subscription references.
- 492 accounts have support ticket references.
- 352 accounts have churn event references.

### Subscriptions
- 5,000 records.
- subscription_id is unique.
- 4,514 end_date values are missing.
- 486 records have churn_flag = TRUE.
- ARR equals MRR multiplied by 12 in all records.

### Churn Events
- 600 records.
- churn_event_id is unique.
- 148 feedback_text values are missing.
- 61 events are marked as reactivations.

### Feature Usage
- 25,000 records.
- 24,979 distinct usage IDs.
- 21 usage IDs are repeated, involving 42 records.
- All 25,000 subscription references matched.
- Do not use usage_id as a primary key without further investigation.

### Support Tickets
- 2,000 records.
- 2,000 unique ticket IDs.
- 825 satisfaction scores are missing.
- Average satisfaction among recorded responses is 3.98.
- All 2,000 account references matched.

## 4. Overall Assessment

The source datasets support basic account, subscription, churn-event, feature-usage and support-ticket exploration.

Recurring revenue metrics, period-based churn rates, trial conversion and retention require additional business definitions or historical lifecycle evidence.

The current matrix is a Week 1 feasibility assessment, not a claim that all KPIs have been implemented or approved for production reporting.

## 5. Recommended Week 2 Actions

1. Confirm subscription snapshot and current-period revenue definitions.
2. Agree on customer and subscription churn denominators.
3. Investigate the 21 repeated Feature Usage IDs.
4. Confirm whether missing subscription end dates represent active subscriptions.
5. Define trial conversion and reactivation measurement rules.
6. Document satisfaction-score coverage in dashboards and reports.
7. Validate SQL and Python KPI totals against the same reporting population.
