# Support Tickets Cleaning Log

**Project:** SaaS Revenue & Subscription Analytics
**Owner:** Lav Kumar
**Stage:** Day 3 — Data Cleaning and Schema Design

## 1. Source and Output

- Source: `data/raw/ravenstack_support_tickets.csv`
- Output: `data/interim/support_tickets_clean.csv`
- Original rows: 2,000
- Output rows: 2,000
- Original columns: 9
- Removed rows: 0

## 2. Cleaning and Validation Actions

- Text fields: leading/trailing whitespace standardized.
- Ticket IDs: uniqueness and missing-value checks performed.
- Timestamps: parsed, validated and standardized.
- Numeric fields: type conversion and validation performed.
- Satisfaction scores: original missing values preserved.
- Priority values: checked against low, medium, high and urgent.
- Account references: validated against accounts.account_id.
- Raw CSV: not modified.

## 3. Whitespace Standardization

| Column | Values changed |
|---|---:|
| `ticket_id` | 0 |
| `account_id` | 0 |
| `submitted_at` | 0 |
| `closed_at` | 0 |
| `priority` | 0 |

## 4. Missing Values Before and After

| Column | Before | After |
|---|---:|---:|
| `ticket_id` | 0 | 0 |
| `account_id` | 0 | 0 |
| `submitted_at` | 0 | 0 |
| `closed_at` | 0 | 0 |
| `resolution_time_hours` | 0 | 0 |
| `priority` | 0 | 0 |
| `first_response_time_minutes` | 0 | 0 |
| `satisfaction_score` | 825 | 825 |
| `escalation_flag` | 0 | 0 |

## 5. Validation Results

- Duplicate complete rows before cleaning: 0
- Duplicate ticket IDs after cleaning: 0
- Invalid timestamp sequences: 0
- Invalid account references: 0
- Unexpected priorities: None
- Satisfaction scores outside 1–5: 0

## 6. Data Preservation

- No rows were removed.
- No satisfaction scores were imputed.
- No IDs were regenerated.
- No business values were intentionally changed.
- Original raw data was preserved.

## 7. Conclusion

The support ticket dataset was processed into a separate interim CSV after validation. All 2,000 records were retained. Missing satisfaction scores were preserved. See the source quality audit for the original findings.
