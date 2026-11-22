# Churn Events and Feature Usage Dataset Inventory — RavenStack

## Inspection scope

| Field | Details |
|---|---|
| Project | SaaS Revenue & Subscription Analytics |
| Dataset | RavenStack Synthetic SaaS Dataset |
| Inventory owner | Madhupriya |
| Review status | Prepared|
| Source files | `data/raw/ravenstack_churn_events.csv`, `data/raw/ravenstack_feature_usage.csv` |
| Raw files modified? | No — inspected read-only |

The dataset is described as synthetic in the project source notes. See [`docs/dataset_source.md`](../docs/dataset_source.md) for attribution and source-verification notes.

## File inventory

| File | Proposed table | Rows (excluding header) | Columns | Size |
|---|---|---:|---:|---:|
| `data/raw/ravenstack_churn_events.csv` | `churn_events` | 600 | 9 | 44,630 bytes |
| `data/raw/ravenstack_feature_usage.csv` | `feature_usage` | 25,000 | 8 | 1,400,898 bytes |

## Churn events

### Headers

`churn_event_id`, `account_id`, `churn_date`, `reason_code`, `refund_amount_usd`, `preceding_upgrade_flag`, `preceding_downgrade_flag`, `is_reactivation`, `feedback_text`

### Column observations

| Column | Inferred type | Missing / blank | Distinct values | Notes |
|---|---|---:|---:|---|
| `churn_event_id` | String identifier | 0 | 600 | Unique across all 600 rows; candidate primary key. |
| `account_id` | String identifier | 0 | 352 | Repeats across events; candidate FK to `accounts.account_id`. |
| `churn_date` | Date | 0 | 311 | Observed dates span 2023-01-25 to 2024-12-31; no invalid date strings observed. |
| `reason_code` | Categorical string | 0 | 6 | Reason category; preserve as text unless categories are formally constrained. |
| `refund_amount_usd` | Decimal numeric | 0 | 142 | Refund amount in USD as named; observed range 0.00–392.92. |
| `preceding_upgrade_flag` | Boolean | 0 | 2 | True/False values. |
| `preceding_downgrade_flag` | Boolean | 0 | 2 | True/False values. |
| `is_reactivation` | Boolean | 0 | 2 | True/False values. |
| `feedback_text` | Text | 148 | 4 | Blank in 148 rows; retain as nullable text. |

### Candidate identifiers and relationship

| Column | Potential role | Evidence |
|---|---|---|
| `churn_event_id` | Candidate primary key | 600 nonblank values, all 600 distinct; no exact duplicate rows. |
| `account_id` | Candidate foreign key | 352 distinct nonblank account IDs; all 352 match `accounts.account_id` (zero unmatched rows). |

The `account_id` values repeat because an account can have multiple churn-event records. The file does not establish whether repeated events represent separate cancellation episodes, retries, or another event definition; confirm the intended grain before analysis.

## Feature usage

### Headers

`usage_id`, `subscription_id`, `usage_date`, `feature_name`, `usage_count`, `usage_duration_secs`, `error_count`, `is_beta_feature`

### Column observations

| Column | Inferred type | Missing / blank | Distinct values | Notes |
|---|---|---:|---:|---|
| `usage_id` | String identifier | 0 | 24,979 | Not unique: 21 values occur more than once (42 rows in those groups); not a validated primary key. |
| `subscription_id` | String identifier | 0 | 4,967 | Repeats across usage records; candidate FK to `subscriptions.subscription_id`. |
| `usage_date` | Date | 0 | 731 | Observed dates span 2023-01-01 to 2024-12-31; no invalid date strings observed. |
| `feature_name` | Categorical string | 0 | 40 | Feature label; preserve as text. |
| `usage_count` | Integer | 0 | 27 | Usage quantity; observed range 0–26. |
| `usage_duration_secs` | Integer | 0 | 4,168 | Usage duration in seconds; observed range 0–12,696. |
| `error_count` | Integer | 0 | 9 | Count of errors; observed range 0–8. |
| `is_beta_feature` | Boolean | 0 | 2 | True/False values. |

### Candidate identifiers and relationship

| Column / combination | Potential role | Evidence |
|---|---|---|
| `usage_id` | Possible identifier, not a validated key | 24,979 distinct values across 25,000 rows; each of its 21 duplicate groups contains non-identical records. |
| `subscription_id` | Candidate foreign key | 4,967 distinct subscription IDs; all match `subscriptions.subscription_id` (zero unmatched rows). |
| `subscription_id`, `usage_date`, `feature_name` | Possible composite key, not unique | 24,997 distinct combinations across 25,000 rows. |

Repeated subscriptions are expected for multiple usage records. The observed `usage_id` collisions and repeated subscription/date/feature combinations mean neither `usage_id` alone nor the proposed composite can safely be used as a primary key without clarification or a source-data correction.

## Summary and recommendations

1. Retain `churn_event_id` as the churn-event primary-key candidate; preserve IDs as text.
2. Link churn events to accounts through `account_id`, and feature usage to subscriptions through `subscription_id`. Both references matched their respective raw parent files completely in this inspection.
3. Do not treat `usage_id` or (`subscription_id`, `usage_date`, `feature_name`) as a unique key based on the observed data.
4. Parse date fields as DATE, flags as BOOLEAN, and usage counts/duration as integers. Keep `feedback_text` nullable and `refund_amount_usd` as a decimal type.
5. Confirm the event grain, the duplicated usage-ID generation/meaning, and whether multiple rows for the same subscription/date/feature are valid before defining database constraints or aggregating usage.
6. Preserve both raw CSV files unchanged; document any cleaning or deduplication decisions separately.

**Completion:** Headers, row/column counts, observed identifier uniqueness, candidate parent links, and selected data-quality checks have been recorded. 
