
# Day 4 — Support Tickets Database Load Validation

## 1. Objective

Validate the cleaned Support Tickets dataset before database analysis and execute initial SQL exploration queries using SQLite.

## 2. Dataset Information

- Source: `data/interim/support_tickets_clean.csv`
- Records loaded: 2,000
- Columns: 9
- Database: SQLite
- Table: `support_tickets`
- Missing satisfaction scores: 825

## 3. Data Validation Results

All 10 validation checks passed.

| Validation | Result |
|---|---|
| Expected row count | PASS |
| Unique ticket IDs | PASS |
| Non-null ticket IDs | PASS |
| Non-null account IDs | PASS |
| Account references | PASS |
| Non-negative resolution time | PASS |
| Non-negative first response time | PASS |
| Satisfaction score range (1–5) | PASS |
| Closed timestamp after submission | PASS |
| No duplicate complete rows | PASS |

Unmatched account references: 0.

## 4. SQLite Load Verification

The cleaned CSV was loaded into the SQLite table `support_tickets`.

- Loaded records: 2,000
- SQL exploration queries executed: 12
- Query execution errors: 0
- Final database row count: 2,000

## 5. Initial SQL Findings

### Ticket distribution by priority

| Priority | Ticket Count |
|---|---:|
| Urgent | 514 |
| High | 510 |
| Medium | 491 |
| Low | 485 |

### Average resolution time

| Priority | Average Hours |
|---|---:|
| High | 36.96 |
| Low | 36.35 |
| Medium | 35.59 |
| Urgent | 34.57 |

### Average first response time

| Priority | Average Minutes |
|---|---:|
| High | 91.44 |
| Low | 91.15 |
| Medium | 85.86 |
| Urgent | 85.53 |

### Escalation distribution

- Non-escalated: 1,905
- Escalated: 95

### Satisfaction score distribution

| Score | Responses |
|---|---:|
| 3 | 396 |
| 4 | 405 |
| 5 | 374 |

There are 825 missing satisfaction scores. These were retained as NULL and excluded from the score distribution.

### Account-wise ticket volume

The highest observed ticket count for one account was 11.

### Data consistency

- Invalid negative duration records: 0
- Closed-before-submission records: 0
- Duplicate ticket records: 0

## 6. Observations

1. Urgent tickets have the highest ticket volume (514).
2. High-priority tickets have the highest average resolution time (36.96 hours).
3. Urgent tickets have the lowest average resolution time (34.57 hours).
4. High-priority tickets also have the highest average first response time (91.44 minutes).
5. Escalated tickets represent 95 of 2,000 records.
6. Satisfaction scores are missing for 41.25% of records, which limits satisfaction analysis.
7. All account references passed the validation check.

These are descriptive findings and do not establish causal relationships.

## 7. Deliverables

- `sql/03_initial_exploration.sql`
- `src/run_support_ticket_sql.py`
- `reports/support_tickets_load_validation.md`
- `data/interim/support_tickets_day4.db`

## 8. Conclusion

The cleaned Support Tickets dataset passed all 10 validation checks and was successfully loaded into SQLite with 2,000 records. All 12 initial SQL exploration queries executed successfully. The dataset is ready for further analytical exploration, subject to the documented missing satisfaction values.
