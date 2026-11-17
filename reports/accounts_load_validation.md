# Accounts Load Validation

**Dataset:** `accounts_clean.csv`  
**Validation date:** 2026-11-17  
**Target table:** `accounts` (proposed table name)  
**Validation scope:** File-level pre-load validation. No database load was performed as part of this check.

## 1. Validation summary

| Validation check | Result | Status |
|---|---:|---|
| Row count | 500 | PASS |
| Column count | 10 | PASS |
| Missing cells | 0 | PASS |
| Exact duplicate rows | 0 | PASS |
| Null `account_id` values | 0 | PASS |
| Duplicate `account_id` values | 0 | PASS |
| Invalid non-empty `signup_date` values | 0 | PASS |
| `signup_date` range | 2023-01-02 to 2024-12-31 | PASS |

All file-level checks above passed. The cleaned file contains 500 records and 10 columns.

## 2. Column structure

The cleaned dataset contains these columns:

- `account_id`
- `account_name`
- `industry`
- `country`
- `signup_date`
- `referral_source`
- `plan_tier`
- `seats`
- `is_trial`
- `churn_flag`

## 3. Data type checks

| Column | CSV/Pandas type |
|---|---|
| `account_id` | `object` |
| `account_name` | `object` |
| `industry` | `object` |
| `country` | `object` |
| `signup_date` | `object` |
| `referral_source` | `object` |
| `plan_tier` | `object` |
| `seats` | `int64` |
| `is_trial` | `bool` |
| `churn_flag` | `bool` |

`signup_date` is stored in the CSV as ISO-formatted text (`YYYY-MM-DD`). CSV files do not preserve a native date type; cast it to `DATE` when loading into the database.

## 4. Suggested database load validation

After loading the file into the database table `accounts`, run the checks below in the database client. These are validation queries to execute after the load; they are **not evidence that a database load has already occurred**.

```sql
-- 1. Confirm loaded row count
SELECT COUNT(*) AS total_rows
FROM accounts;

-- 2. Check null account identifiers
SELECT COUNT(*) AS null_account_ids
FROM accounts
WHERE account_id IS NULL;

-- 3. Check duplicate account identifiers
SELECT account_id, COUNT(*) AS id_count
FROM accounts
GROUP BY account_id
HAVING COUNT(*) > 1;

-- 4. Check missing values in key account fields
SELECT
    SUM(CASE WHEN account_name IS NULL THEN 1 ELSE 0 END) AS null_account_names,
    SUM(CASE WHEN signup_date IS NULL THEN 1 ELSE 0 END) AS null_signup_dates,
    SUM(CASE WHEN plan_tier IS NULL THEN 1 ELSE 0 END) AS null_plan_tiers
FROM accounts;
```

Expected results based on the validated CSV:
- `COUNT(*)` should equal **500**.
- `null_account_ids` should equal **0**.
- The duplicate-ID query should return **no rows**.
- The listed required-field null counts should equal **0**.

## 5. Load acceptance criteria

The accounts load can be accepted when:
1. The database row count matches the cleaned CSV row count (500).
2. `account_id` is non-null and unique.
3. Required account fields have no unexpected null values.
4. `signup_date` is stored as a database `DATE` (or an equivalent date type).
5. The loaded table's column names and meanings match the cleaned CSV.

## 6. Current status and limitation

- **File-level validation:** PASS.
- **Database load validation:** PENDING — run the SQL checks after importing `accounts_clean.csv` into the target database.
- **Raw source:** Preserved separately; this report does not modify the raw dataset.
