cat > docs/erd/support_tickets_erd.md
ckets

## Table: support_tickets

| Column | Proposed Data Type | Constraint |
|---|---|---|
| ticket_id | VARCHAR(20) | PRIMARY KEY, NOT NULL |
| account_id | VARCHAR(20) | FOREIGN KEY, NOT NULL |
| submitted_at | TIMESTAMP | NOT NULL |
| closed_at | TIMESTAMP | NOT NULL |
| resolution_time_hours | NUMERIC(8,2) | NOT NULL |
| priority | VARCHAR(20) | NOT NULL |
| first_response_time_minutes | INTEGER | NOT NULL |
| satisfaction_score | NUMERIC(3,1) | NULL |
| escalation_flag | BOOLEAN | NOT NULL |

## Keys and Relationships

- Primary key: ticket_id
- Foreign key: account_id references accounts.account_id
- One account can have multiple support tickets.
- Suggested indexes: account_id, submitted_at, priority.

## Data Quality Evidence

- Total records: 2,000
- Unique ticket IDs: 2,000
- Unmatched account references: 0
- Missing satisfaction scores: 825 (41.25%)
- No duplicate complete rows.
- No records removed during cleaning.
- Missing satisfaction scores retained without imputation.

## Implementation Note

These are proposed schema definitions, not deployed database constraints.