# Subscription Lifecycle and Movement Rules — SaaS Revenue & Subscription Analytics

**Project:** RavenStack SaaS Revenue & Subscription Analytics  
**Owner:** Jaykishan  
**Status:** Working rules for team review; unresolved items are explicitly marked  
**Source basis:** `docs/data_dictionary_subscriptions.md`, `docs/data_dictionary_accounts.md`, `docs/data_dictionary_churn_events_feature_usage.md`, `docs/week2_handover.md`, `docs/cleaning_decision_log.md`.

## 1. Purpose

This document defines how the team interprets subscription state at a point in time and how it identifies changes between reporting periods. It covers lifecycle status mapping, effective dates, cancellation, reactivation, plan changes, multiple subscriptions per account and the mutually exclusive MRR movement taxonomy.

## 2. Source tables and grain

| Table | Grain | Relevant fields |
|---|---|---|
| `accounts` | One row per `account_id` (500 observed) | `account_id`, `signup_date`, `referral_source`, `plan_tier`, `is_trial`, `churn_flag` |
| `subscriptions` | One row per `subscription_id` (5,000 observed) | `subscription_id`, `account_id`, `start_date`, `end_date`, `plan_tier`, `seats`, `mrr_amount`, `arr_amount`, `is_trial`, `upgrade_flag`, `downgrade_flag`, `churn_flag`, `billing_frequency`, `auto_renew_flag` |
| `churn_events` | One row per `churn_event_id` (600 observed) | `churn_event_id`, `account_id`, `churn_date`, `reason_code`, `refund_amount_usd`, `preceding_upgrade_flag`, `preceding_downgrade_flag`, `is_reactivation` |

Relationships validated in Week 1: accounts → subscriptions (one-to-many), accounts → churn_events (one-to-many). All subscription account references and churn-event account references matched accounts.

## 3. Raw status mapping

The subscription source does **not** contain a text `subscription_status` column. The following are derived analysis labels, not source status values.

| Derived label | Source evidence | Meaning / handling |
|---|---|---|
| `not_started` | `start_date > snapshot_date` | Subscription has not started as of snapshot |
| `candidate_active` | Start date on/before snapshot, NULL end date, `churn_flag = FALSE` | Candidate ongoing record; NULL end date is not independently proof of active |
| `candidate_ended` | Populated `end_date`, `churn_flag = TRUE` | Churn-marked record with an end date; end-date business meaning still needs confirmation |
| `trial_candidate_active` | Candidate active + `is_trial = TRUE` | Trial population; all 778 trial rows have zero MRR and ARR |
| `paid_candidate_active` | Candidate active + `is_trial = FALSE` | Candidate non-trial active population |
| `lifecycle_conflict` | Date and flags disagree | Retain for investigation; do not silently coerce |

Observed alignment: 4,514 NULL `end_date` records have `churn_flag = FALSE`; 486 populated `end_date` records have `churn_flag = TRUE`. The dictionary explicitly states the business meaning of end date needs confirmation.

Do not derive `paused`, `past_due`, `suspended`, `cancelled` or `expired` as distinct statuses because those source states are not provided.

## 4. Effective start and end dates

- `start_date` is the recorded start date, required, observed from 2023-01-09 to 2024-12-31.
- `end_date` is nullable; 4,514 NULL and 486 populated values, observed populated range 2023-04-05 to 2024-12-31.
- Week 1 cleaning decision: preserve NULL; do not replace it with current date or an artificial value.
- Source does not specify whether `end_date` is last active day or first inactive day.

Two candidate month-end tests must be evaluated until the team confirms semantics:

**If end_date is inclusive (last active day):**
```sql
start_date <= snapshot_date
AND (end_date IS NULL OR end_date >= snapshot_date)
```

**If end_date is exclusive (first inactive day):**
```sql
start_date <= snapshot_date
AND (end_date IS NULL OR end_date > snapshot_date)
```

`churn_flag` should be evaluated alongside dates. Whether it is a hard exclusion or a cross-check must be approved. Keep trial eligibility separate from paid-customer denominator eligibility.

## 5. Month-end snapshot convention

Use one snapshot per calendar month, as of the last calendar date. Recommended snapshot grain: one row per `report_month × subscription_id`, before aggregation.

Recommended columns:
`report_month`, `snapshot_date`, `subscription_id`, `account_id`, `plan_tier`, `billing_frequency`, `is_trial`, `start_date`, `end_date`, `churn_flag`, `is_active_snapshot`, `mrr_amount`, `arr_amount`.

A snapshot answers: “Which subscriptions qualify as active on this date, and what recurring amount is associated with them?” It does not count all churn events during the month.

## 6. Cancellation timing

Available evidence: `subscriptions.end_date`, `subscriptions.churn_flag`, `subscriptions.auto_renew_flag`, and `churn_events.churn_date`.

Not available: cancellation-request timestamp, explicit cancellation-effective timestamp, a status-history table, or a subscription event log.

Rules:
1. `auto_renew_flag = FALSE` does not itself mean churn.
2. Do not assume `churn_flag` provides an exact cancellation date.
3. Use `churn_events.churn_date` as the recorded event date for event-based analysis, but do not claim it is the cancellation request date or effective service-end date without confirmation.
4. Do not assume `end_date` and `churn_date` represent the same milestone.
5. Retain mismatches among event date, end date and flags for review.

## 7. Reactivation

`churn_events.is_reactivation` is available. The dictionary says its exact event interpretation is not specified. There are 600 churn-event rows for 352 distinct accounts; 61 events are marked as reactivations (per Week 1 feasibility matrix).

Candidate account-level reactivation requires:
- evidence the account previously churned,
- a later return indication (`is_reactivation = TRUE` and/or later eligible subscription snapshot),
- sequence validation by `churn_date`,
- returning MRR counted as reactivated rather than new-customer MRR.

The event table links to `account_id`, not `subscription_id`. With multiple subscriptions per account, the event cannot always identify the specific subscription that returned. Do not invent that link.

## 8. Plan changes

Available fields: `subscriptions.upgrade_flag`, `subscriptions.downgrade_flag`, `churn_events.preceding_upgrade_flag`, `churn_events.preceding_downgrade_flag`.

The source does not provide plan-change timestamp, prior plan, new plan, old MRR or new MRR. The flags support source-record/event indicators only; they do not prove timing or monetary impact.

A continuing account's MRR increase/decrease between consecutive month-end snapshots can be measured as expansion/contraction. This is an observed revenue movement, not proof that a particular upgrade/downgrade flag caused it.

Do not count an upgrade as a new customer. A new `subscription_id` for an existing account is a new subscription record; it is not automatically new-customer acquisition.

## 9. Multiple subscriptions per account

Observed: 5,000 subscription rows across 500 accounts; 2–19 subscription records per account.

- Subscription state and MRR are first evaluated at `subscription_id` grain.
- Account MRR is the sum of eligible subscription MRR for the account.
- Customer count is `COUNT(DISTINCT account_id)`.
- Ending one subscription does not imply account churn if another subscription remains eligible.
- Customer churn occurs only when the account has no eligible paid subscription at closing snapshot and the event/lifecycle rule supports loss.
- Do not count multiple churn-event rows for one account as multiple lost customers.

## 10. Snapshot analysis vs event analysis

| Business question | Method | Fields |
|---|---|---|
| Active subscriptions at month-end | Snapshot | subscription dates and flags |
| Month-end MRR | Snapshot then aggregate | active population + `mrr_amount` |
| Churn events during month | Event-based | `churn_events.churn_date` |
| Unique customers lost | Event plus account/subscription state | `account_id`, `churn_date`, snapshots |
| Reactivation | Event sequence + snapshot | `is_reactivation`, `churn_date`, subscription state |
| Expansion/contraction | Compare consecutive snapshots | account/subscription MRR |
| Exact plan-change date | Not supported by current source | no event timestamp |

## 11. MRR movement taxonomy and mutually exclusive classification

### 11.1 Measurement basis

Compare consecutive month-end snapshots. Use account-level MRR as the primary customer movement bridge (sum of active subscription MRR per account), while retaining subscription-level detail for audit.

For each account and month:
- `opening_mrr`: account MRR in previous month-end snapshot.
- `closing_mrr`: account MRR in current month-end snapshot.
- `delta_mrr = closing_mrr - opening_mrr`.

The movement categories below must be mutually exclusive at account level.

### 11.2 Definitions

| Movement | Definition | Calculation / condition |
|---|---|---|
| New customer MRR | First observed paid customer revenue entering the active population | Opening MRR = 0; closing MRR > 0; no earlier paid account history in available data |
| New subscription MRR | Revenue from a new subscription ID for an account that already existed | Subscription absent from prior snapshot; account may have opening MRR > 0 |
| Expansion MRR | Increase in recurring revenue for a continuing active account | Opening MRR > 0; closing MRR > opening MRR |
| Contraction MRR | Decrease for a continuing account that remains active | Opening MRR > 0; 0 < closing MRR < opening MRR |
| Churned MRR | Opening recurring revenue lost when account leaves paid active population | Opening MRR > 0; closing MRR = 0; customer churn criteria pass |
| Reactivated MRR | Returning recurring revenue after a previously evidenced churn | Prior churn state plus supported later return; do not label as new customer |
| No movement | No change in recurring revenue | Opening MRR = closing MRR > 0 |
| Unclassified | Evidence insufficient or conflicting | Keep as residual; investigate |

### 11.3 Priority order to prevent double counting

1. If opening MRR = 0 and closing MRR > 0:
   - prior churn and supported return evidence → Reactivated MRR;
   - no earlier paid account history in the observed window → New Customer MRR;
   - otherwise → New Subscription MRR / existing-account addition, not new customer.
2. If opening MRR > 0 and closing MRR = 0:
   - classify as Churned MRR only if the account has no eligible paid subscription at close and churn evidence is valid.
3. If opening and closing MRR are both positive:
   - closing > opening → Expansion MRR;
   - closing < opening → Contraction MRR;
   - equal → No movement.
4. If simultaneous/conflicting events make the category uncertain, assign `unclassified` and retain a review record.

For a subscription-level bridge, one subscription may churn while another subscription for the same account starts. The account must not be labelled churned if it remains paid-active. Report subscription-level churn separately from customer churn.

### 11.4 Simultaneous events

- Churn of one subscription plus start of another for same account: account-level bridge uses net account MRR and account remains active; subscription-level outputs can separately show the ended and started subscription.
- Upgrade and downgrade flags both true or contradictory: do not infer sequence; classify by observed snapshot MRR change only and flag for review.
- Churn event and reactivation event in same month: order by `churn_date` where possible; if no clear ordering or no subscription linkage, do not assume both are independent revenue movements. Use the month-end state and mark ambiguous event sequence.
- New subscription and expansion in same period: select one account-level bridge convention; do not add the same MRR to both categories.
- Refund in a churn event: keep refund amount separate from MRR movement.

### 11.5 Reconciliation

```text
Ending MRR
= Starting MRR
+ New Customer MRR
+ New Subscription MRR (only if separately reported)
+ Expansion MRR
+ Reactivated MRR
- Contraction MRR
- Churned MRR
+/- documented adjustments
```

If New Subscription MRR for existing accounts is included within Expansion MRR, it must not also be added as a separate bridge component. The final report must state which approach is used. Unexplained residuals must remain visible and be investigated.

## 12. SQL implementation notes

Use PostgreSQL date logic and avoid joining churn events directly to subscriptions before aggregating/deduplicating event rows; otherwise repeated account events can multiply subscription rows.

Illustrative snapshot predicate (end-date boundary is still pending):

```sql
-- Choose exactly one end-date comparison after business approval.
start_date <= snapshot_date
AND (end_date IS NULL OR end_date >= snapshot_date) -- inclusive alternative
```

Illustrative account-level aggregation after the active subscription snapshot:

```sql
SELECT
    report_month,
    account_id,
    SUM(mrr_amount) AS account_mrr
FROM monthly_subscription_snapshot
WHERE is_active_snapshot = TRUE
  AND is_trial = FALSE
GROUP BY report_month, account_id;
```

The SQL is a pattern, not a final query until active-date and trial rules are signed off.

## 13. Open questions and sign-off

| Decision | Owner(s) | Status |
|---|---|---|
| End-date inclusive or exclusive | Jaykishan + Meghana | Pending |
| Is `churn_flag` authoritative or a cross-check? | Jaykishan + Meghana + Madhu Priya | Pending |
| What does `churn_date` represent? | Jaykishan + Madhu Priya | Pending |
| How should trial accounts be counted? | Jaykishan + Yash | Pending |
| Meaning and ordering of reactivation events | Jaykishan + Madhu Priya | Pending |
| Account-level treatment of new subscriptions | Jaykishan + Yash + Meghana | Pending |
| Final bridge convention for new subscription MRR vs expansion | Jaykishan + team | Pending |

### Approval log

| Rule | Status | Approver(s) | Date | Notes |
|---|---|---|---|---|
| Movement grain and definitions | Pending team review | — | — | Account-level bridge with subscription detail |
| Reactivation priority | Pending | — | — | Must not overlap new customer MRR |
| Simultaneous event policy | Pending | — | — | Use unclassified when evidence conflicts |
| MRR bridge convention | Pending | — | — | Avoid double-counting new subscription MRR |

---
**Prepared by:** Jaykishan
