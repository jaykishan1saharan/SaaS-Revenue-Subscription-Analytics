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


---

# Week 2 Addendum — Revenue, Subscription Movements and Churn

**Documentation owner:** Jaykishan  
**Status:** Working definition for team review. Approval rows remain pending until reviewers confirm the rules.  
**Source basis:** RavenStack Week 1 data dictionaries, handover, cleaning decision log and KPI feasibility matrix.

## 8. Reporting calendar and period boundaries

### 8.1 Reporting month

Use calendar months for the Week 2 monthly KPI series.

- `period_start`: first calendar day of the month, inclusive.
- `period_end_exclusive`: first calendar day of the following month, exclusive.
- `snapshot_date`: final calendar day of the reporting month.
- Date fields are stored/documented as `DATE`; do not invent a timezone or convert these date values to UTC.
- Event inclusion uses `event_date >= period_start AND event_date < period_end_exclusive`.

Example: November 2024 covers `[2024-11-01, 2024-12-01)` and its month-end snapshot date is `2024-11-30`.

The source coverage supports dates through 2024-12-31 for accounts, subscriptions and churn events. The reporting-month series must be limited to the valid source coverage and the population actually observable under the lifecycle rules.

### 8.2 Point-in-time vs event-based analysis

- **Snapshot:** evaluate which subscriptions are active as of a specific month-end date, then aggregate their recurring revenue.
- **Event-based:** evaluate records whose event dates fall within a reporting month, such as `churn_events.churn_date`.
- A monthly event count is not a month-end subscription count. Do not substitute one for the other.

## 9. Metric grain and denominator policy

| Metric | Grain | Denominator / population |
|---|---|---|
| Active subscription snapshot | `report_month × subscription_id` | Subscription records meeting approved active rule on snapshot date |
| MRR | `report_month × subscription_id`, then sum | Eligible active subscription MRR |
| Plan MRR | `report_month × plan_tier` | Same eligible subscription population |
| Customer count | `report_month × account_id` distinct | Accounts with at least one eligible subscription |
| Customer churn | `report_month × account_id` distinct | Eligible distinct accounts active at the opening snapshot |
| Churn events | `churn_event_id` | Event records; never a customer denominator |
| MRR movements | Account/subscription bridge between consecutive snapshots | Comparable opening and closing populations |

An account may have multiple subscription rows. Sum eligible subscription MRR at subscription grain; count customers using distinct `account_id`. One subscription ending does not prove customer churn if another subscription for that account remains active.

### Opening denominator convention

For a calendar month, the opening customer population is the distinct eligible account population at the immediately preceding month-end snapshot. The current month lost-customer numerator must use the same customer-level definition. The first month in the available reporting range has no preceding month snapshot and should have a NULL/NA churn rate unless an agreed opening snapshot is available.

Trial treatment must be explicit. Recommended reporting split:
- `active_accounts_all`: accounts with at least one active subscription, including trial subscriptions.
- `active_paid_accounts`: accounts with at least one active non-trial subscription.
- Use `active_paid_accounts` as the default customer churn denominator for paid-customer churn; publish all-account churn separately only if requested and labelled.

This is a proposed analytical convention, pending team approval.

## 10. MRR definition and scope

### 10.1 MRR

**Definition:** Sum of the source `subscriptions.mrr_amount` for subscriptions included in the approved month-end active snapshot.

```text
MRR_t = SUM(mrr_amount_i)
        for subscriptions i active at month-end t
```

Source: `subscriptions.mrr_amount`, `subscription_id`, `account_id`, `start_date`, `end_date`, `churn_flag`, `is_trial`, `billing_frequency`, `plan_tier`.

The Week 1 feasibility matrix records source-wide `SUM(mrr_amount) = 11,338,747` and `SUM(arr_amount) = 136,064,964`. These are totals across all source subscription rows, not month-end MRR, and must not be presented as a monthly snapshot.

The subscription dictionary records:
- 5,000 subscription rows; 5,000 unique `subscription_id`.
- 2,539 `monthly` and 2,461 `annual` billing-frequency values.
- 778 trial subscriptions; all 778 have zero MRR and ARR.
- `arr_amount = 12 × mrr_amount` in all 5,000 rows.
- Currency/unit is not specified.
- No discount, tax, invoice or payment amount field is present.

### 10.2 Annual/monthly normalization

The source field is explicitly documented as `mrr_amount` (monthly recurring revenue), and every row has `arr_amount = 12 × mrr_amount`. Therefore the default implementation must use `mrr_amount` directly for both `monthly` and `annual` billing-frequency records. Do **not** divide annual-frequency rows by 12 again; that would double-normalize a field already named MRR.

Use `billing_frequency` as a validation/segmentation field. If source-owner review establishes that `mrr_amount` is not monthly-normalized, revise this rule with evidence and record the change.

### 10.3 Currency, seats, discounts and refunds

- Currency/unit for subscription MRR/ARR is unknown. Label outputs `source_amount` or `MRR (source units; currency unconfirmed)` until confirmed. Do not label as INR or USD.
- Do not multiply MRR by `seats`: the data dictionary describes `mrr_amount` as the monthly recurring revenue amount associated with the subscription and does not establish a per-seat price.
- No discount field is documented. Do not apply an inferred discount.
- `churn_events.refund_amount_usd` is a refund field and must remain separate from recurring MRR. Its `_usd` suffix suggests USD but the data dictionary still calls for source-owner validation.
- No supported one-time fee, tax, invoice, usage-charge or payment field is identified in the subscription table. Exclude unsupported non-recurring amounts from MRR.

## 11. Subscription lifecycle rule — working convention

The source has no `subscription_status` column. It has `start_date`, nullable `end_date`, `churn_flag`, `is_trial`, `auto_renew_flag` and plan/revenue attributes.

Observed:
- 4,514 records have NULL `end_date`; all have `churn_flag = FALSE`.
- 486 records have populated `end_date`; all have `churn_flag = TRUE`.
- The source dictionary does not say whether `end_date` is the last active day or first inactive day.

**Provisional candidate rule:** a subscription is eligible on snapshot date if `start_date <= snapshot_date`, `end_date IS NULL`, and `churn_flag = FALSE`, plus any additional approved handling for populated end dates. Do not finalize the populated-end-date comparison until the team confirms inclusivity. The two possible comparisons are:
- Inclusive end date (last active day): `end_date >= snapshot_date`.
- Exclusive end date (first inactive day): `end_date > snapshot_date`.

`auto_renew_flag = FALSE` alone is not churn. Preserve conflicting lifecycle evidence for QA.

## 12. Currency/unit label and output schema

Until currency is confirmed, the monthly KPI output must not use a currency symbol. Recommended schema for `data/processed/monthly_saas_kpis.csv`:

| Column | Type | Definition |
|---|---|---|
| `report_month` | DATE or YYYY-MM string | First day of reporting month |
| `snapshot_date` | DATE | Month-end as-of date |
| `active_subscriptions` | INTEGER | Count of eligible subscription IDs |
| `active_accounts_all` | INTEGER | Distinct accounts with any eligible subscription |
| `active_paid_accounts` | INTEGER | Distinct accounts with an eligible non-trial subscription |
| `mrr_source_amount` | NUMERIC | Sum of eligible `mrr_amount`; source currency/unit unconfirmed |
| `arr_source_amount` | NUMERIC | Sum of eligible `arr_amount`; source currency/unit unconfirmed |
| `basic_mrr_source_amount` | NUMERIC | Eligible Basic plan MRR |
| `pro_mrr_source_amount` | NUMERIC | Eligible Pro plan MRR |
| `enterprise_mrr_source_amount` | NUMERIC | Eligible Enterprise plan MRR |
| `source_currency` | TEXT | `unknown` until confirmed |
| `definition_version` | TEXT | Version/tag of approved business rules |

The detailed movement columns are added in the Day 8 reporting specification.

## 13. MRR example (illustrative arithmetic only)

If three subscriptions are eligible at a month-end and their source `mrr_amount` values are 100, 200 and 0, then:

```text
MRR = 100 + 200 + 0 = 300 source amount units
```

The zero-MRR trial row remains in the active subscription count if it meets the lifecycle rule, but contributes zero to MRR. Do not attach a currency symbol until confirmed.

## 14. Subscription movement taxonomy

Movement values are measured between two consecutive month-end snapshots, at a consistent entity grain. The default bridge should be account-level recurring revenue (sum of that account's eligible subscription MRR), with subscription-level detail retained for audit.

- **New customer MRR:** opening account MRR = 0 and closing account MRR > 0, and the account has no earlier eligible paid subscription history in the available observation window. If history before the dataset is unavailable, label as `new_in_observed_history`, not proven first-ever customer.
- **New subscription MRR:** MRR from a subscription ID absent from the prior snapshot for an account that may already exist. Report separately; it is not automatically new-customer MRR.
- **Expansion MRR:** positive increase in comparable recurring MRR for an account present in both snapshots, excluding separately classified new subscriptions if the bridge is designed to isolate them.
- **Contraction MRR:** absolute value of a decrease in recurring MRR for a continuing account that remains active at the closing snapshot.
- **Churned MRR:** opening MRR removed when an account has no eligible subscription at the closing snapshot and qualifies as customer churn under the approved rule.
- **Reactivated MRR:** closing MRR for an account that had previously churned and returns after a documented churn state, supported by event/snapshot sequence. It must not also be classified as new-customer MRR.
- **Unclassified/bridge residual:** any difference not supported by the above rules. Retain and investigate; never force it into a movement category.

An upgrade flag is not sufficient by itself to classify the exact timing or amount of expansion because the source has no plan-change timestamp or old/new price history. Snapshot comparison can measure observed net MRR change, but cannot prove the exact cause of that change.

### Mutually exclusive classification order

Apply a single account-level bridge classification to avoid double counting:

1. Opening MRR = 0 and closing MRR > 0:
   - If prior churn + supported return evidence exists: `reactivated_mrr`.
   - Else if no prior paid account history is observable: `new_customer_mrr`.
   - Else: `new_subscription_mrr` / existing-customer reactivation classification as supported; do not call it new customer.
2. Opening MRR > 0 and closing MRR = 0: `churned_mrr` if customer churn criteria pass.
3. Opening MRR > 0 and closing MRR > 0:
   - Closing greater than opening: `expansion_mrr` = difference.
   - Closing lower than opening: `contraction_mrr` = absolute difference.
   - Equal: `no_movement`.
4. Any conflicting or simultaneous lifecycle evidence that prevents a defensible assignment: `unclassified`; investigate.

For a subscription-level bridge, an account can have a churned subscription and a new subscription while remaining an active customer. Do not classify the whole account as churned in that case.

### MRR movement reconciliation

```text
Ending MRR
= Starting MRR
+ New Customer MRR
+ New Subscription MRR (if reported separately)
+ Expansion MRR
+ Reactivated MRR
- Contraction MRR
- Churned MRR
+/- documented bridge adjustments
```

If new subscription MRR is included within expansion or new customer MRR, do not add it again. Choose one mutually exclusive reporting design and document it in the output. For the simplified Week 2 bridge, new customer MRR is separate; additional subscriptions for existing accounts are treated as expansion/new-subscription movement, not new-customer MRR.

The bridge must reconcile exactly or carry an explicitly reported residual caused by unsupported source history or classification gaps.

## 15. Churn KPI definitions and denominator policy

### Customer churn

**Customers lost:** distinct eligible paid accounts that were in the opening customer population and meet the approved account-churn condition during the reporting month. A candidate condition is a recorded churn event in the month plus no eligible paid subscription at month-end. Validate event/date alignment and account subscription history before applying.

```text
Customer Churn Rate (%)
= Distinct eligible customers lost during month
  / Distinct eligible paid customers at opening snapshot
  × 100
```

Count distinct `account_id`, never `COUNT(*)` from `churn_events`. The source has 600 churn-event rows for 352 distinct accounts; repeated account IDs are expected.

### Gross revenue churn

Recommended Week 2 convention:

```text
Gross Revenue Churn Rate (%)
= (Churned MRR + Contraction MRR)
  / Starting MRR
  × 100
```

Report churned MRR and contraction MRR as separate components. Gross revenue churn excludes expansion and reactivation offsets.

### Net revenue churn

Recommended Week 2 convention:

```text
Net Revenue Churn Rate (%)
= (Churned MRR + Contraction MRR
   - Expansion MRR - Reactivated MRR)
  / Starting MRR
  × 100
```

This convention includes reactivated MRR as an offset. If the team chooses a different convention, document it and keep all monthly comparisons consistent. A net churn rate can be negative when expansion/reactivation exceed churn/contraction.

If starting MRR is zero, the rate is undefined (NULL/NA), not zero.

### Plan and acquisition segmentation

- Plan churn may be grouped by the opening subscription `plan_tier` or opening account's plan, but the chosen attribution must be consistent and labelled.
- Acquisition channel may use `accounts.referral_source`; the field is available and has observed categories `partner`, `other`, `organic`, `event`, `ads`.
- Do not infer acquisition channel from plan or account name.
- For accounts with multiple plans/subscriptions, avoid assigning the full account churn to multiple plan rows. Use subscription-level churned MRR for plan revenue churn; use one explicit account attribution rule for customer churn.

## 16. Week 2 assumptions, open questions and approval log

| ID | Decision | Working rule / evidence | Status |
|---|---|---|---|
| W2-01 | Reporting period | Calendar month, DATE boundaries | Proposed |
| W2-02 | Snapshot | Last calendar date of month | Proposed |
| W2-03 | End-date inclusivity | Not specified in source; choose inclusive or exclusive after review | Open |
| W2-04 | Active rule | Start/end dates + churn marker; trial handled separately | Open |
| W2-05 | MRR normalization | Use documented `mrr_amount` directly; ARR = 12 × MRR in all rows | Proposed |
| W2-06 | Currency/unit | Unknown for subscription amounts | Open |
| W2-07 | Seats | Do not multiply MRR by seats absent per-seat definition | Proposed |
| W2-08 | Discounts | No discount field in documented source | Confirmed limitation |
| W2-09 | Refunds | Keep `refund_amount_usd` separate from MRR | Proposed |
| W2-10 | Customer denominator | Distinct paid accounts at opening snapshot; report trial-inclusive separately if needed | Proposed |
| W2-11 | Reactivation | Requires previous churn state and supported return evidence | Open |
| W2-12 | Plan changes | Flags lack event timestamps/old-new price history | Confirmed limitation |
| W2-13 | Gross revenue churn | Churned + contraction divided by starting MRR | Proposed |
| W2-14 | Net revenue churn | Churned + contraction − expansion − reactivation divided by starting MRR | Proposed |

### Team approval record

| Decision area | Reviewers | Status | Date / notes |
|---|---|---|---|
| Reporting calendar and snapshot | Jaykishan + team | Pending team confirmation | — |
| Active/end-date interpretation | Jaykishan + Meghana | Pending | — |
| MRR field and source units | Jaykishan + Meghana | Pending source-owner confirmation | — |
| Trial/customer denominator | Jaykishan + Yash | Pending | — |
| Churn/reactivation event mapping | Jaykishan + Madhu Priya | Pending | — |
| Movement taxonomy | Jaykishan + Meghana + Madhu Priya + Yash | Pending | — |
| Refund and currency treatment | Jaykishan + Madhu Priya | Pending | — |

Do not change `Pending` to `Approved` until the named reviewers have explicitly confirmed the decision. Record actual names, date and decision rationale.
