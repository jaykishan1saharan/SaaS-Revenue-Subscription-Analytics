
# Metric Definitions — SaaS Revenue & Subscription Analytics

## 1. Purpose

This document defines initial business metrics, calculation logic, source fields and limitations for the RavenStack datasets.

## 2. Revenue Metrics

### Monthly Recurring Revenue (MRR)

- Definition: Sum of monthly recurring revenue values for the selected subscription population.
- Formula: SUM(mrr_amount)
- Source: subscriptions.mrr_amount
- Status: Partially supported.
- Caveat: The source contains 5,000 subscription records. A current-period subscription snapshot and historical revenue methodology must be confirmed before reporting current MRR.

### Annual Recurring Revenue (ARR)

- Definition: Annualized recurring revenue.
- Formula: SUM(arr_amount)
- Source: subscriptions.arr_amount
- Validation: ARR equals MRR multiplied by 12 in all 5,000 rows.
- Status: Partially supported.
- Caveat: Annualized source amounts are available, but current-period and historical snapshot semantics require confirmation.

### Average Revenue per Account

- Formula: Selected-period recurring revenue / eligible distinct accounts.
- Sources: subscriptions.mrr_amount, subscriptions.account_id.
- Status: Partially supported.
- Caveat: Requires an agreed reporting population and period.

## 3. Customer and Subscription Metrics

### Customer Count

- Formula: COUNT(DISTINCT account_id)
- Source: accounts.account_id
- Status: Supported.
- Observed accounts: 500.

### Subscription Count

- Formula: COUNT(DISTINCT subscription_id)
- Source: subscriptions.subscription_id
- Status: Supported.
- Observed subscriptions: 5,000.

### Customer Churn

- Definition: Customers lost during a defined reporting period divided by eligible customers at the beginning of that period.
- Potential fields: accounts.churn_flag, subscriptions.churn_flag, churn_events.churn_date.
- Status: Partially supported.
- Caveat: A period-based calculation requires a confirmed definition of customer loss, beginning-of-period population and treatment of reactivation.

### Subscription Churn

- Definition: Subscriptions terminated during a reporting period divided by subscriptions eligible at the beginning of the period.
- Potential fields: subscriptions.churn_flag, start_date, end_date.
- Status: Partially supported.
- Caveat: Missing end dates and lifecycle semantics require review.

### Upgrade and Downgrade Counts

- Formula: Count records with upgrade_flag = TRUE or downgrade_flag = TRUE.
- Sources: subscriptions.upgrade_flag, subscriptions.downgrade_flag.
- Status: Supported for source-record counts.
- Caveat: These flags do not establish the exact timing or monetary impact of each plan change.

### Trial Conversion Rate

- Definition: Trial accounts that become paid accounts divided by eligible trial accounts.
- Potential fields: accounts.is_trial, subscriptions.is_trial.
- Status: Not supported reliably.
- Caveat: Trial start, trial end and conversion timestamps are not available.

### Reactivation Count

- Formula: Count churn events where is_reactivation = TRUE.
- Source: churn_events.is_reactivation.
- Status: Supported as an event count.
- Caveat: Reactivation rate requires an agreed denominator and reporting period.

## 4. Feature Usage Metrics

### Total Feature Usage

- Formula: SUM(usage_count)
- Source: feature_usage.usage_count
- Status: Supported.
- Observed total: 250,525.

### Feature Adoption

- Definition: Distinct eligible subscriptions using a feature divided by eligible subscriptions.
- Sources: feature_usage.subscription_id, feature_usage.feature_name, subscriptions.subscription_id.
- Status: Partially supported.
- Caveat: Eligible subscription population and reporting period must be defined.

### Feature Error Rate

- Suggested formula: SUM(error_count) / SUM(usage_count)
- Sources: feature_usage.error_count, feature_usage.usage_count.
- Status: Partially supported.
- Caveat: Confirm that usage_count represents the denominator of error opportunities.

### Feature Usage Duration

- Formula: SUM(usage_duration_secs)
- Source: feature_usage.usage_duration_secs
- Status: Supported as a recorded duration total.
- Caveat: The 21 repeated usage IDs must not be removed without evidence of duplicate events.

## 5. Support Metrics

### Average Resolution Time

- Formula: AVG(resolution_time_hours)
- Source: support_tickets.resolution_time_hours
- Status: Supported.
- Observed average: 35.86 hours.

### Average First Response Time

- Formula: AVG(first_response_time_minutes)
- Source: support_tickets.first_response_time_minutes
- Status: Supported.
- Observed average: 88.48 minutes.

### Escalation Rate

- Formula: Escalated tickets / Total tickets × 100
- Source: support_tickets.escalation_flag
- Status: Supported.
- Observed escalated tickets: 95 out of 2,000.

### Average Customer Satisfaction

- Formula: AVG(satisfaction_score)
- Source: support_tickets.satisfaction_score
- Status: Partially supported.
- Observed average: 3.98.
- Caveat: 825 of 2,000 tickets have missing scores.

## 6. Financial and Churn Event Metrics

### Churn Refund Amount

- Formula: SUM(refund_amount_usd)
- Source: churn_events.refund_amount_usd
- Status: Supported as a recorded refund amount.
- Caveat: Refunds must not automatically be treated as recurring revenue loss.

### Churn Reasons

- Formula: COUNT(*) grouped by reason_code.
- Source: churn_events.reason_code
- Status: Supported as event counts.
- Caveat: Unknown reasons should remain a distinct category.

## 7. Reporting Rules

1. Define reporting periods explicitly.
2. Use distinct identifiers where counting entities.
3. Avoid double-counting subscription history.
4. Keep missing satisfaction scores as NULL.
5. Distinguish churn events from churned customers.
6. Distinguish MRR/ARR from collected cash revenue.
7. Record assumptions whenever a denominator or time window is required.
