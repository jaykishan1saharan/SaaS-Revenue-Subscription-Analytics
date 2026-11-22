# Support Tickets — Data Quality Audit

**Project:** SaaS Revenue & Subscription Analytics
**Auditor:** Lav Kumar
**Audit stage:** Day 2 — EDA and Data Quality Audit
**Source:** `data/raw/ravenstack_support_tickets.csv`
**Reference:** `data/raw/ravenstack_accounts.csv`

> This is a read-only audit. No raw records were modified, deleted, or imputed.

## 1. Dataset Overview

- Total records: 2,000
- Total columns: 9
- Distinct ticket IDs: 2,000
- Distinct account IDs in tickets: 492
- Exact duplicate rows: 0

| Column | Data type |
|---|---|
| `ticket_id` | `object` |
| `account_id` | `object` |
| `submitted_at` | `object` |
| `closed_at` | `object` |
| `resolution_time_hours` | `float64` |
| `priority` | `object` |
| `first_response_time_minutes` | `int64` |
| `satisfaction_score` | `float64` |
| `escalation_flag` | `bool` |

## 2. Missing Value Analysis

| Column | Missing count | Missing percentage |
|---|---:|---:|
| `ticket_id` | 0 | 0.00% |
| `account_id` | 0 | 0.00% |
| `submitted_at` | 0 | 0.00% |
| `closed_at` | 0 | 0.00% |
| `resolution_time_hours` | 0 | 0.00% |
| `priority` | 0 | 0.00% |
| `first_response_time_minutes` | 0 | 0.00% |
| `satisfaction_score` | 825 | 41.25% |
| `escalation_flag` | 0 | 0.00% |

## 3. Ticket ID Validation

- Missing ticket IDs: 0
- Unique ticket IDs: 2,000
- Rows participating in duplicate ticket IDs: 0
- Number of distinct duplicated ticket IDs: 0
- No duplicate ticket IDs detected.

## 4. Categorical Distribution

### priority

| Value | Count |
|---|---:|
| urgent | 514 |
| high | 510 |
| medium | 491 |
| low | 485 |

### escalation_flag

| Value | Count |
|---|---:|
| False | 1,905 |
| True | 95 |

- Expected priority categories: high, low, medium, urgent
- Unexpected priority categories: None

## 5. Timestamp Validation

- `submitted_at` missing values: 0
- `submitted_at` unparseable non-null values: 0
- `closed_at` missing values: 0
- `closed_at` unparseable non-null values: 0
- Tickets closed before submission: 0

Date coverage:
- `submitted_at`: 2023-01-02 00:00:00 to 2024-12-31 00:00:00
- `closed_at`: 2023-01-03 03:00:00 to 2024-12-31 19:00:00

## 6. Numeric and Business Rule Checks

### resolution_time_hours
- Missing: 0
- Minimum: 1.0
- Maximum: 72.0
- Negative values: 0

### first_response_time_minutes
- Missing: 0
- Minimum: 1
- Maximum: 180
- Negative values: 0

### satisfaction_score
- Missing: 825
- Minimum: 3.0
- Maximum: 5.0
- Negative values: 0

- Satisfaction scores outside 1–5: 0
- Zero resolution times: 0
- Zero first-response times: 0

## 7. Resolution Duration Consistency

- Records with comparable timestamps and resolution duration: 2,000
- Records differing by more than 1 hour: 0
- A one-hour tolerance is used for this diagnostic comparison; differences require investigation, not automatic correction.

## 8. Account Reference Validation

- Account records in parent dataset: 500
- Ticket records checked: 2,000
- Matched ticket account references: 2,000
- Unmatched non-null account references: 0
- Distinct unmatched account IDs: 0

## 9. Audit Findings Summary

- Exact duplicate rows and duplicate ticket IDs were checked separately.
- Missing satisfaction scores must not automatically be treated as errors; they may represent tickets without customer feedback.
- Priority categories were compared against the expected values: low, medium, high and urgent.
- Timestamp ordering and duration consistency were investigated.
- Account references were checked against the accounts dataset.
- No source records were modified or removed.

## 10. Limitations and Next Steps
- Investigate every unexpected category, invalid timestamp, negative metric or unmatched reference, if present.
- Confirm business rules with the team before classifying unusual records as errors.
- Retain all original records for the subsequent cleaning stage.
- This report covers support tickets only; other members are auditing their assigned datasets.
