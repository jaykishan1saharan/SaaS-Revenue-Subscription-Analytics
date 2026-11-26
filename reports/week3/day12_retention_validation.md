# Week 3 Day 12 — Retention validation and denominator review

**Scope:** Validate the existing overall and first-paid-plan retention outputs against account-level cohort assignments and customer-month activity.

**Observation cutoff:** December 2024.
**Retention unit:** Distinct eligible `account_id`, not subscriptions.

## Summary

The overall retention matrix passes the denominator, percentage-bound, and cohort-size checks. Recalculation from `customer_month_activity.csv` reproduces all 300 observed overall cohort-age percentages at the stored four-decimal precision. The other 276 matrix cells are unavailable future windows and are correctly NULL rather than zero.

Month 0 is not 100% for two cohorts because Month 0 is measured at month-end, while the denominator includes every account whose first qualifying paid subscription started in that month. Those values are consistent with the activity data, not denominator errors. Plan-level results reconcile to 500 cohort accounts, but individual cohort-plan cells are frequently small; treat plan results as descriptive, not inferential.

## Overall denominator and percentage checks

| Check | Result |
|---|---:|
| Cohort-assignment rows | 500 |
| Distinct assigned accounts | 500 |
| Duplicate account assignments | 0 |
| Cohort months | 24 |
| Sum of distinct account counts across cohort months | 500 |
| Matrix rows / cohort-size matches | 24 / 24 |
| Observed overall cohort-age cells | 300 |
| Future/unobserved cells stored as NULL | 276 |
| Observed cells with numerator ≤ denominator | 300 / 300 |
| Observed retention range | 92.8571%–100.0000% |
| Observed values outside [0%, 100%] | 0 |

Numerators were independently counted as distinct active accounts for each cohort month and activity month. Every observed percentage matches `100 × numerator / cohort size`, rounded to four decimal places. The assignment file repeats `cohort_size` on each account row; it must not be summed row-by-row. Cohort size is checked as a distinct-account count within each cohort month.

### Month 0

All 24 cohorts have an observed Month 0 value. Twenty-two have full month-end retention; two have accounts that qualified for the cohort but were not active at that month-end:

| Cohort | Month 0 retained / cohort size | Retention |
|---|---:|---:|
| 2023-04 | 14 / 15 | 93.3333% |
| 2024-01 | 21 / 22 | 95.4545% |

The Month 0 denominator is cohort entry based on first paid start month; the numerator is month-end active accounts. These are different events, so Month 0 need not equal 100%.

## Early, late, sparse, and incomplete windows

- **Early cohort:** January 2023 has 2 accounts and is observable through Month 23 (December 2024). Its Month 0, 6, 12, and 23 values are all 2/2. With only two accounts, a single account changes its rate by 50 percentage points.
- **Late cohort:** December 2024 has 26 accounts and Month 0 is 26/26. Month 6 and Month 12 are not yet observable and remain NULL.
- **Sparse cohorts:** Using `cohort size ≤ 10` as a review threshold, January, February, and March 2023 are sparse (sizes 2, 7, and 10). Their rates are descriptive and sensitive to individual accounts.
- **Month 6:** 18 of 24 cohorts have a complete window, through the June 2024 cohort. The six July–December 2024 cohorts correctly have NULL Month 6.
- **Month 12:** 12 of 24 cohorts have a complete window, through the December 2023 cohort. The 12 cohorts from January–December 2024 correctly have NULL Month 12.

The matrix uses NULL for an unobserved future month. It must not be interpreted as zero retention or included in an average as zero.

## Multiple-subscription and account-grain checks

| Check | Result |
|---|---:|
| Source subscriptions / accounts | 5,000 / 500 |
| Subscription records per account | 2–19 |
| Customer-month activity rows | 5,115 |
| Duplicate `account_id × activity_month` rows | 0 |
| Account-month rows with more than one active paid subscription | 4,459 / 5,115 |
| Accounts with more than one active paid subscription in any month | 497 |
| Maximum active paid subscriptions on one account-month | 16 |

The activity file aggregates active subscriptions to one row per account and month. Numerators therefore count distinct accounts; counting subscription rows would overstate retention, especially given the high frequency of concurrent subscriptions.

## First-paid-plan comparison review

The plan output assigns plan from the account's first qualifying paid subscription. Its cohort sizes sum to the same 500 accounts. There are 71 non-empty cohort-plan cells out of 72 possible; January 2023 has no Enterprise cohort accounts, so that zero-size cell is absent rather than a missing observation.

| First-paid plan | Full cohort accounts | Month 0 retained / n | Month 6 retained / mature n | Month 12 retained / mature n |
|---|---:|---:|---:|---:|
| Basic | 164 | 164 / 164 | 115 / 115 | 74 / 74 |
| Enterprise | 172 | 171 / 172 | 107 / 107 | 46 / 46 |
| Pro | 164 | 163 / 164 | 111 / 111 | 66 / 66 |

Month 6 counts include only cohorts through June 2024; Month 12 counts include only cohorts through December 2023. All displayed plan denominators are positive, and each observed plan retention percentage corresponds to an integer numerator no greater than its cohort-plan denominator.

**Stability and interpretation flags**

- 27 of 71 non-empty cohort-plan cells have five or fewer accounts (cell sizes range from 1 to 17; median 7). A single account can materially change rates in these cells; avoid ranking or interpreting individual cohort-plan percentages.
- The mature-window plan totals above are larger, but remain descriptive comparisons. Do not infer statistical significance or that plan caused retention differences: cohort vintage and sample sizes differ, the observation window is limited, and lifecycle/end-date semantics remain provisional.
- The observed 100% Month 6 and Month 12 rates in the mature plan groups should be reported with their denominators and cutoff dates, not as evidence of universally perfect retention.

## Validation basis and limitations

The checks used the existing `customer_cohort_assignments.csv`, `customer_month_activity.csv`, `cohort_retention_matrix.csv`, and `cohort_retention_by_plan.csv`, with source subscriptions used to verify first-paid-plan attribution. The saved overall and plan retention outputs matched fresh in-memory calculations from the current cohort-analysis logic; no existing source or data files were changed for this review.

The activity definition uses the provisional inclusive end-date month-end rule. The source does not establish whether `end_date` is inclusive, so these checks validate arithmetic and denominator consistency under the existing rule; they do not resolve lifecycle semantics or certify the retention definition for final external reporting.
