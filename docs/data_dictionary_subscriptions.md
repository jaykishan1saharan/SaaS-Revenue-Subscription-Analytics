# Data Dictionary — Subscriptions

## 1. Dataset details

- **Source:** `data/raw/ravenstack_subscriptions.csv`
- **Proposed table:** `subscriptions`
- **Grain:** One row per subscription record, identified by `subscription_id`.
- **Observed size:** 5,000 rows × 14 columns.
- **Related table:** `accounts`, sourced from `data/raw/ravenstack_accounts.csv`.
- **Data nature:** Synthetic dataset, attributed in repository documentation to River @ Rivalytics.
- **Raw data handling:** Source file was inspected read-only and remains unchanged.

Types below are inferred from raw CSV values and describe recommended logical storage types, not a claim that a database table has already been created.

## 2. Column definitions

| Column | Recommended type | Meaning | Nullability / observed values |
|---|---|---|---|
| `subscription_id` | VARCHAR / TEXT | Unique identifier for a subscription record. | Required; 5,000 distinct values; candidate primary key. |
| `account_id` | VARCHAR / TEXT | Identifier of the account associated with the subscription. | Required; 500 distinct values; candidate FK to `accounts.account_id`. |
| `start_date` | DATE | Date the subscription began. | Required; observed range 2023-01-09 to 2024-12-31. |
| `end_date` | DATE | Date the subscription ended, when populated. | Nullable; 4,514 nulls and 486 populated values. Observed populated range 2023-04-05 to 2024-12-31. |
| `plan_tier` | VARCHAR / TEXT | Subscription plan category. | Required; Basic, Pro, Enterprise. |
| `seats` | INTEGER | Number of seats associated with the subscription. | Required; numeric integer values. |
| `mrr_amount` | NUMERIC / DECIMAL | Monthly recurring revenue amount associated with the subscription. | Required; observed range 0–33,830. Currency/unit is not specified. |
| `arr_amount` | NUMERIC / DECIMAL | Annual recurring revenue amount associated with the subscription. | Required; observed range 0–405,960. All rows equal 12 × MRR. Currency/unit is not specified. |
| `is_trial` | BOOLEAN | Indicates whether the subscription record is a trial. | Required; True 778, False 4,222. |
| `upgrade_flag` | BOOLEAN | Indicates an upgrade event/condition for the subscription. | Required; True 529, False 4,471. Exact event timing is not defined. |
| `downgrade_flag` | BOOLEAN | Indicates a downgrade event/condition for the subscription. | Required; True 218, False 4,782. Exact event timing is not defined. |
| `churn_flag` | BOOLEAN | Indicates the dataset's churn marker for the subscription. | Required; True 486, False 4,514. This is the available lifecycle indicator; no explicit status column exists. |
| `billing_frequency` | VARCHAR / TEXT | Billing cadence recorded for the subscription. | Required; monthly 2,539, annual 2,461. |
| `auto_renew_flag` | BOOLEAN | Indicates whether automatic renewal is enabled. | Required; True 4,005, False 995. |

## 3. Subscription lifecycle interpretation

The CSV does **not** contain a column named `subscription_status`. Lifecycle interpretation must use the available fields without pretending that the raw file contains statuses it does not have.

| Observed combination | Count | Safe interpretation |
|---|---:|---|
| `churn_flag = True` and `end_date` populated | 486 | Churn-marked records with an end date |
| `churn_flag = False` and `end_date` null | 4,514 | Records with no recorded end date and no churn flag |

These two fields align perfectly in the inspected data. A blank `end_date` should be retained as NULL; it is not an invalid date. Confirm whether the end date means cancellation, expiry, or another closure event before deriving additional lifecycle labels.

Other lifecycle-related attributes:
- `is_trial`: trial indicator; all 778 trial rows have zero MRR and ARR.
- `upgrade_flag`: upgrade marker.
- `downgrade_flag`: downgrade marker.
- `auto_renew_flag`: renewal setting.

The file does not specify event timestamps or whether upgrade/downgrade flags represent historical events or current state.

## 4. Candidate keys and relationships

### Candidate primary key

- **Column:** `subscription_id`
- **Validation:** 5,000 rows, 5,000 distinct values, zero missing values.
- **Recommendation:** Candidate primary key for the subscriptions table.

### Candidate foreign key

- **Column:** `account_id`
- **Parent:** `accounts.account_id`
- **Validation:** All 500 distinct account IDs used by subscriptions exist in the accounts file; zero unmatched references.
- **Cardinality:** One account to many subscriptions. There are 5,000 subscription rows across 500 accounts; observed count per account is 2–19.

### Plan reference

- `plan_tier` is present as a category, with values Basic, Pro, and Enterprise.
- No `plan_id` column or separate plans file/table is present in the inspected source.
- The accounts file also contains `plan_tier`; do not treat it as a plan foreign key without a formal plan dimension and agreed relationship rules.

## 5. Billing and revenue notes

- `billing_frequency` has two observed values: `monthly` and `annual`.
- `mrr_amount` and `arr_amount` are numeric and non-null in all rows.
- Every row satisfies `arr_amount = 12 × mrr_amount`.
- 778 rows have zero MRR and ARR; all 778 are marked as trials.
- The CSV has no currency code, currency symbol, tax field, discount field, invoice amount, or payment amount. Do not assume a currency or equate these fields with cash collected.
- Confirm the intended definition, currency, and unit for MRR/ARR before external reporting.

## 6. Date and data-quality validation

| Validation | Result |
|---|---:|
| Missing `start_date` | 0 |
| Missing `end_date` | 4,514 |
| Invalid date strings | 0 |
| End date earlier than start date | 0 |
| Missing subscription IDs | 0 |
| Duplicate subscription IDs | 0 |
| Missing account IDs | 0 |
| Unmatched account references | 0 |
| MRR/ARR arithmetic mismatches | 0 |

## 7. Suggested relational schema

| Column | Suggested PostgreSQL type | Constraint |
|---|---|---|
| subscription_id | TEXT | PRIMARY KEY |
| account_id | TEXT | NOT NULL; FOREIGN KEY REFERENCES accounts(account_id) |
| start_date | DATE | NOT NULL |
| end_date | DATE | NULL |
| plan_tier | TEXT | NOT NULL |
| seats | INTEGER | NOT NULL |
| mrr_amount | NUMERIC(12,2) | NOT NULL (confirm source units/currency first) |
| arr_amount | NUMERIC(12,2) | NOT NULL (confirm source units/currency first) |
| is_trial | BOOLEAN | NOT NULL |
| upgrade_flag | BOOLEAN | NOT NULL |
| downgrade_flag | BOOLEAN | NOT NULL |
| churn_flag | BOOLEAN | NOT NULL |
| billing_frequency | TEXT | NOT NULL; observed monthly/annual |
| auto_renew_flag | BOOLEAN | NOT NULL |

The suggested decimal scale is a database-design recommendation; the source CSV contains integer-formatted amount values. Final DDL should be reviewed with the project team.

## 8. Open questions for review

1. What currency and unit do `mrr_amount` and `arr_amount` represent?
2. Does `end_date` represent cancellation date, subscription expiry, or any end-of-term event?
3. Are upgrade/downgrade flags current-state indicators or historical event markers?
4. Should `churn_flag` be interpreted strictly as subscription churn, and how should reactivations be represented?
5. Is a separate plan dimension intended for a later project stage?

---

**Inspection result:** Subscription lifecycle fields, candidate keys, plan categories, billing cadence, revenue fields, observed flag values, and account linkage are documented. The raw CSV was not modified.
