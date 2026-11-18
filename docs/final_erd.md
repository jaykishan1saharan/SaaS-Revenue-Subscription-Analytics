erDiagram

    ACCOUNTS ||--o{ SUBSCRIPTIONS : has
    ACCOUNTS ||--o{ CHURN_EVENTS : experiences
    ACCOUNTS ||--o{ SUPPORT_TICKETS : raises
    SUBSCRIPTIONS ||--o{ FEATURE_USAGE : records

    ACCOUNTS {
        TEXT account_id PK
        TEXT account_name
        TEXT industry
        TEXT country
        DATE signup_date
        TEXT referral_source
        TEXT plan_tier
        INTEGER seats
        BOOLEAN is_trial
        BOOLEAN churn_flag
    }

    SUBSCRIPTIONS {
        TEXT subscription_id PK
        TEXT account_id FK
        DATE start_date
        DATE end_date
        TEXT plan_tier
        INTEGER seats
        NUMERIC mrr_amount
        NUMERIC arr_amount
        BOOLEAN is_trial
        BOOLEAN upgrade_flag
        BOOLEAN downgrade_flag
        BOOLEAN churn_flag
        TEXT billing_frequency
        BOOLEAN auto_renew_flag
    }

    CHURN_EVENTS {
        TEXT churn_event_id PK
        TEXT account_id FK
        DATE churn_date
        TEXT reason_code
        NUMERIC refund_amount_usd
        BOOLEAN preceding_upgrade_flag
        BOOLEAN preceding_downgrade_flag
        BOOLEAN is_reactivation
        TEXT feedback_text
    }

    FEATURE_USAGE {
        BIGINT usage_record_id PK
        TEXT usage_id
        TEXT subscription_id FK
        DATE usage_date
        TEXT feature_name
        INTEGER usage_count
        INTEGER usage_duration_secs
        INTEGER error_count
        BOOLEAN is_beta_feature
    }

    SUPPORT_TICKETS {
        TEXT ticket_id PK
        TEXT account_id FK
        TIMESTAMP submitted_at
        TIMESTAMP closed_at
        NUMERIC resolution_time_hours
        TEXT priority
        INTEGER first_response_time_minutes
        INTEGER satisfaction_score
        BOOLEAN escalation_flag
    }


