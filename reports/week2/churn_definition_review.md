# Week 2 Day 9 — Churn KPI Definition Review

**Owner:** Jaykishan  
**Scope:** Approve customer churn, gross revenue churn and net revenue churn definitions and denominator policy  
**Status:** Recommended definitions for team approval; lifecycle/event dependencies remain explicit

## 1. Review objective

Ensure customer churn and recurring revenue churn are measured separately, use aligned reporting periods, and do not confuse churn-event rows with distinct customers lost.

## 2. Source evidence

The Week 1 data dictionaries and KPI feasibility matrix document:

- `accounts`: 500 distinct account records.
- `subscriptions`: 5,000 subscription records across 500 accounts; one account can have multiple subscriptions.
- `churn_events`: 600 event records for 352 distinct accounts.
- `churn_events.churn_event_id` is unique across 600 rows.
- `churn_events.churn_date` is a DATE, observed from 2023-01-25 through 2024-12-31.
- `churn_events.is_reactivation` has 61 TRUE events (Week 1 feasibility matrix).
- `subscriptions.end_date` has 4,514 NULLs; the end-date business meaning is not confirmed.
- `accounts.churn_flag` and `subscriptions.churn_flag` are available, but their different grains and business meaning must not be conflated.
- `churn_events.refund_amount_usd` is a refund measure, not automatically recurring revenue loss.

Because churn events repeat by account, `COUNT(*)` from `churn_events` is not the lost-customer count.

## 3. Reporting period alignment

Use calendar-month periods:
- period start inclusive;
- next month start exclusive;
- churn event belongs to month when `churn_date >= period_start AND churn_date < next_month_start`.

Opening customer and MRR denominators are measured at the immediately preceding month-end snapshot. Numerator events are evaluated during the current month and validated against the account's subscription state.

The first month without a prior opening snapshot has no valid period churn denominator; publish the churn rate as NULL/NA for that month.

## 4. Customer churn definition

**Eligible starting customers:** distinct paid accounts active at the opening snapshot (the prior month-end), where active means at least one eligible non-trial subscription under the approved lifecycle rule.

**Customers lost:** distinct opening-population accounts that:
1. have qualifying churn evidence during the current reporting month; and
2. have no eligible paid subscription at the closing month-end snapshot.

This is the recommended account-level definition. It avoids counting a customer as churned when only one of multiple subscriptions ended but another paid subscription remains active.

```text
Customer Churn Rate (%)
= Distinct eligible customers lost during the month
  / Distinct eligible paid customers at opening snapshot
  × 100
```

Use `COUNT(DISTINCT account_id)` for both numerator and denominator. Do not use event row count. If the churn event and month-end state disagree, flag the account for review rather than forcing a classification.

### Trial policy

Recommended denominator for the primary customer churn KPI: paid accounts only (at least one eligible non-trial subscription at opening snapshot). Keep a separate all-account / trial-inclusive count if useful, but do not mix it into the paid-customer churn rate without relabelling.

## 5. Churned MRR

**Definition:** MRR present in the opening snapshot that is removed because an account has no eligible paid subscription at the closing snapshot and qualifies as churned.

For customer-level churn, use the account's full opening MRR only when the account is fully churned. If one subscription ends but another remains active, do not classify the full account MRR as churned.

Subscription-level churned MRR may be reported as a separate measure for ended subscription records, but it must not be confused with customer churned MRR.

## 6. Gross revenue churn

**Recommended Week 2 definition:**

```text
Gross Revenue Churn Rate (%)
= (Churned MRR + Contraction MRR)
  / Starting MRR
  × 100
```

- `Starting MRR`: total eligible MRR at the opening month-end snapshot.
- `Churned MRR`: recurring revenue lost from fully churned customers.
- `Contraction MRR`: recurring revenue reduction for continuing accounts that remain active.
- Expansion and reactivation do not offset gross revenue churn.

Report churned MRR and contraction MRR separately so the metric remains auditable.

## 7. Net revenue churn

**Recommended Week 2 definition:**

```text
Net Revenue Churn Rate (%)
= (Churned MRR + Contraction MRR
   - Expansion MRR - Reactivated MRR)
  / Starting MRR
  × 100
```

This convention treats expansion and supported reactivation as offsets to recurring revenue loss. It may produce a negative rate when expansion/reactivation exceed churn/contraction.

If starting MRR = 0, the rate is undefined and must be NULL/NA, not zero.

If expansion, contraction or reactivation cannot be supported by the snapshot/event evidence, do not publish a definitive net revenue churn rate. Mark it unavailable or provisional.

## 8. Plan and acquisition channel analysis

- `subscriptions.plan_tier` contains Basic, Pro and Enterprise.
- `accounts.referral_source` contains partner, other, organic, event and ads.
- For plan-level revenue churn, attribute opening MRR and churned MRR to the opening subscription plan.
- For customer churn by plan, define a single account attribution rule (for example, opening primary/highest-value plan) before grouping. Do not count one account in multiple plan groups unless the report explicitly says it is subscription-level.
- Acquisition-channel churn may group distinct lost accounts by `accounts.referral_source`.
- Do not infer missing acquisition channel or plan-change history.

## 9. Validation rules

1. Numerator distinct accounts must be a subset of the opening eligible account population for customer churn.
2. Repeated churn events for the same account count once in the customer churn numerator for the month.
3. Accounts with multiple subscriptions are churned only when no eligible paid subscription remains at close.
4. Opening customer denominator uses the prior month-end snapshot; do not use current month-end customers.
5. Opening MRR denominator uses the same prior month-end snapshot as the movement bridge.
6. Churned MRR must reconcile to opening MRR removed from qualifying churned accounts/subscriptions.
7. Refunds are not included in MRR churn.
8. The first report month without an opening snapshot has NULL churn rates.
9. SQL and Python must use identical account population, period boundaries and trial policy.

## 10. Review conclusion and approval

**Jaykishan's recommended definitions:**
- Customer churn = distinct paid accounts lost / distinct paid accounts at opening snapshot.
- Gross revenue churn = (churned MRR + contraction MRR) / starting MRR.
- Net revenue churn = (churned MRR + contraction MRR − expansion MRR − reactivated MRR) / starting MRR.

**Important dependency:** The final customer churn numerator depends on an approved active-subscription/end-date rule and validated churn-event semantics. Do not mark the KPI fully production-approved until those Day 6 lifecycle decisions are confirmed.

| Decision | Review recommendation | Status |
|---|---|---|
| Calendar month and event boundary | Use date-based calendar month | Recommended |
| Opening customer denominator | Distinct paid accounts at prior month-end | Pending team approval |
| Customers lost | Distinct opening accounts with churn evidence and no paid active subscription at close | Pending lifecycle approval |
| Gross revenue churn | Churned + contraction / starting MRR | Recommended |
| Net revenue churn | Churned + contraction − expansion − reactivation / starting MRR | Recommended |
| Event count vs customer count | Always distinct account IDs for customer churn | Required |
| Refund treatment | Exclude refund amount from MRR churn | Required |
| Plan/channel attribution | Use opening plan and `referral_source`; define one account-level rule | Pending |

### Sign-off

| Reviewer | Area | Status | Date / notes |
|---|---|---|---|
| Jaykishan | Churn KPI definitions and denominator recommendation | Prepared for review | 2026-11-21 |
| Yash | Customer population, distinct account counts, trial denominator | Pending | — |
| Madhu Priya | Churn event semantics and reactivation | Pending | — |
| Meghana | Subscription lifecycle and MRR churn mapping | Pending | — |
| Team | Final approval | Pending | — |

---
**Prepared by:** Jaykishan
