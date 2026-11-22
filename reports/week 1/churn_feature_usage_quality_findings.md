# Churn Events and Feature Usage — Data Quality Findings

**Scope:** `data/raw/ravenstack_churn_events.csv` and `data/raw/ravenstack_feature_usage.csv`  
**Related files checked:** accounts and subscriptions CSVs  
**Audit type:** Read-only profile and cross-file validation

> No raw data was changed, removed, or imputed. Findings that depend on undefined event or lifecycle semantics are marked for confirmation rather than treated as proven errors.

## 1. Executive summary

- Both files have complete required identifiers and valid, parseable event dates. Churn events have 148 missing `feedback_text` values (24.67%); feature usage has no missing cells.
- All 600 churn-event account references and all 25,000 usage subscription references match their respective parent files.
- The churn-event ID is unique (600/600). Feature usage has 21 repeated `usage_id` values affecting 42 rows. Neither file contains exact duplicate rows.
- Feature usage has substantial date mismatches against its linked subscription periods: 19,142 rows are before `start_date` (76.57%); 290 rows are after a populated `end_date` (1.16%). These are high-priority items to resolve before lifecycle-based usage analysis.
- Three `(subscription_id, usage_date, feature_name)` combinations occur twice. The pair of churn events for one account on the same date also merits review.

## 2. Dataset profile

| Check | Churn events | Feature usage |
|---|---:|---:|
| Rows / columns | 600 / 9 | 25,000 / 8 |
| Missing cells | 148, all in `feedback_text` | 0 |
| Candidate event/usage ID | `churn_event_id`: 600 distinct | `usage_id`: 24,979 distinct |
| Rows with repeated candidate ID | 0 | 42 (21 IDs, each appearing twice) |
| Exact duplicate rows | 0 | 0 |
| Date parsing failures | 0 | 0 |
| Distinct valid parent references | 352 accounts; all matched | 4,967 subscriptions; all matched |

## 3. Findings

### CH-01 — Missing churn feedback

**Priority: Medium**

- `feedback_text` is blank for 148 of 600 churn events (24.67%); the other eight churn columns have no missing values.
- The nonblank feedback consists of four values: `too expensive` (161), `missing features` (155), `switched to competitor` (136), plus the 148 blanks.
- Missing feedback can bias text-based summaries. Confirm whether feedback is optional or conditionally collected; preserve blanks rather than imputing text.

### CH-02 — Repeated account/date event

**Priority: Medium — confirm event grain**

- There are 600 events for 352 accounts. Repeated accounts are present (up to five events for an account), which may be legitimate given the `is_reactivation` field (61 events are marked `True`).
- One account has two different event IDs on the same date (2024-11-19). Both rows have reason `pricing` and `is_reactivation=False`, but have different refund amounts and feedback. There are no exact duplicate rows.
- Confirm whether same-day events are valid separate events, multiple records for one event, or a source duplication. Do not remove either record without that decision.

### CH-03 — Event-date coverage and account-status interpretation

**Priority: Low / review context**

- All 600 `churn_date` values parse successfully and fall between 2023-01-25 and 2024-12-31. Events span 311 distinct dates; no event predates its account's `signup_date` (three occur on the signup date).
- Event counts are uneven over time: 73 events in 2023 and 527 in 2024; December 2024 has 117 events. This may reflect the synthetic data's construction or a genuine time pattern; validate coverage/exposure before interpreting it as a churn trend.
- Of the 352 accounts with events, 277 have `churn_flag=False` in the accounts file; those accounts account for 465 event rows. This can be consistent with historical events or reactivation, but the account flag's time meaning is not specified. Confirm before using that flag to classify historical events.

### FU-01 — Repeated usage identifiers

**Priority: High — candidate key not reliable**

- `usage_id` has 24,979 distinct values across 25,000 rows: 21 identifiers each occur twice (42 affected rows).
- In each repeated-ID pair, the rows refer to different subscriptions and dates. There are no exact duplicate rows.
- Do not use `usage_id` as a primary key or deduplicate by it until the source identifier behavior is clarified. If records must be uniquely stored, obtain a validated source key or define a surrogate key.

### FU-02 — Usage dates outside linked subscription periods

**Priority: High — confirm date semantics**

- Of the 25,000 usage rows, 19,142 (76.57%) are dated before the linked subscription's `start_date`. This affects 4,783 of the 5,000 subscriptions (95.66%). These rows precede the start by 1–728 days (median 287 days).
- A further 290 rows (1.16%) occur after a populated `end_date`, affecting 164 subscriptions. All 290 are linked to subscriptions with `churn_flag=True`; they occur 1–582 days after end (median 69 days).
- Two rows fall exactly on the linked `end_date`.
- If `start_date`/`end_date` bound the period in which a subscription can generate usage and `usage_date` is the event date, the before-start and after-end records are temporally inconsistent. Confirm whether dates are snapshots, reporting periods, or attached to subscription records that do not represent the historical usage period. Resolve the intended rule before filtering or attributing usage to active subscriptions.

### FU-03 — Repeated subscription/date/feature combinations

**Priority: Medium — confirm observation grain**

- Three `(subscription_id, usage_date, feature_name)` combinations each appear twice, affecting six rows. The file has 24,997 distinct combinations among 25,000 rows.
- No exact duplicate rows were found, so these are not identical record copies. If the intended grain is one row per subscription, date, and feature, these combinations violate that grain; if multiple observations per day are allowed, the key is not unique by design.
- Confirm the intended usage observation interval and aggregate/deduplication rules before reporting activity at this grain.

### FU-04 — Beta flag varies within each feature name

**Priority: Low / confirm flag meaning**

- All 40 observed `feature_name` values occur with both `is_beta_feature=True` and `False` in different rows; 2,544 rows are marked beta and 22,456 are not.
- If beta status is a fixed property of a feature, this is inconsistent categorization. If the flag records time-varying rollout status, the variation may be legitimate. Confirm the flag's time semantics before grouping a feature as beta or non-beta.

## 4. Usage patterns and value checks

- Usage dates parse across the full 731-day period from 2023-01-01 through 2024-12-31, with observations on every calendar day. Monthly row counts range from 944 to 1,137; daily counts range from 12 to 53. These are counts of recorded rows, not necessarily distinct users or sessions.
- All 40 feature labels are populated. Feature record counts range from 563 (`feature_23`) to 659 (`feature_12` and `feature_32`). Labels are generic; the files do not provide feature descriptions.
- `usage_count` ranges from 0 to 26, `usage_duration_secs` from 0 to 12,696, and `error_count` from 0 to 8. No negative values were found. Two rows have both zero usage and zero duration; the other 24,998 have positive values for both. Seventeen rows have `error_count > usage_count`; whether that is invalid depends on the units and definitions of the two measures.
- 33 subscriptions have no matching usage rows. This is an absence of observed usage, not necessarily a missing-reference defect.

## 5. Referential integrity

| Relationship | Source rows checked | Unmatched |
|---|---:|---:|
| `churn_events.account_id` → `accounts.account_id` | 600 | 0 |
| `feature_usage.subscription_id` → `subscriptions.subscription_id` | 25,000 | 0 |

No invalid parent references were found in the tested relationships.

## 6. Recommended follow-up

1. Confirm whether `usage_date` is an event date and whether subscription dates delimit valid usage. Investigate both before-start and after-end cases against the source definitions.
2. Resolve the uniqueness contract for `usage_id` and the intended granularity of daily subscription-feature observations.
3. Confirm whether churn events may repeat on the same account/date and how event history relates to the account-level `churn_flag`.
4. Confirm whether beta status is time-varying and whether error counts are expected to be bounded by usage counts.
5. Confirm that blank churn feedback is an expected optional field; do not impute it without an approved rule.

## 7. Method and limitations

The audit parsed dates, counted missing values and exact duplicate rows, profiled identifiers and observed values, and joined event references to the provided parent files. Usage-period checks compare each usage row's `usage_date` with the `start_date` and populated `end_date` of its referenced subscription. Those comparisons flag records for review but do not establish the business meaning of the dates. No source records were changed.
