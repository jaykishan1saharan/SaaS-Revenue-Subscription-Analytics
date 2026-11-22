# Week 2 Final Sign-off & Issue Register

**Owner:** Jaykishan  
**Review date:** 2026-11-22  
**Status:** Integration review drafted; team sign-off pending.

## 1. Sign-off summary

The supplied MRR and account-population outputs are internally consistent across 24 reporting months. The movement bridge ties to month-end opening/closing MRR only when the **15,106 source amount unit** unclassified positive movement is retained. Customer churn and plan churn outputs remain provisional pending independent event and QA review.

**Decision:** Conditional acceptance for internal Week 2 integration. This is not a claim of final team approval, production readiness, or live SQL/Python parity.

## 2. Issue register

| ID | Issue / decision | Evidence / impact | Owner(s) | Status | Required closure |
|---|---|---|---|---|---|
| W2-01 | End-date inclusivity | Supplied outputs use `end_date >= snapshot_date`; source does not define whether end date is last active day or first inactive day. Boundary rows may change month-end counts and MRR. | Jaykishan, Meghana, source owner | Open / blocking final approval | Confirm semantics; if exclusive, change predicate to `>` and regenerate all monthly outputs. |
| W2-02 | Subscription MRR currency and unit | No currency code/unit metadata in source. | Jaykishan, source owner | Open | Confirm currency/scale or retain `source_amount` and unknown currency labels in every report. |
| W2-03 | Movement residual | Four account-month rows in Sep-2023, Feb-2024 and Oct-2024 total 15,106; classified `new_subscription_or_return_unconfirmed`. | Jaykishan, Madhu Priya, Meghana | Open / blocking full bridge sign-off | Review churn/reactivation chronology and subscription continuity; classify only with evidence, otherwise keep explicit unclassified adjustment. |
| W2-04 | Reactivation event semantics | 61 `is_reactivation = TRUE` event rows are available, but event meaning/order and subscription linkage require review. | Madhu Priya | Open | Submit event rule review and identify supported account return sequences. |
| W2-05 | Customer churn independent validation | Yash output reports one lost account in Sep-2024 (1/384 = 0.2604%); no independent event QA supplied in this integration bundle. | Madhu Priya, Lav Kumar, Yash | Open | Recompute distinct lost accounts from event/subscription history and reconcile against opening/closing account snapshots. |
| W2-06 | SQL/Python parity | Generated CSV outputs were cross-checked, but SQL was not executed against live Supabase/PostgreSQL and compared with Python in this review. | Meghana, Lav Kumar | Open | Execute SQL, compare all monthly/plan/movement outputs and attach evidence. |
| W2-07 | Missing MRR SQL deliverable | `sql/03_mrr_calculations.sql` was not present in the reviewed Meghana ZIP. | Meghana | Open | Add the SQL implementation and verify it against `monthly_mrr.csv`. |
| W2-08 | Missing final consolidated KPI output | `data/processed/monthly_saas_kpis.csv` was not present in the reviewed files. | Meghana | Open | Produce the agreed consolidated monthly KPI table after review. |
| W2-09 | Missing independent QA evidence | Lav's movement/churn validation reports, final validation checklist, notebook execution evidence and movement waterfall were not included in the reviewed handoff. | Lav Kumar | Open | Add required QA files and record pass/blocked results. |
| W2-10 | Missing final customer population QA | `reports/week2/final_customer_population_qa.md` was not included in the reviewed Yash package. | Yash | Open | Add final account count/segmentation/multi-subscription QA and reconcile to the snapshot. |
| W2-11 | Churn-event and churn-flag semantics | Account and subscription flags have different grains; `churn_date`, `end_date` and `churn_flag` are not proven to be the same milestone. | Madhu Priya, Yash, Meghana | Open | Document event meaning and exception handling; do not use static flags alone to date customer churn. |
| W2-12 | GitHub PR review/merge state | PRs and reviewer approvals cannot be verified from the supplied local files. | Jaykishan, all contributors | Open | Confirm each PR is reviewed, comments resolved and merged; record links/approvers in the sign-off table. |

## 3. Required final sign-off checklist

- [ ] End-date boundary confirmed and outputs regenerated if needed.
- [ ] Currency/unit confirmed or unknown-unit limitation explicitly accepted.
- [ ] 15,106 movement residual dispositioned or formally accepted as unclassified.
- [ ] Madhu Priya's churn-event and reactivation review merged.
- [ ] Lav Kumar's independent SQL/Python, movement and churn QA merged.
- [ ] Meghana's MRR SQL and consolidated monthly KPI output added and validated.
- [ ] Yash's final customer population QA added.
- [ ] Customer churn denominator/numerator and plan attribution reviewed.
- [ ] All PR review comments resolved and merge status verified.
- [ ] Final KPI report reviewed and approved by the team.

## 4. Sign-off record

| Role / reviewer | Review area | Decision | Name / approval | Date | Notes |
|---|---|---|---|---|---|
| Integration lead | Cross-file MRR, movement and population reconciliation | Conditional recommendation only | Jaykishan — fill after review | Pending | 15,106 residual and listed issues remain open |
| Yash | Account population, customer grain and segmentation | Pending | — | — | Include final population QA |
| Meghana | Lifecycle, MRR and plan-level churn | Pending | — | — | Confirm end-date rule and add MRR SQL |
| Madhu Priya | Churn events, reactivation and churned MRR | Pending | — | — | Event chronology required |
| Lav Kumar | Independent QA and SQL/Python parity | Pending | — | — | Attach execution evidence |
| Team | Week 2 final report approval | Pending | — | — | Complete only after blocking issues are closed or formally accepted |

## 5. Final status wording for the Week 2 report

Until the checklist is complete, use:

> Week 2 integration review completed on the supplied generated outputs. Monthly MRR and account population files reconcile across all 24 reporting months. The movement bridge retains 15,106 source amount units as unclassified pending event-history review. Churn metrics, lifecycle boundary semantics, independent SQL/Python parity and final team approval remain provisional or pending.
