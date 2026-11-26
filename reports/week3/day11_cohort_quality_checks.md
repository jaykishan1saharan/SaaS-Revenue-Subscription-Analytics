# Week 3 Day 11 — Cohort data quality checks

    **Source:** `data/raw/ravenstack_accounts.csv` and `data/raw/ravenstack_subscriptions.csv`

    **Cohort rule:** First non-trial subscription with positive numeric MRR per account; cohort month is its start month.

**Lifecycle note:** The source has no subscription status field. A same-day start/end record is retained as cohort-eligible when otherwise valid, but logged for review because end-date semantics are unconfirmed.

## Input profile and findings

Counts below are source-row counts unless labeled as distinct accounts. Issue categories overlap; a row can have multiple reason codes in the exclusion/review log.

| Check | Count |
|---|---:|
| source subscription rows | 5,000 |
| distinct nonblank subscription IDs | 5,000 |
| rows with missing subscription IDs | 0 |
| rows with duplicate subscription IDs | 0 |
| account rows | 500 |
| account rows with missing IDs | 0 |
| account rows with duplicate IDs | 0 |
| subscription rows with missing account IDs | 0 |
| subscription rows with unknown account references | 0 |
| subscription rows with ambiguous account references | 0 |
| missing start dates | 0 |
| invalid nonmissing start dates | 0 |
| invalid nonmissing end dates | 0 |
| end dates before start dates | 0 |
| same-day start/end dates (review) | 13 |
| trial rows | 778 |
| missing or invalid trial flags | 0 |
| missing MRR rows | 0 |
| invalid nonmissing MRR rows | 0 |
| non-positive MRR rows | 778 |
| churn/end-date mismatches (review) | 0 |
| conflicting upgrade/downgrade flags (review) | 23 |
| excluded subscription rows | 778 |
| rows with review findings (may also be excluded) | 36 |
| eligible paid subscription rows | 4,222 |
| eligible distinct accounts | 500 |
| cohort assignment rows | 500 |
| distinct assigned accounts | 500 |
| sum of distinct-account cohort sizes | 500 |

### Cohort-size reconciliation

| Cohort month | Distinct eligible accounts |
|---|---:|
| 2023-01 | 2 |
| 2023-02 | 7 |
| 2023-03 | 10 |
| 2023-04 | 15 |
| 2023-05 | 13 |
| 2023-06 | 18 |
| 2023-07 | 15 |
| 2023-08 | 25 |
| 2023-09 | 14 |
| 2023-10 | 18 |
| 2023-11 | 23 |
| 2023-12 | 26 |
| 2024-01 | 22 |
| 2024-02 | 17 |
| 2024-03 | 25 |
| 2024-04 | 24 |
| 2024-05 | 28 |
| 2024-06 | 31 |
| 2024-07 | 27 |
| 2024-08 | 24 |
| 2024-09 | 31 |
| 2024-10 | 22 |
| 2024-11 | 37 |
| 2024-12 | 26 |

| Reconciliation | Result |
|---|---|
| Sum of cohort sizes equals distinct eligible accounts (500) | PASS (500) |
| Every eligible account has exactly one cohort assignment | PASS (500 assigned) |
| Eligible accounts are counted at account grain, not subscription grain | PASS |

## Eligibility, exclusion and review rules

- Excluded from paid cohort qualification: missing/duplicate subscription IDs; missing, unknown or ambiguous account references; missing/invalid start date; invalid or reversed end date; missing/invalid trial flag; trial rows; and missing, invalid or non-positive MRR.
- Review-only findings: same-day start/end, churn-flag/end-date disagreement, missing or invalid churn flags, invalid upgrade/downgrade flags, and simultaneous upgrade and downgrade flags. A review-only row remains cohort-eligible if it passes the paid-cohort requirements; its uncertainty is not silently discarded.
- NULL end dates are allowed. The month-end active-subscription boundary is not used to determine initial cohort membership.
- `trial_subscription` and `non_positive_mrr` can both be recorded for the same row. The reason list is intentionally non-exclusive.

## Exclusion/review record file

`reports/week3/day11_excluded_or_review_records.csv` contains one row for every source record with an exclusion or review finding. `source_table` identifies the source CSV; `source_row_number` is its 1-based data-row position. `disposition` is `exclude` if any exclusion reason applies; otherwise it is `review`. `cohort_eligible` indicates whether a subscription row can contribute to the eligible cohort population.

The report and log are standalone review deliverables based on the source inputs. Cohort counts are descriptive and do not resolve pending lifecycle semantics.
