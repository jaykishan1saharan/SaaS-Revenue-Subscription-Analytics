-- ============================================================
-- SaaS REVENUE & SUBSCRIPTION ANALYTICS
-- File: 03_initial_exploration.sql
-- Database: Supabase PostgreSQL
-- Purpose: Initial SQL-based exploratory data analysis
-- ============================================================


-- ============================================================
-- SECTION 1: OVERALL DATABASE OVERVIEW
-- ============================================================

-- 1.1 Total records in all five tables

SELECT 'accounts' AS table_name, COUNT(*) AS total_records
FROM public.accounts

UNION ALL

SELECT 'subscriptions', COUNT(*)
FROM public.subscriptions

UNION ALL

SELECT 'churn_events', COUNT(*)
FROM public.churn_events

UNION ALL

SELECT 'feature_usage', COUNT(*)
FROM public.feature_usage

UNION ALL

SELECT 'support_tickets', COUNT(*)
FROM public.support_tickets;


-- ============================================================
-- SECTION 2: ACCOUNTS EXPLORATION
-- ============================================================

-- 2.1 Accounts by industry

SELECT
    industry,
    COUNT(*) AS total_accounts
FROM public.accounts
GROUP BY industry
ORDER BY total_accounts DESC;


-- 2.2 Accounts by country

SELECT
    country,
    COUNT(*) AS total_accounts
FROM public.accounts
GROUP BY country
ORDER BY total_accounts DESC;


-- 2.3 Accounts by plan tier

SELECT
    plan_tier,
    COUNT(*) AS total_accounts
FROM public.accounts
GROUP BY plan_tier
ORDER BY total_accounts DESC;


-- 2.4 Accounts by referral source

SELECT
    referral_source,
    COUNT(*) AS total_accounts
FROM public.accounts
GROUP BY referral_source
ORDER BY total_accounts DESC;


-- 2.5 Trial vs non-trial accounts

SELECT
    is_trial,
    COUNT(*) AS total_accounts
FROM public.accounts
GROUP BY is_trial
ORDER BY is_trial;


-- 2.6 Account churn flag distribution

SELECT
    churn_flag,
    COUNT(*) AS total_accounts
FROM public.accounts
GROUP BY churn_flag;


-- 2.7 Account signup trend by month

SELECT
    DATE_TRUNC('month', signup_date)::DATE AS signup_month,
    COUNT(*) AS new_accounts
FROM public.accounts
GROUP BY signup_month
ORDER BY signup_month;


-- 2.8 Average seats by plan tier

SELECT
    plan_tier,
    COUNT(*) AS total_accounts,
    ROUND(AVG(seats::NUMERIC), 2) AS average_seats
FROM public.accounts
GROUP BY plan_tier
ORDER BY average_seats DESC;


-- ============================================================
-- SECTION 3: SUBSCRIPTIONS EXPLORATION
-- ============================================================

-- 3.1 Subscriptions by plan tier

SELECT
    plan_tier,
    COUNT(*) AS total_subscriptions
FROM public.subscriptions
GROUP BY plan_tier
ORDER BY total_subscriptions DESC;


-- 3.2 Subscriptions by billing frequency

SELECT
    billing_frequency,
    COUNT(*) AS total_subscriptions
FROM public.subscriptions
GROUP BY billing_frequency
ORDER BY total_subscriptions DESC;


-- 3.3 Trial vs non-trial subscriptions

SELECT
    is_trial,
    COUNT(*) AS total_subscriptions
FROM public.subscriptions
GROUP BY is_trial;


-- 3.4 Subscription churn distribution

SELECT
    churn_flag,
    COUNT(*) AS total_subscriptions
FROM public.subscriptions
GROUP BY churn_flag;


-- 3.5 Upgrade and downgrade distribution

SELECT
    upgrade_flag,
    downgrade_flag,
    COUNT(*) AS total_subscriptions
FROM public.subscriptions
GROUP BY upgrade_flag, downgrade_flag
ORDER BY total_subscriptions DESC;


-- 3.6 Auto-renew distribution

SELECT
    auto_renew_flag,
    COUNT(*) AS total_subscriptions
FROM public.subscriptions
GROUP BY auto_renew_flag;


-- 3.7 Revenue summary

SELECT
    COUNT(*) AS total_subscriptions,
    ROUND(SUM(mrr_amount), 2) AS total_mrr,
    ROUND(SUM(arr_amount), 2) AS total_arr,
    ROUND(AVG(mrr_amount), 2) AS average_mrr,
    ROUND(AVG(arr_amount), 2) AS average_arr
FROM public.subscriptions;


-- 3.8 Revenue by plan tier

SELECT
    plan_tier,
    COUNT(*) AS total_subscriptions,
    ROUND(SUM(mrr_amount), 2) AS total_mrr,
    ROUND(SUM(arr_amount), 2) AS total_arr,
    ROUND(AVG(mrr_amount), 2) AS average_mrr
FROM public.subscriptions
GROUP BY plan_tier
ORDER BY total_mrr DESC;


-- 3.9 Revenue by billing frequency

SELECT
    billing_frequency,
    COUNT(*) AS total_subscriptions,
    ROUND(SUM(mrr_amount), 2) AS total_mrr,
    ROUND(SUM(arr_amount), 2) AS total_arr
FROM public.subscriptions
GROUP BY billing_frequency
ORDER BY total_mrr DESC;


-- 3.10 Subscription starts by month

SELECT
    DATE_TRUNC('month', start_date)::DATE AS subscription_month,
    COUNT(*) AS new_subscriptions
FROM public.subscriptions
GROUP BY subscription_month
ORDER BY subscription_month;


-- 3.11 Missing subscription end dates by churn status

SELECT
    churn_flag,
    is_trial,
    COUNT(*) AS total_records,
    COUNT(*) FILTER (
        WHERE end_date IS NULL
    ) AS missing_end_dates
FROM public.subscriptions
GROUP BY churn_flag, is_trial
ORDER BY churn_flag, is_trial;


-- ============================================================
-- SECTION 4: CHURN EVENTS EXPLORATION
-- ============================================================

-- 4.1 Churn events by reason code

SELECT
    reason_code,
    COUNT(*) AS total_churn_events
FROM public.churn_events
GROUP BY reason_code
ORDER BY total_churn_events DESC;


-- 4.2 Refund summary

SELECT
    COUNT(*) AS total_churn_events,
    ROUND(SUM(refund_amount_usd), 2) AS total_refunds,
    ROUND(AVG(refund_amount_usd), 2) AS average_refund,
    MAX(refund_amount_usd) AS maximum_refund
FROM public.churn_events;


-- 4.3 Churn events by month

SELECT
    DATE_TRUNC('month', churn_date)::DATE AS churn_month,
    COUNT(*) AS total_churn_events
FROM public.churn_events
GROUP BY churn_month
ORDER BY churn_month;


-- 4.4 Preceding upgrade and downgrade flags

SELECT
    preceding_upgrade_flag,
    preceding_downgrade_flag,
    COUNT(*) AS total_events
FROM public.churn_events
GROUP BY preceding_upgrade_flag, preceding_downgrade_flag
ORDER BY total_events DESC;


-- 4.5 Reactivation distribution

SELECT
    is_reactivation,
    COUNT(*) AS total_events
FROM public.churn_events
GROUP BY is_reactivation;


-- 4.6 Churn events by account plan tier

SELECT
    a.plan_tier,
    COUNT(*) AS total_churn_events
FROM public.churn_events c
JOIN public.accounts a
    ON c.account_id = a.account_id
GROUP BY a.plan_tier
ORDER BY total_churn_events DESC;


-- ============================================================
-- SECTION 5: FEATURE USAGE EXPLORATION
-- ============================================================

-- 5.1 Usage by feature

SELECT
    feature_name,
    COUNT(*) AS usage_records,
    SUM(usage_count) AS total_usage_count,
    SUM(error_count) AS total_errors,
    ROUND(AVG(usage_duration_secs::NUMERIC), 2)
        AS average_duration_seconds
FROM public.feature_usage
GROUP BY feature_name
ORDER BY total_usage_count DESC;


-- 5.2 Most frequently used features

SELECT
    feature_name,
    SUM(usage_count) AS total_usage_count
FROM public.feature_usage
GROUP BY feature_name
ORDER BY total_usage_count DESC
LIMIT 10;


-- 5.3 Feature usage by month

SELECT
    DATE_TRUNC('month', usage_date)::DATE AS usage_month,
    feature_name,
    SUM(usage_count) AS total_usage_count
FROM public.feature_usage
GROUP BY usage_month, feature_name
ORDER BY usage_month, total_usage_count DESC;


-- 5.4 Beta vs non-beta feature usage

SELECT
    is_beta_feature,
    COUNT(*) AS usage_records,
    SUM(usage_count) AS total_usage_count,
    SUM(error_count) AS total_errors
FROM public.feature_usage
GROUP BY is_beta_feature;


-- 5.5 Feature usage error summary

SELECT
    feature_name,
    SUM(error_count) AS total_errors,
    SUM(usage_count) AS total_usage_count
FROM public.feature_usage
GROUP BY feature_name
ORDER BY total_errors DESC;


-- 5.6 Usage by subscription plan

SELECT
    s.plan_tier,
    COUNT(*) AS usage_records,
    SUM(f.usage_count) AS total_usage_count,
    SUM(f.error_count) AS total_errors
FROM public.feature_usage f
JOIN public.subscriptions s
    ON f.subscription_id = s.subscription_id
GROUP BY s.plan_tier
ORDER BY total_usage_count DESC;


-- ============================================================
-- SECTION 6: SUPPORT TICKETS EXPLORATION
-- ============================================================

-- 6.1 Tickets by priority

SELECT
    priority,
    COUNT(*) AS total_tickets
FROM public.support_tickets
GROUP BY priority
ORDER BY total_tickets DESC;


-- 6.2 Support ticket resolution summary

SELECT
    COUNT(*) AS total_tickets,
    ROUND(AVG(resolution_time_hours), 2)
        AS average_resolution_hours,
    MAX(resolution_time_hours) AS maximum_resolution_hours,
    ROUND(AVG(first_response_time_minutes), 2)
        AS average_first_response_minutes
FROM public.support_tickets;


-- 6.3 Tickets by escalation status

SELECT
    escalation_flag,
    COUNT(*) AS total_tickets
FROM public.support_tickets
GROUP BY escalation_flag;


-- 6.4 Satisfaction score distribution

SELECT
    satisfaction_score,
    COUNT(*) AS total_responses
FROM public.support_tickets
GROUP BY satisfaction_score
ORDER BY satisfaction_score;


-- 6.5 Missing satisfaction scores

SELECT
    COUNT(*) AS total_tickets,
    COUNT(*) FILTER (
        WHERE satisfaction_score IS NULL
    ) AS missing_satisfaction_scores
FROM public.support_tickets;


-- 6.6 Average resolution time by priority

SELECT
    priority,
    COUNT(*) AS total_tickets,
    ROUND(AVG(resolution_time_hours), 2)
        AS average_resolution_hours
FROM public.support_tickets
GROUP BY priority
ORDER BY average_resolution_hours DESC;


-- 6.7 Average first response time by priority

SELECT
    priority,
    ROUND(AVG(first_response_time_minutes), 2)
        AS average_first_response_minutes
FROM public.support_tickets
GROUP BY priority
ORDER BY average_first_response_minutes DESC;


-- ============================================================
-- SECTION 7: CROSS-TABLE EXPLORATION
-- ============================================================

-- 7.1 Accounts and subscription overview

SELECT
    a.account_id,
    a.account_name,
    a.plan_tier AS account_plan,
    COUNT(s.subscription_id) AS total_subscriptions,
    ROUND(COALESCE(SUM(s.mrr_amount), 0), 2) AS total_mrr
FROM public.accounts a
LEFT JOIN public.subscriptions s
    ON a.account_id = s.account_id
GROUP BY
    a.account_id,
    a.account_name,
    a.plan_tier
ORDER BY total_mrr DESC
LIMIT 20;


-- 7.2 Churn events and account industry

SELECT
    a.industry,
    COUNT(c.churn_event_id) AS total_churn_events,
    ROUND(SUM(c.refund_amount_usd), 2) AS total_refunds
FROM public.accounts a
JOIN public.churn_events c
    ON a.account_id = c.account_id
GROUP BY a.industry
ORDER BY total_churn_events DESC;


-- 7.3 Support ticket volume by account plan

SELECT
    a.plan_tier,
    COUNT(t.ticket_id) AS total_tickets,
    ROUND(AVG(t.resolution_time_hours), 2)
        AS average_resolution_hours
FROM public.accounts a
JOIN public.support_tickets t
    ON a.account_id = t.account_id
GROUP BY a.plan_tier
ORDER BY total_tickets DESC;


-- 7.4 Feature usage and support tickets by account

SELECT
    a.account_id,
    a.account_name,
    COUNT(DISTINCT s.subscription_id) AS total_subscriptions,
    COUNT(DISTINCT f.usage_record_id) AS usage_records,
    COUNT(DISTINCT t.ticket_id) AS support_tickets
FROM public.accounts a
LEFT JOIN public.subscriptions s
    ON a.account_id = s.account_id
LEFT JOIN public.feature_usage f
    ON s.subscription_id = f.subscription_id
LEFT JOIN public.support_tickets t
    ON a.account_id = t.account_id
GROUP BY a.account_id, a.account_name
ORDER BY usage_records DESC
LIMIT 20;


-- ============================================================
-- END OF INITIAL EXPLORATION
-- ============================================================
