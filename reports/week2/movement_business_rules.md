# Week 2 Day 8 — Subscription Movement Business Rules

**Owner:** Jaykishan  
**Purpose:** Define a mutually exclusive MRR movement taxonomy and prevent upgrades/new subscriptions from being misclassified as new customers.  
**Status:** Proposed rules for team review; source limitations retained.

## 1. Decision summary

Use consecutive month-end snapshots to measure the change in recurring revenue. The primary customer movement bridge is at `account_id` grain, with subscription-level detail retained for audit. Calculate account MRR by summing eligible subscription MRR for each account.

Do not count an upgrade as a new customer. A new `subscription_id` under an existing `account_id` is a new subscription record, not automatically a new customer.

## 2. Source evidence and limitations

Available:
- `subscriptions.subscription_id`, `account_id`, `start_date`, `end_date`, `plan_tier`, `mrr_amount`, `arr_amount`, `is_trial`, `upgrade_flag`, `downgrade_flag`, `churn_flag`, `billing_frequency`.
- `churn_events.churn_event_id`, `account_id`, `churn_date`, `preceding_upgrade_flag`, `preceding_downgrade_flag`, `is_reactivation`.

Not available in documented source:
- subscription-level churn event key in `churn_events`;
- plan-change timestamp;
- old plan / new plan history;
- old MRR / new MRR event values;
- event sequence ID for simultaneous changes.

The upgrade/downgrade flags support source-record counts/indicators only. Snapshot differences can measure revenue movement but cannot prove the exact cause or date of a plan change.

## 3. Measurement grain

For each account and report month:
- `opening_mrr`: account MRR in prior month-end snapshot;
- `closing_mrr`: account MRR in current month-end snapshot;
- `delta_mrr = closing_mrr - opening_mrr`.

At subscription level, retain `subscription_id` to identify which records started or ended. Do not join raw churn event rows to subscriptions before event deduplication/aggregation; repeated account event rows can multiply subscription rows.

## 4. Mutually exclusive movement definitions

| Category | Rule | MRR amount |
|---|---|---|
| New Customer MRR | Opening account MRR = 0, closing > 0, and no earlier paid account history in observed data | Closing MRR |
| Reactivated MRR | Opening = 0, closing > 0, and prior churn plus supported return evidence exists | Closing MRR |
| New Subscription MRR | New subscription ID for an account already in customer population | MRR of new subscription; report separately if source snapshots support it |
| Expansion MRR | Continuing active account's closing MRR exceeds opening MRR | Closing − opening |
| Contraction MRR | Continuing account remains active but closing MRR is below opening MRR | Opening − closing |
| Churned MRR | Opening MRR > 0 and closing MRR = 0, with account churn evidence and no other eligible paid subscription at close | Opening MRR |
| No Movement | Opening MRR = closing MRR > 0 | 0 |
| Unclassified | Conflicting or insufficient evidence | Keep as residual; investigate |

**Observed-history caveat:** If the dataset does not include history before the first observed date, the team cannot prove a customer is first-ever new. Use `new_in_observed_history` in technical outputs where appropriate.

## 5. Classification precedence

Apply this order to avoid overlap:

1. `opening_mrr = 0 AND closing_mrr > 0`:
   - previous churn and supported return → Reactivated MRR;
   - no earlier paid account history in available data → New Customer MRR;
   - otherwise → New Subscription MRR / existing-account addition.
2. `opening_mrr > 0 AND closing_mrr = 0`:
   - Churned MRR only if no eligible paid subscription remains and the churn condition passes.
3. `opening_mrr > 0 AND closing_mrr > 0`:
   - closing > opening → Expansion;
   - closing < opening → Contraction;
   - equal → No Movement.
4. Conflicting or simultaneous events with no reliable ordering → Unclassified.

For a simplified account-level bridge, additional subscriptions for existing accounts are included in the account's net expansion where the account remains active. If the report separately exposes New Subscription MRR, subtract that component from the residual expansion classification so the same MRR is never counted twice. Choose one approach consistently.

## 6. Simultaneous-event handling

| Scenario | Account-level treatment | Subscription-level treatment |
|---|---|---|
| One subscription ends and another starts for same account | Do not mark customer churn if another paid subscription remains active; classify account net change | Record old subscription ending and new subscription start separately |
| Upgrade and downgrade flags both true / contradictory | Do not infer event order; use observed MRR delta or unclassified | Flag for review |
| Churn and reactivation events in same month | Order by `churn_date` if possible; if sequence or subscription link unclear, unclassified | Do not assume two independent revenue movements |
| New subscription added to existing account | Not new customer; account-level net change generally expansion | New subscription record |
| Refund attached to churn event | Exclude from MRR bridge | Report separately as refund |
| Account churn event but another subscription remains active | Not customer churn under the paid-account definition | Individual subscription may have churned |

## 7. Reconciliation convention

```text
Ending MRR
= Starting MRR
+ New Customer MRR
+ Expansion MRR
+ Reactivated MRR
- Contraction MRR
- Churned MRR
```

This is the required simplified bridge when additional subscription MRR for existing accounts is included within expansion. If the team reports `New Subscription MRR` separately, include it as a separate positive bridge line and remove the same amount from Expansion MRR.

The bridge must not double-count:
- New Customer MRR and Reactivated MRR;
- New Subscription MRR and Expansion MRR;
- subscription churn and customer churn;
- repeated churn events for the same account.

If the bridge does not reconcile, retain a `movement_residual` and investigate source coverage, date-boundary rules, unmatched subscription continuity or unsupported lifecycle events. Never force the residual into New MRR.

## 8. Suggested movement output fields

Recommended account-month movement output:

| Column | Purpose |
|---|---|
| `report_month` | Current reporting month |
| `account_id` | Account key |
| `opening_mrr_source_amount` | Prior snapshot account MRR |
| `closing_mrr_source_amount` | Current snapshot account MRR |
| `delta_mrr_source_amount` | Closing minus opening |
| `movement_type` | Mutually exclusive classification |
| `new_customer_mrr` | Positive amount for new customer category |
| `expansion_mrr` | Positive amount |
| `contraction_mrr` | Positive magnitude |
| `churned_mrr` | Positive amount removed |
| `reactivated_mrr` | Positive amount returned |
| `new_subscription_mrr` | Optional separate component; must not overlap expansion |
| `movement_residual` | Unexplained amount, if any |
| `classification_note` | Reason/evidence or limitation |

## 9. Review and sign-off

| Rule | Reviewer(s) | Status |
|---|---|---|
| Account-level bridge with subscription detail | Jaykishan + Yash + Meghana | Pending |
| Reactivation precedence over new customer | Jaykishan + Madhu Priya | Pending |
| New subscription vs expansion reporting | Jaykishan + Meghana | Pending |
| Simultaneous-event policy | Jaykishan + Madhu Priya | Pending |
| Reconciliation convention | Jaykishan + team | Pending |

**Jaykishan's recommendation:** Approve the classification precedence and account-level bridge only after the team confirms active snapshot logic. The current source does not support exact historical plan-change timing.
