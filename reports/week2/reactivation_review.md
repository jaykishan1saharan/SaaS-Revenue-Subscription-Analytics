# Reactivation and Subscription MRR Review

- **Status:** Provisional event-sequence and join review; not a certified churn KPI.
- **Inputs:** `ravenstack_churn_events.csv` and `ravenstack_subscriptions.csv`
- **Reproducible analysis:** [subscription_movements.py](../../src/subscription_movements.py)
- **SQL review:** [04_subscription_movements.sql](../../sql/04_subscription_movements.sql)

## Summary

| Measure | Observed result |
|---|---:|
| Recorded event rows | 600 |
| Accounts with recorded events | 352 |
| Non-reactivation candidate churn rows | 539 |
| Reactivation-flagged rows | 61 |
| Reactivation rows with any earlier candidate-churn event in account history | 34 |
| Reactivation rows immediately after one earlier candidate-churn event | 29 |
| Reactivation rows after another reactivation row | 6 |
| Reactivation rows with no earlier event in this file | 26 |
| Candidate churn rows immediately after a reactivation row | 18 |
| Accounts with a possible churn/reactivation/repeated-churn sequence | 5 |
| Event rows in an ambiguous same-account/date group | 2 |

The sequence-supported reactivations below have one preceding event on a
strictly earlier date, and that preceding event is a non-reactivation row.
This is evidence that the rows may form a churn-then-reactivation sequence;
it does not prove that the account was active before the first event or that
either date is the effective transition date. Of the 34 reactivation rows with
any earlier candidate-churn record, 29 immediately follow one unique
non-reactivation event. The other 5 follow an intervening reactivation; a sixth
consecutive reactivation has no earlier candidate-churn record. These are not
counted as direct churn-to-reactivation evidence.

## Sequence-supported reactivation rows

| Churn event ID | Account ID | Reactivation date |
|---|---|---|
| C-92f889 | A-956988 | 2024-12-30 |
| C-f81017 | A-271f46 | 2024-08-09 |
| C-7cd070 | A-13466a | 2024-04-18 |
| C-480232 | A-31ab9a | 2024-09-23 |
| C-043665 | A-b2225d | 2024-06-27 |
| C-f24343 | A-425e76 | 2023-09-03 |
| C-9d36da | A-bcf664 | 2024-08-17 |
| C-860574 | A-4e44e8 | 2024-10-11 |
| C-a761a8 | A-50bb9f | 2024-09-12 |
| C-07be44 | A-751c58 | 2024-11-05 |
| C-08d3b3 | A-3f9cc0 | 2024-12-21 |
| C-08b126 | A-0cc442 | 2024-09-26 |
| C-2ce12e | A-712426 | 2024-11-26 |
| C-b6bc5f | A-bb1486 | 2024-11-23 |
| C-486194 | A-2ebb4b | 2024-12-29 |
| C-f5a863 | A-e7a1e2 | 2024-09-30 |
| C-e49016 | A-b7724f | 2024-09-01 |
| C-151fb1 | A-fd7ad3 | 2024-12-19 |
| C-118bea | A-65aeb5 | 2024-12-02 |
| C-f1268a | A-32728c | 2024-07-19 |
| C-9b6151 | A-2bc93d | 2024-08-15 |
| C-f6f8a5 | A-2d1036 | 2024-10-28 |
| C-3efa9b | A-cdf020 | 2024-11-07 |
| C-917c1d | A-39868b | 2024-05-24 |
| C-44918f | A-9208f0 | 2024-09-15 |
| C-36d17e | A-ac85cd | 2024-12-13 |
| C-1f8fd5 | A-e351e1 | 2024-12-04 |
| C-474d36 | A-6f50ae | 2024-02-26 |
| C-0d5e99 | A-68f37c | 2024-06-29 |

## Possible repeated churn/reactivation cycles

These are ordered by `churn_date`; `C` is a non-reactivation candidate churn
row and `R` is a reactivation-flagged row. They are possible cycles, not
validated state transitions. Account `A-0cc442` has two consecutive
reactivation flags; they are retained as separate records rather than treated
as two confirmed transitions.

| Account ID | Ordered event sequence |
|---|---|
| A-0cc442 | 2024-07-20 C `C-55f4ec` → 2024-09-26 R `C-08b126` → 2024-10-06 R `C-020446` → 2024-10-23 C `C-47694c` |
| A-425e76 | 2023-08-10 C `C-901c1a` → 2023-09-03 R `C-f24343` → 2023-12-25 C `C-75ddda` → 2024-10-22 C `C-ae47d1` |
| A-751c58 | 2024-09-17 C `C-0f0386` → 2024-11-05 R `C-07be44` → 2024-12-16 C `C-1dce6d` |
| A-e7a1e2 | 2024-09-08 C `C-4ab0e2` → 2024-09-30 R `C-f5a863` → 2024-12-11 C `C-e2ecb7` |
| A-fd7ad3 | 2024-11-12 C `C-59499c` → 2024-11-23 C `C-2299d7` → 2024-12-19 R `C-151fb1` → 2024-12-31 C `C-e20d30` |

There is one same-day group with two non-reactivation events for account
`A-cc102e` on 2024-11-19 (`C-e20cc6`, `C-ce47da`). Both remain separate
recorded rows; their within-day ordering and whether either is a duplicate are
unresolved.

## Subscription MRR mapping

`churn_events` has no `subscription_id`. The analysis therefore treats an
exact `(account_id, churn_date) = (account_id, end_date)` match as a
**candidate date-key association**, never as a verified event-to-subscription
foreign key. Reactivation rows are excluded from churn MRR matching.

| Candidate churn-event mapping result | Rows |
|---|---:|
| No exact same-account/end-date match | 532 |
| One event with multiple exact-date subscriptions | 1 |
| Multiple events on the same account/date; order/mapping ambiguous | 2 |
| One-to-one exact-date candidate subscription match | 4 |

The one ambiguous subscription match is event `C-5328d6` for account
`A-0b0d6d` on 2024-12-31. Two subscriptions end that day (`S-6ef81d`,
MRR 475; `S-6f47c5`, MRR 2,587), so neither is assigned to the event.

| Event ID | Account ID | Event / end date | Candidate subscription | Candidate subscription MRR | Other subscription rows not ended by event date |
|---|---|---|---|---:|---:|
| C-57871b | A-6a4e2d | 2024-07-19 | S-9b8421 | 0 | 8 |
| C-47694c | A-0cc442 | 2024-10-23 | S-bd1912 | 1,843 | 9 |
| C-97ab4b | A-82d8a6 | 2024-12-29 | S-038f6f | 0 | 13 |
| C-8d2855 | A-8bde0c | 2024-12-30 | S-4fe9b6 | 1,225 | 16 |

These four exact-date candidates sum to **3,068 in source MRR**, grouped by
recorded event month as July 2024: 0, October 2024: 1,843, and December 2024:
1,225. This is a candidate departing-subscription amount only—not confirmed
churned MRR. Each matched account also has 8–16 other subscription rows whose
end date is null or later than the event date. Since null `end_date` semantics
are unconfirmed, those rows prevent a defensible claim that the event represents
the account's full departure. **No account-level churned MRR is attributed.**

Monthly grouping uses `churn_date` as the recorded event date. The source does
not confirm that it is the effective cancellation date or the period in which
recurring MRR should be recognized. Event refunds are not part of any MRR
amount or mapping.

## Limitations

- `is_reactivation` is a marker, not a validated state transition.
- The source does not establish an initial account state, an effective-date
  contract, or the order of same-day events.
- Account IDs may have multiple subscriptions; churn events do not identify
  which subscription ended.
- `end_date` and `churn_flag` align in the inspected subscription data, but
  the meaning of `end_date` and null end dates still requires confirmation.
- Treat sequence and exact-date matches as review evidence, not final churn or
  revenue metrics.
