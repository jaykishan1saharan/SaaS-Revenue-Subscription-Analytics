# Churn Event Rule Review

**Scope:** Interpret `churn_events` for event counts and distinct-account churn reporting.  
**Source:** `data/raw/ravenstack_churn_events.csv`  
**Status:** Proposed reporting rule; confirm the business definitions before treating it as a production churn KPI.

## Executive summary

The source has **600 event records** with unique `churn_event_id` values, but only **352 distinct `account_id` values**. An event count is therefore not a count of distinct customers lost. The `is_reactivation` flag is the available signal for separating a reactivation record from a candidate churn record: 539 rows are `False` and 61 are `True`. Under the provisional rule below, these are respectively candidate churn events and reactivation events—not 600 churns.

There are **339 distinct accounts** with at least one non-reactivation record. This is a candidate distinct-account churn count, not a verified count of unique customers lost: the source does not establish that one account equals one customer or that every non-reactivation row is a confirmed cancellation.

## Event grain and repeated accounts

Treat one row, identified by `churn_event_id`, as one **recorded event**. The event ID is unique in the observed file, but the exact business definition of an event is not documented. Do not deduplicate on `account_id`, `churn_date`, or their combination.

| Observed measure | Count |
|---|---:|
| Event records | 600 |
| Distinct accounts with any event | 352 |
| Accounts with more than one event | 175 |
| Events belonging to those repeated accounts | 423 |
| Maximum events for one account | 5 |
| Accounts with at least one non-reactivation record | 339 |
| Accounts with at least one reactivation record | 55 |
| Accounts with both record types | 42 |

One account has two different event IDs on the same date, both marked non-reactivation, with reason `pricing` and different refund amounts and feedback. Keep both records in the event count pending source-owner confirmation; do not infer that either is a duplicate.

## Event-date use

Use `churn_date` to assign a **recorded event** to a reporting date or period. It is populated and parseable in all 600 rows, covering **2023-01-25 through 2024-12-31**. Count and group records by that date without shifting them based on account status or subscription dates.

The field name alone does not establish whether `churn_date` is the effective cancellation date, the date the event was recorded, or another business date. It is day-grain, and no tie-breaker or ordering contract is documented for multiple events on the same day. Therefore:

- Label date-based output as recorded-event activity until the date definition is confirmed.
- Do not infer the effective date of lost recurring revenue from this field alone.
- Treat same-day events as separate records in descriptive event counts; flag them for lifecycle sequencing review.

## Proposed reactivation treatment

For provisional reporting, interpret `is_reactivation=True` as a **reactivation transition**, not as another churn:

1. Count all rows in a separate recorded-event total.
2. Count `is_reactivation=False` rows as **candidate churn-event records**.
3. Count `is_reactivation=True` rows as **reactivation-event records** and exclude them from the candidate churn-event count.
4. For a distinct-account measure over a stated period, count each `account_id` with at least one candidate churn event once. A practical provisional label is “distinct accounts with a recorded candidate churn event,” not “customers lost.”
5. A reactivation does not erase the earlier churn event. It starts a new active spell in a lifecycle model; if another valid non-reactivation event occurs after it, count that as another churn event. Do not count the reactivation itself as churn.

The raw flag sequence is not sufficient to certify this lifecycle logic. Among the 55 accounts with a reactivation record, 42 also have a non-reactivation record. A date-order check finds 29 accounts with a non-reactivation record before a reactivation record and 18 with a reactivation before a later non-reactivation record; these groups can overlap where an account has multiple events. This supports separating event types, but does not prove that the records represent valid state transitions.

For an eventual lifecycle-based metric, order events by confirmed effective date and apply a state rule: a valid churn moves an active account to churned; a valid reactivation moves a churned account back to active; only a subsequent valid churn creates another churn transition. Resolve same-day order and flag inconsistencies with the source owner. Do not infer an initial active/churned state from this file alone. Distinct accounts lost in a reporting period should still be counted once per period, while event-level churn transitions can count more than once.

## Refund interpretation

`refund_amount_usd` is present on every row and ranges from **$0.00 to $392.92**. The observed sum is **$8,652.25**: 458 rows have zero and 142 have a positive amount. Reactivation-flagged rows also carry amounts (sum **$531.34**), so a nonzero refund is not, by itself, evidence that the row is a churn event.

Treat the field as a recorded amount for that event row only. Its name suggests USD, but currency, payment status, refund timing, and whether values are event-level versus cumulative are unconfirmed. Do not label its sum as revenue lost, churned MRR, or net revenue impact; do not use it to identify churn or reactivation.

## Data limitations and reporting guardrails

- The file describes recorded churn-related events, not a complete account-state history. It has no explicit activation/start event, effective-date definition, or validated lifecycle sequence.
- `account_id` is the available distinct entity key. The data does not establish that an account corresponds one-to-one with a customer/logo.
- `is_reactivation` is a boolean marker with undefined semantics; validation is needed to confirm that `True` means a reactivation transition on that row.
- Same-day events need an ordering or reconciliation rule for lifecycle metrics. Keep source records intact until clarified.
- The source spans 2023 and 2024, with 73 records in 2023 and 527 in 2024. Exposure and period completeness are unknown, so raw counts are not churn rates or evidence of a trend.
- The account-level `churn_flag` has no documented as-of date and can disagree with historical event rows; do not use it to overwrite or validate event classification without its temporal definition.
- Refund semantics are unconfirmed. Refund amounts do not measure recurring revenue loss.

## Recommended output labels

| Output | Recommended definition / label |
|---|---|
| Total recorded events | Count of source rows (`churn_event_id`) |
| Candidate churn-event records | Count of rows where `is_reactivation=False` |
| Reactivation-event records | Count of rows where `is_reactivation=True` |
| Distinct accounts with recorded candidate churn | Distinct `account_id` among non-reactivation rows in the stated period; not a churn rate or necessarily distinct customers lost |
| Recorded refund amount | Sum of row-level `refund_amount_usd`, clearly separated from recurring revenue loss |

**Related findings:** [Week 1 churn and feature-usage findings](../churn_feature_usage_week1_findings.md), [churn and feature-usage quality findings](../churn_feature_usage_quality_findings.md), and [churn-event data dictionary](../../docs/data_dictionary_churn_events_feature_usage.md).
