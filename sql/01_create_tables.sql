-- ============================================================
-- PROJECT: SaaS Revenue & Subscription Analytics
-- DATABASE: Supabase PostgreSQL
-- FILE: 01_create_tables.sql
-- OWNER: Jaykishan
-- PURPOSE: Create five project tables and their relationships
-- ============================================================

-- 1. ACCOUNTS
-- Parent table for subscriptions, churn events and support tickets.

CREATE TABLE IF NOT EXISTS public.accounts (
    account_id TEXT PRIMARY KEY,
    account_name TEXT NOT NULL,
    industry TEXT NOT NULL,
    country TEXT NOT NULL,
    signup_date DATE NOT NULL,
    referral_source TEXT NOT NULL,
    plan_tier TEXT NOT NULL,
    seats INTEGER NOT NULL,
    is_trial BOOLEAN NOT NULL,
    churn_flag BOOLEAN NOT NULL
);


-- 2. SUBSCRIPTIONS
-- Each subscription belongs to an account.

CREATE TABLE IF NOT EXISTS public.subscriptions (
    subscription_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    plan_tier TEXT NOT NULL,
    seats INTEGER NOT NULL,
    mrr_amount NUMERIC(14,2) NOT NULL,
    arr_amount NUMERIC(14,2) NOT NULL,
    is_trial BOOLEAN NOT NULL,
    upgrade_flag BOOLEAN NOT NULL,
    downgrade_flag BOOLEAN NOT NULL,
    churn_flag BOOLEAN NOT NULL,
    billing_frequency TEXT NOT NULL,
    auto_renew_flag BOOLEAN NOT NULL,

    CONSTRAINT fk_subscriptions_accounts
        FOREIGN KEY (account_id)
        REFERENCES public.accounts(account_id)
);


-- 3. CHURN EVENTS
-- Each churn event belongs to an account.

CREATE TABLE IF NOT EXISTS public.churn_events (
    churn_event_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    churn_date DATE NOT NULL,
    reason_code TEXT NOT NULL,
    refund_amount_usd NUMERIC(12,2) NOT NULL,
    preceding_upgrade_flag BOOLEAN NOT NULL,
    preceding_downgrade_flag BOOLEAN NOT NULL,
    is_reactivation BOOLEAN NOT NULL,
    feedback_text TEXT,

    CONSTRAINT fk_churn_events_accounts
        FOREIGN KEY (account_id)
        REFERENCES public.accounts(account_id)
);


-- 4. FEATURE USAGE
-- usage_id is retained as the source identifier.
-- It is NOT the primary key because Day 2 found repeated IDs.
-- usage_record_id provides a unique database-generated key.

CREATE TABLE IF NOT EXISTS public.feature_usage (
    usage_record_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usage_id TEXT NOT NULL,
    subscription_id TEXT NOT NULL,
    usage_date DATE NOT NULL,
    feature_name TEXT NOT NULL,
    usage_count INTEGER NOT NULL,
    usage_duration_secs INTEGER NOT NULL,
    error_count INTEGER NOT NULL,
    is_beta_feature BOOLEAN NOT NULL,

    CONSTRAINT fk_feature_usage_subscriptions
        FOREIGN KEY (subscription_id)
        REFERENCES public.subscriptions(subscription_id)
);


-- 5. SUPPORT TICKETS
-- Each support ticket belongs to an account.

CREATE TABLE IF NOT EXISTS public.support_tickets (
    ticket_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    submitted_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP NOT NULL,
    resolution_time_hours NUMERIC(10,2) NOT NULL,
    priority TEXT NOT NULL,
    first_response_time_minutes NUMERIC(10,2) NOT NULL,
    satisfaction_score INTEGER,
    escalation_flag BOOLEAN NOT NULL,

    CONSTRAINT fk_support_tickets_accounts
        FOREIGN KEY (account_id)
        REFERENCES public.accounts(account_id)
);


-- ============================================================
-- INDEXES
-- Improve common joins and date-based analysis.
-- Primary keys already have their own indexes.
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_subscriptions_account_id
    ON public.subscriptions(account_id);

CREATE INDEX IF NOT EXISTS idx_churn_events_account_id
    ON public.churn_events(account_id);

CREATE INDEX IF NOT EXISTS idx_feature_usage_subscription_id
    ON public.feature_usage(subscription_id);

CREATE INDEX IF NOT EXISTS idx_support_tickets_account_id
    ON public.support_tickets(account_id);

CREATE INDEX IF NOT EXISTS idx_subscriptions_start_date
    ON public.subscriptions(start_date);

CREATE INDEX IF NOT EXISTS idx_churn_events_churn_date
    ON public.churn_events(churn_date);

CREATE INDEX IF NOT EXISTS idx_feature_usage_usage_date
    ON public.feature_usage(usage_date);

CREATE INDEX IF NOT EXISTS idx_support_tickets_submitted_at
    ON public.support_tickets(submitted_at);


-- ============================================================
-- END OF TABLE CREATION
-- ============================================================