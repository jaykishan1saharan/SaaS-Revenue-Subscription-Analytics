# Final Churn Reconciliation QA

**Status:** Event reconciliation and lifecycle KPI calculations passed under
the documented provisional end-date and reactivation rules.

## Scope

This QA reconciles the 600 churn-event records against the 5,000 subscription
records and the candidate churned-MRR mapping. It does not certify customer
loss or lifecycle transitions because the source has no subscription-level
event foreign key or confirmed churn effective-date semantics.

## Event reconciliation

| Measure | Result |
|---|---:|
| Recorded event rows | 600 |
| Candidate churn rows (`is_reactivation = false`) | 539 |
| Reactivation rows (`is_reactivation = true`) | 61 |
| Distinct accounts with any event | 352 |
| Distinct accounts with candidate churn | 339 |
| Distinct accounts with reactivation | 55 |
| Sequence-supported reactivation rows | 29 |

The 539 candidate churn rows and 339 candidate-churn accounts are not
customer-loss counts. Repeated event IDs remain separate recorded events.
Distinct accounts must be deduplicated only for account-level reporting.

## Subscription MRR reconciliation

The exact date-key test found:

| Mapping result | Rows |
|---|---:|
| No exact same-account/end-date match | 532 |
| Ambiguous single-event/multiple-subscription match | 1 |
| Ambiguous multiple-event/same-account-date | 2 |
| One-to-one candidate match | 4 |

The four one-to-one candidates are subscription departures, not confirmed
churned MRR. They have 8, 9, 13 or 16 other subscription rows that are not
ended by the event date. The eligibility rule therefore rejects all four
because the account may still have an ended-by-churn-date or null-end-date
subscription population.

**Final eligible churned-MRR event count:** 0

**Final eligible churned-MRR amount:** 0.0 source MRR units

No amount can be reported as customer churned MRR until the lifecycle, end-date
and event-to-subscription mapping rules are approved.

## Refund control

| Refund measure | Source amount |
|---|---:|
| All event rows | 8,652.25 |
| Candidate churn rows | 8,120.91 |
| Reactivation rows | 531.34 |

Refund values are excluded from MRR and recurring-revenue-churn calculations.
They are also not used to classify an event as churn or reactivation.

## Reactivation and repeated-cycle treatment

- `is_reactivation = true` is reported as a reactivation event, not as churn.
- A direct reactivation is sequence-supported only after a prior
  non-reactivation event in a strictly earlier account-date row.
- Same-day event groups remain ambiguous; no within-day tie-breaker is invented.
- Repeated candidate-churn events for one account/month are retained in the
  event file and deduplicated in account-month summaries.
- The possible churn/reactivation/cycle accounts are counted as sequence
  evidence only. A reactivation does not erase a prior event, and a later
  candidate churn is not double-counted in the account-month distinct account.

## Customer and revenue churn status

The lifecycle reconciled output is available in
`data/processed/churn/monthly_lifecycle_churn.csv`.

| Metric | Result | Status |
|---|---|---|
| Customer churn rate | 0.2604% in September 2024 | Pass under the provisional opening/closing paid-account rule |
| Churned MRR | 5,771 source units in September 2024 | Pass for the one fully lost account |
| Contraction MRR | 517,763 source units across the measured periods | Pass |
| Expansion MRR | 8,260,993 source units across the measured periods | Pass |
| Sequence-supported reactivation MRR | 42,394 source units across November/December 2024 | Pass with reactivation evidence limitation |
| Gross revenue churn rate | Calculated month by month | Pass / provisional lifecycle |
| Net revenue churn rate | Calculated month by month | Pass / provisional lifecycle |

The repeatable gross/net formulas are:

```text
Gross revenue churn = (churned MRR + contraction MRR) / starting MRR
Net revenue churn   = (churned MRR + contraction MRR
                       - expansion MRR - reactivated MRR) / starting MRR
```

Starting MRR and all movement components use the provisional inclusive
`end_date >= month-end` rule already used by the repository. The September
2024 opening population is 384 paid accounts and the one lost account is
deduplicated once. Refunds are never added to or subtracted from MRR.

## QA verdict

- **Event row count reconciliation:** Pass
- **Candidate/reactivation separation:** Pass
- **Refund exclusion:** Pass
- **Distinct-account/event-row separation:** Pass
- **Cycle double-count prevention:** Pass for the generated account-month summary
- **Definitive exact-subscription/date-key churned-MRR assignment:** Pass as
  an explicit no-match result under the strict mapping rule
- **Customer-level churned-MRR and customer churn:** Pass under the month-end
  lifecycle definition
- **Gross/net revenue churn:** Pass as provisional monthly lifecycle KPIs

Production sign-off still requires confirmation of the end-date boundary,
subscription effective-date meaning, reactivation semantics and
event-to-subscription linkage.
