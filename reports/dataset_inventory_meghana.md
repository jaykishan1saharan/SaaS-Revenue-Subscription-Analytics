# Subscription Dataset Inventory — RavenStack SaaS Analytics

## 1. Inspection scope

| Field | Details |
|---|---|
| Project | SaaS Revenue & Subscription Analytics |
| Dataset | RavenStack Synthetic SaaS Dataset |
| Source file | `data/raw/ravenstack_subscriptions.csv` |
| Related reference file | `data/raw/ravenstack_accounts.csv` |
| Proposed table | `subscriptions` |
| Inventory owner | Meghana |
| Review status | Prepared; team review pending |
| Raw file modified? | No — inspected read-only |

The repository's raw-data README attributes the synthetic dataset to River @ Rivalytics. See `docs/dataset_source.md` for attribution and source-verification notes.

## 2. File-level inventory

| Field | Observed result |
|---|---:|
| Rows (excluding header) | 5,000 |
| Columns | 14 |
| File size | 432,565 bytes |
| Missing values | 4,514, all in `end_date` |
| Distinct subscription IDs | 5,000 |
| Distinct account IDs referenced | 500 |
| Duplicate subscription IDs | 0 |
| Unmatched account references | 0 |

## 3. Column inventory and observed data types

Types are inferred from CSV values. Recommended storage: identifiers/categories as text, date-only values as DATE, flags as BOOLEAN, and counts/amounts as numeric types.

| Column | Inferred type | Missing | Distinct values | Notes |
|---|---|---:|---:|---|
| `subscription_id` | string | 0 | 5,000 | Candidate primary key |
| `account_id` | string | 0 | 500 | FK candidate to accounts |
| `start_date` | date | 0 | 625 | Subscription start |
| `end_date` | date | 4,514 | 208 | Nullable lifecycle end date |
| `plan_tier` | string/category | 0 | 3 | Basic, Pro, Enterprise |
| `seats` | integer | 0 | 123 | Seats on subscription |
| `mrr_amount` | integer/numeric | 0 | 306 | Monthly recurring revenue amount |
| `arr_amount` | integer/numeric | 0 | 306 | Annual recurring revenue amount |
| `is_trial` | boolean | 0 | 2 | Trial indicator |
| `upgrade_flag` | boolean | 0 | 2 | Upgrade indicator |
| `downgrade_flag` | boolean | 0 | 2 | Downgrade indicator |
| `churn_flag` | boolean | 0 | 2 | Churn/lifecycle indicator; no separate status column |
| `billing_frequency` | string/category | 0 | 2 | Monthly or annual |
| `auto_renew_flag` | boolean | 0 | 2 | Auto-renewal indicator |

## 4. Lifecycle, plan and billing observations

### Lifecycle indicator

There is no explicit `subscription_status` field. The observed `churn_flag` values are:

| churn_flag | Rows |
|---|---:|
| `True` | 486 |
| `False` | 4,514 |

- All 486 rows with `churn_flag = True` have a populated `end_date`.
- All 4,514 rows with `churn_flag = False` have a blank `end_date`.
- This is the observed encoding, not evidence of a richer status taxonomy such as paused, past_due, or cancelled.
- A blank `end_date` is consistent with an ongoing subscription in this dataset and should not automatically be treated as a data error.

### Plan and account references

| Field | Observed values |
|---|---|
| `plan_tier` | Basic (1,602), Pro (1,675), Enterprise (1,723) |
| `account_id` | 500 distinct IDs; all match the accounts file |
| Separate `plan_id` / plans table | Not present in the inspected subscription CSV |

The accounts file also contains `account_id` and `plan_tier`. Plan tier is a descriptive category, not a validated foreign key to a separate plan dimension.

### Dates and billing

| Field | Observed result |
|---|---|
| `start_date` range | 2023-01-09 to 2024-12-31 |
| `end_date` range (non-null) | 2023-04-05 to 2024-12-31 |
| Invalid date strings | 0 |
| End dates earlier than start dates | 0 |
| `billing_frequency` | monthly (2,539), annual (2,461) |
| `mrr_amount` range | 0 to 33,830 |
| `arr_amount` range | 0 to 405,960 |

All observed rows satisfy `arr_amount = mrr_amount × 12`. Confirm the intended business definition and currency/unit with the dataset owner before financial reporting. No currency column is present.

## 5. Candidate keys and relationships

| Table | Column | Role | Validation |
|---|---|---|---|
| subscriptions | `subscription_id` | Candidate primary key | 5,000 distinct values across 5,000 rows; no missing values |
| subscriptions | `account_id` | Candidate foreign key | All 500 distinct values found in `accounts.account_id`; no unmatched values |

The account-to-subscription relationship is one-to-many: 500 accounts are referenced by 5,000 subscription rows. Observed subscriptions per account range from 2 to 19 (average 10).

## 6. Initial data-quality checks

| Check | Result |
|---|---|
| Missing `subscription_id` / `account_id` | 0 |
| Duplicate `subscription_id` | 0 |
| Missing values in other columns | 4,514 in `end_date`; 0 elsewhere |
| Invalid date strings | 0 |
| `end_date < start_date` | 0 |
| Account foreign-key mismatches | 0 |
| ARR not equal to 12 × MRR | 0 |
| Zero MRR / ARR rows | 778 |
| Trial rows | 778 |
| Trial rows with zero MRR | 778 |
| Non-trial rows with zero MRR | 0 |

Zero revenue for trial records is consistent across the inspected rows. Do not remove these records: they are meaningful for trial-to-paid and lifecycle analysis.

## 7. Recommendations and limitations

1. Use `subscription_id` as the subscriptions primary-key candidate and `account_id` as a foreign key to `accounts.account_id`.
2. Preserve identifier columns as text.
3. Parse `start_date` and non-null `end_date` as DATE; retain null end dates.
4. Convert the five flag fields and `is_trial` to BOOLEAN after controlled parsing.
5. Use a suitable numeric type for MRR and ARR; confirm currency and scale before presenting monetary totals.
6. Do not invent a `subscription_status` field or a plan dimension. If a reporting status is derived, document the exact rule separately.
7. Confirm whether `churn_flag` is a subscription-level churn marker and whether `end_date` means cancellation, expiration, or another end event.
8. Preserve `data/raw/ravenstack_subscriptions.csv` unchanged; place cleaning or derived fields in a separate processed dataset.

## 8. Completion

Prepared from a read-only inspection of the raw subscription CSV and an account-key cross-check. The raw CSV was not edited. Team lead review and confirmation of currency, lifecycle semantics, and plan definitions remain pending.
