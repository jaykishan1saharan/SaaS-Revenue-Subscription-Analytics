# Churn Events and Feature Usage Load Validation
## SaaS Revenue & Subscription Analytics

**Validation scope:** Churn event and feature usage loads, plus reference checks to parent account and subscription datasets.

---

# Part A: Churn Events

**Source file:** `ravenstack_churn_events.csv`  
**Target table:** `public.churn_events`  
**Expected rows:** 600  
**Actual rows:** 600  
**Status:** Passed

## 1. Load summary

| Metric | Result |
|---|---:|
| Expected rows | 600 |
| Actual rows | 600 |
| Difference | 0 |
| Duplicate rows | 0 |
| Missing cells | 148 |
| Load status | Passed |

## 2. Primary key validation

| Column | Constraint | Result |
|---|---|---|
| `churn_event_id` | Primary key | Verified |
| Duplicate `churn_event_id` values | 0 | Passed |

## 3. Missing value review

| Column | Missing count | Percentage |
|---|---:|---:|
| `feedback_text` | 148 | 24.67% |

Missing feedback text values are retained as NULL, which is acceptable because the field is optional and the raw source does not require text for every churn event.

## 4. Foreign key and reference validation

Reference checks against the parent datasets show no orphan records.

| Child table | Foreign key | Parent table | Orphan count |
|---|---|---|---:|
| `churn_events` | `account_id` | `accounts` | 0 |
| `subscriptions` | `account_id` | `accounts` | 0 |

The subscription-to-account reference check confirms every subscription belongs to a valid account record; this is a critical dependency ahead of feature-usage joins.

## 5. Numeric range review

| Column | Minimum | Maximum |
|---|---:|---:|
| `refund_amount_usd` | 0.00 | 392.92 |

No negative refund amounts were observed.

## 6. Date validation

| Validation | Invalid records | Status |
|---|---:|---|
| Churn date before associated account signup date | 0 | Passed |

No churn event date was earlier than its account signup date.

## 7. Churn event conclusion

All 600 churn event records were loaded successfully.

Primary key uniqueness and account references were verified. Missing feedback text was preserved as NULL, and no invalid churn-date/account-date relationships were found.

---

# Part B: Feature Usage

**Source file:** `ravenstack_feature_usage.csv`  
**Target table:** `public.feature_usage`  
**Expected rows:** 25,000  
**Actual rows:** 25,000  
**Status:** Passed

## 1. Load summary

| Metric | Result |
|---|---:|
| Expected rows | 25,000 |
| Actual rows | 25,000 |
| Difference | 0 |
| Duplicate rows | 0 |
| Missing cells | 0 |
| Load status | Passed |

## 2. Primary key validation

| Column | Constraint | Result |
|---|---|---|
| `usage_record_id` | Generated primary key | Verified |
| Duplicate `usage_record_id` values | 0 | Passed |

The raw source file includes a naturally repeated `usage_id` field; it was retained for source traceability but not used as the database primary key.

## 3. Source identifier review

| Metric | Result |
|---|---:|
| Total records | 25,000 |
| Unique source IDs | 24,979 |
| Repeated source IDs | 21 |

The 21 repeated `usage_id` values were reviewed and retained because they do not invalidate the dataset; they simply indicate a non-unique source identifier that should not be used as a primary key.

## 4. Missing value validation

| Validation | Missing count | Status |
|---|---:|---|
| All `feature_usage` columns | 0 | Passed |

No missing values were found in the feature usage dataset.

## 5. Foreign key validation

| Child table | Foreign key | Parent table | Orphan count |
|---|---|---|---:|
| `feature_usage` | `subscription_id` | `subscriptions` | 0 |

The feature-usage records are fully aligned to valid subscription records.

## 6. Numeric range review

| Column | Minimum | Maximum |
|---|---:|---:|
| `usage_count` | 0 | 26 |
| `error_count` | 0 | 8 |

No negative values were observed in the numeric usage metrics.

## 7. Feature usage conclusion

All 25,000 feature usage records were loaded successfully.

The generated `usage_record_id` primary key was verified, repeated source `usage_id` values were identified and retained, and all tested subscription relationships returned zero orphan records.

---

## Final combined summary

| Dataset | Expected rows | Actual rows | Status |
|---|---:|---:|---|
| Churn events | 600 | 600 | Passed |
| Feature usage | 25,000 | 25,000 | Passed |
| Total | 25,600 | 25,600 | Passed |

**Overall status:** Loaded and validated.

## Reference integrity verdict

The following reference checks passed:

- `churn_events.account_id` → `accounts.account_id`: 0 orphan rows
- `subscriptions.account_id` → `accounts.account_id`: 0 orphan rows
- `feature_usage.subscription_id` → `subscriptions.subscription_id`: 0 orphan rows

This confirms the churn and feature-usage data are aligned with the account and subscription dimensions needed for downstream retention, adoption, and churn analysis.
