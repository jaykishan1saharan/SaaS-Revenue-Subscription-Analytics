# Data Dictionary — Churn Events and Feature Usage

## Dataset details

- **Source files:** `data/raw/ravenstack_churn_events.csv` and `data/raw/ravenstack_feature_usage.csv`
- **Proposed tables:** `churn_events` and `feature_usage`
- **Observed sizes:** 600 rows × 9 columns; 25,000 rows × 8 columns, respectively.
- **Data nature:** Synthetic dataset as described in [`dataset_source.md`](dataset_source.md).
- **Raw data handling:** Both files were inspected read-only and remain unchanged.

Types and meanings below are inferred from the CSV values and field names. They are recommendations for logical storage, not a claim that database tables have been created. Blank CSV cells are described as missing/null.

## Churn events

**Grain:** One row per recorded churn event in the source. `churn_event_id` is unique in the observed file; exact business meaning of a churn event and treatment of reactivations should be confirmed.

| Column | Recommended type | Meaning | Nullability / observed values |
|---|---|---|---|
| `churn_event_id` | TEXT | Identifier for the churn-event record. | Required; 600 distinct values across 600 rows; candidate primary key. |
| `account_id` | TEXT | Account associated with the churn event. | Required; 352 distinct values; repeats across events. All values match `accounts.account_id`; candidate foreign key. |
| `churn_date` | DATE | Date recorded for the churn event. | Required; observed range 2023-01-25 to 2024-12-31; no invalid date strings observed. |
| `reason_code` | TEXT | Coded churn reason. | Required; 6 distinct observed values. |
| `refund_amount_usd` | NUMERIC / DECIMAL | Refund amount, apparently denominated in USD based on the column name. | Required; 142 distinct values; observed range 0.00–392.92. Validate currency and amount semantics with the data owner. |
| `preceding_upgrade_flag` | BOOLEAN | Indicates whether an upgrade preceded the event. | Required; two observed values (True/False). Timing window is not specified. |
| `preceding_downgrade_flag` | BOOLEAN | Indicates whether a downgrade preceded the event. | Required; two observed values (True/False). Timing window is not specified. |
| `is_reactivation` | BOOLEAN | Indicates whether the record is associated with a reactivation. | Required; two observed values (True/False). Exact event interpretation is not specified. |
| `feedback_text` | TEXT | Free-text feedback associated with the event. | Nullable; 148 blank cells; 4 distinct nonblank values. |

### Churn-event key and relationship notes

- `churn_event_id` is a candidate primary key based on 600 nonblank, distinct values in 600 rows.
- `account_id` is a candidate foreign key to `accounts.account_id`. All 352 distinct IDs (all 600 rows) matched the parent file; no unmatched references were observed.
- There are 600 rows for 352 accounts, so account identifiers repeat. Do not interpret one row per account.
- No exact duplicate rows were observed.

## Feature usage

**Grain:** One row per recorded feature-usage observation in the source. The precise recording interval or meaning of a row is not specified.

| Column | Recommended type | Meaning | Nullability / observed values |
|---|---|---|---|
| `usage_id` | TEXT | Identifier assigned to a feature-usage record. | Required; 24,979 distinct values in 25,000 rows. 21 values each repeat; not a validated primary key. |
| `subscription_id` | TEXT | Subscription associated with the usage record. | Required; 4,967 distinct values; candidate foreign key to `subscriptions.subscription_id`. All values matched the parent file. |
| `usage_date` | DATE | Date of the feature-usage observation. | Required; observed range 2023-01-01 to 2024-12-31; no invalid date strings observed. |
| `feature_name` | TEXT | Feature associated with the usage record. | Required; 40 distinct observed values. |
| `usage_count` | INTEGER | Count of uses or usage events represented by the record. | Required; 27 distinct numeric values; observed range 0–26. Confirm the precise counting unit. |
| `usage_duration_secs` | INTEGER | Usage duration in seconds. | Required; 4,168 distinct numeric values; observed range 0–12,696. |
| `error_count` | INTEGER | Number of errors associated with the usage observation. | Required; 9 distinct numeric values; observed range 0–8. |
| `is_beta_feature` | BOOLEAN | Indicates whether the feature was designated beta. | Required; two observed values (True/False). |

### Feature-usage key and relationship notes

- `usage_id` is not unique: 21 ID values repeat, involving 42 rows. In every repeated-ID group, the rows are not identical.
- `subscription_id` repeats across usage observations; all 4,967 distinct IDs matched `subscriptions.subscription_id` (zero unmatched rows).
- The combination (`subscription_id`, `usage_date`, `feature_name`) has 24,997 distinct values across 25,000 rows, so it is not unique either.
- No exact duplicate rows were observed.
- Do not impose a primary-key constraint or deduplicate on `usage_id` until the source's intended identifier and collision behavior are confirmed.

## Data-quality summary

| Check | Churn events | Feature usage |
|---|---:|---:|
| Rows | 600 | 25,000 |
| Columns | 9 | 8 |
| Blank cells | 148 (`feedback_text`) | 0 |
| Candidate event/usage ID distinctness | `churn_event_id`: 600 / 600 | `usage_id`: 24,979 / 25,000 |
| Exact duplicate rows | 0 | 0 |
| Parent IDs matched | `account_id`: 600 / 600 rows | `subscription_id`: 25,000 / 25,000 rows |

## Suggested relational constraints

| Table | Column | Suggested constraint |
|---|---|---|
| `churn_events` | `churn_event_id` | Candidate `PRIMARY KEY` |
| `churn_events` | `account_id` | `NOT NULL`; `FOREIGN KEY` to `accounts(account_id)` |
| `feature_usage` | `subscription_id` | `NOT NULL`; `FOREIGN KEY` to `subscriptions(subscription_id)` |
| `feature_usage` | `usage_id` | No uniqueness constraint until duplicate-ID semantics are resolved |


**Inspection result:** Field names, inferred types, observed missingness, key candidates, and parent-table links are documented. 