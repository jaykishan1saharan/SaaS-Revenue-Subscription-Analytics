# Week 2 Day 7 — MRR Logic Review

**Owner:** Jaykishan  
**Review scope:** Lock MRR formula, revenue scope, SQL/Python interface and monthly output schema  
**Status:** Review recommendation prepared; team/source-owner confirmations remain pending where noted  
**Date:** 2026-11-21

## 1. Review objective

Review the proposed MRR implementation against the Week 2 business definitions and the actual RavenStack source fields. This review is intended to prevent annual revenue from being normalized twice, unsupported currency labels from entering reports, or an unapproved lifecycle rule from being embedded in SQL.

## 2. Source evidence reviewed

The repository's `docs/data_dictionary_subscriptions.md` documents:

- `subscriptions` has 5,000 rows and 5,000 distinct `subscription_id` values.
- One row per subscription record.
- 500 distinct `account_id` values; one account can have multiple subscriptions (2–19 observed per account).
- `start_date` is required; observed range 2023-01-09 through 2024-12-31.
- `end_date` has 4,514 NULLs and 486 populated values.
- `billing_frequency`: monthly 2,539, annual 2,461.
- `mrr_amount` is documented as monthly recurring revenue associated with the subscription.
- `arr_amount` is documented as annual recurring revenue.
- All 5,000 rows satisfy `arr_amount = 12 × mrr_amount`.
- All 778 trial rows have zero MRR and ARR.
- No currency code, currency symbol, discount, tax, invoice amount or payment amount is provided.

The Week 1 `reports/kpi_feasibility_matrix.md` records source-wide totals of MRR = 11,338,747 and ARR = 136,064,964. These are totals across all source rows, not a reporting-month snapshot. They must not be used as the January/February/etc. MRR values.

## 3. MRR formula decision

**Recommended formula:**

```text
MRR_t = SUM(mrr_amount)
        over subscriptions active at month-end t
```

Use `mrr_amount` directly for both `billing_frequency = 'monthly'` and `billing_frequency = 'annual'`, because the source dictionary explicitly defines the field as monthly recurring revenue and validates `arr_amount = 12 × mrr_amount` for every row.

Do not divide annual billing rows by 12 again. Doing so would produce a second normalization and understate annual-frequency MRR.

Use `billing_frequency` for validation and optional segmentation, not to automatically transform a field already named/documented as MRR.

**Approval caveat:** This is the defensible interpretation of the supplied data dictionary. If the dataset owner confirms a different meaning, update the rule with evidence and version the metric definition.

## 4. Revenue scope and exclusions

| Field / item | Review decision | Reason |
|---|---|---|
| `subscriptions.mrr_amount` | Include for eligible active subscriptions | Source dictionary defines as monthly recurring revenue |
| `subscriptions.arr_amount` | Report separately as annualized recurring revenue | Do not add ARR to MRR |
| `billing_frequency` | Retain for QA/segmentation | Does not override documented MRR field meaning |
| `seats` | Do not multiply MRR by seats | Source does not say MRR is per-seat price |
| `is_trial` | Keep trial records in subscription snapshot; zero MRR observed | 778 trial records have zero MRR/ARR; paid customer denominator handled separately |
| Discounts | No adjustment | No discount field in documented source |
| `refund_amount_usd` | Exclude from MRR; analyze separately | Refund is not recurring revenue |
| One-time fees, taxes, usage charges, cash receipts | Exclude | Not identified in the documented subscription source |

## 5. Reporting-month and active-population dependency

- Use calendar months with `period_start` inclusive and next-month start exclusive.
- Snapshot date is the final calendar day of each month.
- Snapshot grain is one row per `report_month × subscription_id`.
- Aggregate MRR only after selecting the eligible snapshot population.
- The source has no `subscription_status` field.
- 4,514 NULL `end_date` records align with `churn_flag = FALSE`; 486 populated end dates align with `churn_flag = TRUE`.
- The source does not say whether `end_date` is last active day or first inactive day.

Therefore, the MRR arithmetic can be locked, but the active-snapshot predicate cannot be called final until the team confirms end-date inclusivity and the role of `churn_flag`.

Candidate alternatives:

```sql
-- end_date is last active day (inclusive)
start_date <= snapshot_date
AND (end_date IS NULL OR end_date >= snapshot_date)
```

```sql
-- end_date is first inactive day (exclusive)
start_date <= snapshot_date
AND (end_date IS NULL OR end_date > snapshot_date)
```

Do not implement both or silently choose one. Retain a boundary test report and record the team's decision.

## 6. Currency and output labels

Subscription `mrr_amount` and `arr_amount` have no currency code or unit metadata. Until confirmed:

- use column names `mrr_source_amount` and `arr_source_amount`;
- label charts `MRR (source amount; currency unconfirmed)`;
- do not display `₹`, `$`, USD or INR for subscription MRR;
- keep `refund_amount_usd` separate and validate its source currency with the data owner.

## 7. SQL/Python interface

Both implementations must use the same logical input/output contract.

**Input population:** validated `subscriptions` table joined to calendar/reporting-month dates, with lifecycle predicate supplied by the approved rule.

**Output grain:** one row per reporting month for the aggregate dataset; plan output one row per reporting month and `plan_tier`.

**Required aggregate columns:**

- `report_month`
- `snapshot_date`
- `active_subscriptions`
- `active_accounts_all`
- `active_paid_accounts`
- `mrr_source_amount`
- `arr_source_amount`
- `basic_mrr_source_amount`
- `pro_mrr_source_amount`
- `enterprise_mrr_source_amount`
- `source_currency`
- `definition_version`

SQL and Python must:
1. use identical month-end dates;
2. use the same end-date and trial inclusion rules;
3. aggregate at subscription grain before account distinct counts;
4. preserve zero-MRR trial rows in subscription counts when lifecycle-eligible;
5. avoid multiplying MRR by seats;
6. avoid annual re-normalization;
7. use NULL/unknown currency label until confirmed.

## 8. Validation checklist

| Check | Expected result |
|---|---|
| Subscription IDs | 5,000 unique source IDs |
| Monthly + annual cadence counts | 2,539 + 2,461 = 5,000 |
| Trial count | 778; all have zero MRR and ARR |
| ARR relation | `arr_amount = 12 × mrr_amount` for all 5,000 rows |
| Currency label | Unknown / source amount until confirmed |
| Multiple subscriptions | Sum at subscription grain; count distinct accounts separately |
| MRR by plan | Plan subtotals sum to total monthly MRR |
| Annual handling | No additional `/12` applied to `mrr_amount` |
| Refund handling | `refund_amount_usd` excluded from MRR |
| Monthly coverage | Report months within source date coverage and with valid snapshot population |

## 9. Review conclusion and sign-off

**Jaykishan review recommendation:** Approve the formula `SUM(active subscriptions.mrr_amount)` and the source-amount output naming. Do not approve a currency symbol or final month-end active predicate until the missing source semantics are confirmed.

| Review item | Recommendation | Status |
|---|---|---|
| MRR formula | Sum `mrr_amount` for month-end active subscriptions | Recommended |
| Annual billing normalization | Do not divide `mrr_amount` again | Recommended |
| Currency label | Source amount; currency unknown | Required safeguard |
| Discount treatment | No adjustment; no source field | Confirmed limitation |
| Refund treatment | Exclude refund from MRR | Recommended |
| Seats treatment | Do not multiply by seats | Recommended |
| Active snapshot end-date boundary | Choose inclusive/exclusive after confirmation | Pending |
| SQL/Python output schema | Use section 7 schema | Recommended |

**Team confirmation required:** Meghana to verify subscription amount/lifecycle interpretation; Yash to confirm customer-vs-subscription roll-up; Lav Kumar to independently compare SQL/Python outputs. Record actual approvals and date before marking final.
