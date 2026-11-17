
# Support Tickets Entity Relationship Diagram

```mermaid
erDiagram
    ACCOUNTS ||--o{ SUPPORT_TICKETS : has

    ACCOUNTS {
        VARCHAR account_id PK
    }

    SUPPORT_TICKETS {
        VARCHAR ticket_id PK
        VARCHAR account_id FK
        TIMESTAMP submitted_at
        TIMESTAMP closed_at
        NUMERIC resolution_time_hours
        VARCHAR priority
        INTEGER first_response_time_minutes
        NUMERIC satisfaction_score
        BOOLEAN escalation_flag
    }
```

## Relationship Explanation

- One account can have zero or many support tickets.
- Each support ticket belongs to one account.
- `ticket_id` is the proposed primary key.
- `account_id` is the proposed foreign key referencing `accounts.account_id`.
