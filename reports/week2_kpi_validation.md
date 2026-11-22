# Week 2 — KPI Validation & Final Integration Review

**Owner:** Jaykishan  
**Review date:** 2026-11-22  
**Scope:** Final integration of Days 6–9 outputs; cross-file population, MRR, movement and churn validation.  
**Overall status:** **Conditional / provisional — not final team-approved sign-off.**

## 1. Executive summary

The supplied MRR and account-population CSV outputs are internally consistent across all 24 reporting months. Plan-level MRR sums to total MRR in every month, and Yash's account roll-up matches Meghana's monthly MRR output for active subscription counts, active account counts, paid account counts and MRR.

The movement file also matches the opening and closing MRR snapshots over 23 month-to-month comparisons. However, the movement categories do not fully reconcile without retaining an explicit **15,106 source amount unit** unclassified positive movement. Four account-month rows are labelled `new_subscription_or_return_unconfirmed`; these must not be silently recoded as new customer or reactivation.

Customer churn and plan churn outputs are available, but the event interpretation and independent QA work expected from Madhu Priya and Lav Kumar were not included in the reviewed package. The end-date inclusivity and source currency/unit also remain unconfirmed. Therefore this report records an integration review and conditional acceptance of internal outputs, not an assertion that every Week 2 KPI is fully approved for external or production reporting.

## 2. Inputs reviewed

| Contributor | Reviewed artifacts | Integration use |
|---|---|---|
| Jaykishan | `docs/metric_definitions.md`, `docs/subscription_lifecycle.md`, MRR/movement/churn review documents | Business definitions and assumptions |
| Meghana | `monthly_mrr.csv`, `monthly_mrr_movements.csv`, `churn_by_plan.csv`, lifecycle/plan churn reports, Python implementation | MRR and movement results; plan churn |
| Yash | Account population review, monthly roll-up CSV, movement identity CSV/review, customer churn population CSV/notes, customer SQL | Account grain, population and customer churn |

The integration review used the supplied generated files. It did not execute the SQL against the live Supabase/PostgreSQL database or verify GitHub pull-request merge status.

## 3. Source population and grain checks

| Check | Observed result | Review |
|---|---:|---|
| Account rows / distinct accounts | 500 / 500 | Pass |
| Subscription rows / distinct subscription IDs | 5,000 / 5,000 | Pass |
| Accounts represented in subscriptions | 500 | Pass |
| Subscriptions per account | 2–19 observed | Multiple subscriptions must be retained |
| Churn event rows / distinct accounts | 600 / 352 | Event rows are not lost-customer counts |
| Trial subscriptions | 778; all have zero MRR and ARR | Keep trial counts separate from paid accounts |
| Billing frequency | 2,539 monthly; 2,461 annual | Use source `mrr_amount` directly for both frequencies |

**Grain rule:** `subscription_id` is the subscription/revenue grain. `account_id` is the customer grain. Sum eligible subscription MRR before deriving account totals; count customers with `COUNT(DISTINCT account_id)`.

## 4. Monthly MRR and account roll-up reconciliation

| Validation | Result | Status |
|---|---:|---|
| Reporting months | 24 (2023-01 to 2024-12) | Pass |
| MRR vs Yash account roll-up: active subscriptions | 24/24 exact matches | Pass |
| MRR vs Yash account roll-up: active accounts | 24/24 exact matches | Pass |
| MRR vs Yash account roll-up: paid accounts | 24/24 exact matches | Pass |
| MRR vs Yash account roll-up: MRR amount | 24/24 exact matches | Pass |
| Basic + Pro + Enterprise MRR vs total MRR | 24/24 exact matches | Pass |
| Monthly ARR vs 12 × monthly MRR | 24/24 exact matches | Pass |
| Yash closing paid accounts vs account roll-up paid accounts | 24/24 exact matches | Pass |

### MRR range

- January 2023 month-end MRR: **4,684 source amount units**.
- December 2024 month-end MRR: **10,259,509 source amount units**.
- December 2024 ARR output: **123,114,108 source amount units**.
- The subscription amount currency/unit is unknown. Do not add INR/USD symbols.

MRR uses `mrr_amount` directly for monthly and annual billing-frequency rows because the source dictionary defines it as monthly recurring revenue and every source row satisfies `arr_amount = 12 × mrr_amount`. No additional annual `/12` conversion is applied. No discount adjustment, seats multiplier, refund, tax or unsupported one-time charge is included.

## 5. MRR movement bridge reconciliation

The movement output contains 11,500 account-month records over 23 comparisons (February 2023 through December 2024). There are 500 account rows per comparison. Summed opening MRR matches the previous month's MRR; summed closing MRR matches the current month's MRR.

| Movement category | Amount (source units) |
|---|---:|
| New customer MRR | 2,420,546 |
| Expansion MRR | 8,260,993 |
| Reactivated MRR | 94,450 |
| Contraction MRR | 517,763 |
| Churned MRR | 18,507 |
| Unclassified positive movement / residual | 15,106 |
| **Net change** | **10,254,825** |

Reconciliation:

```text
Starting MRR (Jan-2023)                           4,684
+ New customer MRR                           2,420,546
+ Expansion MRR                              8,260,993
+ Reactivated MRR                               94,450
- Contraction MRR                             (517,763)
- Churned MRR                                  (18,507)
+ Unclassified positive movement                15,106
                                               ---------
Ending MRR (Dec-2024)                        10,259,509
```

The unclassified 15,106 is four positive account-month rows across 2023-09 (1,990), 2024-02 (3,136 and 3,184) and 2024-10 (6,796). Each row has zero opening MRR and positive closing MRR, but the reviewed data does not prove whether it represents a returning subscription for an existing account or a reactivation. Keep this amount separate pending Madhu Priya's event chronology review.

The movement CSV's `new_subscription_mrr` is a diagnostic sum of new subscription starts. It overlaps the account-level bridge categories and is not an additive bridge component. Do not add it again.

## 6. Customer and plan churn checks

### Customer churn population

- Yash's output contains 24 monthly rows.
- January 2023 has no preceding month-end snapshot, so opening paid accounts and churn rate are NULL.
- September 2024 reports 1 distinct lost account from 384 opening eligible paid accounts: **0.2604%**.
- Other months report zero lost accounts under the provisional event-plus-closing-state rule.
- The output separately reports accounts with churn events; those counts are not the number of customers lost.
- Closing eligible paid account counts match the Yash/Meghana account roll-up for all 24 months.

This is a provisional customer churn calculation. Madhu Priya's event review and Lav Kumar's independent churn validation are required before final KPI approval.

### Plan-level churn

- 72 rows cover 24 months × 3 plans.
- 69 plan-month churn rates are defined; 3 are NULL because opening plan denominators are zero.
- Plan attribution uses `plan_tier` on the ended subscription row. It is subscription-level churn, not customer-level churn.
- Multiple concurrent subscriptions and missing plan-change history limit account-level plan attribution.

## 7. Known limitations and publication controls

1. No source `subscription_status` column exists; status labels are derived only from available flags and dates.
2. The inclusive `end_date >= snapshot_date` rule is used in supplied outputs but remains unconfirmed. If `end_date` means first inactive day, the predicate must be `end_date > snapshot_date` and outputs must be regenerated.
3. Subscription MRR/ARR currency and unit are unknown; label as source amount.
4. `churn_flag` has no event timestamp and does not by itself identify a monthly churn period.
5. `churn_events` has 600 event rows for 352 accounts; count distinct accounts for customer churn.
6. `is_reactivation` is account-linked and does not identify a subscription ID; event chronology needs review.
7. Upgrade/downgrade flags have no event timestamps or old/new price values; do not infer exact plan-change timing.
8. No discount field exists; no discount adjustment is supported.
9. Refund amounts are not MRR and must be excluded from recurring revenue.
10. The supplied generated outputs were not independently rerun against a live database during this integration review.

## 8. Final integration decision

**Conditional integration recommendation:**

- Accept the MRR output and account-population cross-checks as internally consistent provisional artifacts.
- Accept plan MRR subtotals as reconciling to monthly MRR.
- Accept the movement file's opening/closing snapshot tie-out, while preserving the 15,106 unclassified bridge residual.
- Keep customer and plan churn outputs marked provisional until event semantics and independent QA are supplied.
- Do not claim final team approval, production readiness, or SQL/Python parity without the missing evidence listed in the issue register.

The final sign-off fields remain blank/pending for the actual reviewers to complete.

---

## Appendix A — Reproduction checks

The following pandas-style checks describe the cross-file validation performed on the supplied CSV outputs. The report's results are based on the actual generated CSVs listed in the inputs section.

```python
# Normalize report month keys before joining.
mrr["month"] = pd.to_datetime(mrr["report_month"]).dt.strftime("%Y-%m")
rollup["month"] = pd.to_datetime(rollup["report_month"]).dt.strftime("%Y-%m")

joined = mrr.merge(rollup, on="month", suffixes=("_mrr", "_rollup"))
assert len(joined) == 24
assert (joined["active_subscriptions_mrr"] == joined["active_subscriptions_rollup"]).all()
assert (joined["active_accounts_all_mrr"] == joined["active_accounts_all_rollup"]).all()
assert (joined["active_paid_accounts"] == joined["active_paid_accounts_rollup"]).all()
assert (joined["mrr_source_amount_mrr"] == joined["mrr_source_amount_rollup"]).all()

assert (
    mrr["basic_mrr_source_amount"]
    + mrr["pro_mrr_source_amount"]
    + mrr["enterprise_mrr_source_amount"]
    == mrr["mrr_source_amount"]
).all()

# Keep movement_residual as an explicit bridge category.
# Do not add new_subscription_mrr: it is a diagnostic overlapping measure.
```
