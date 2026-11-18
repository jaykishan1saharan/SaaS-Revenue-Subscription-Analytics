-- ============================================================
-- PROJECT: SaaS Revenue & Subscription Analytics
-- FILE: 02_load_validation.sql
-- OWNER: Jaykishan
-- PURPOSE: Validate loaded data and table relationships
-- Run AFTER importing all five cleaned CSV files.
-- ============================================================


-- 1. ROW COUNTS

SELECT 'accounts' AS table_name, COUNT(*) AS loaded_rows
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


-- 2. PRIMARY KEY DUPLICATE CHECKS
-- Each query should return zero rows.

SELECT account_id, COUNT(*)
FROM public.accounts
GROUP BY account_id
HAVING COUNT(*) > 1;

SELECT subscription_id, COUNT(*)
FROM public.subscriptions
GROUP BY subscription_id
HAVING COUNT(*) > 1;

SELECT churn_event_id, COUNT(*)
FROM public.churn_events
GROUP BY churn_event_id
HAVING COUNT(*) > 1;

SELECT usage_record_id, COUNT(*)
FROM public.feature_usage
GROUP BY usage_record_id
HAVING COUNT(*) > 1;

SELECT ticket_id, COUNT(*)
FROM public.support_tickets
GROUP BY ticket_id
HAVING COUNT(*) > 1;


-- 3. NULL CHECKS FOR REQUIRED IDENTIFIERS

SELECT
    COUNT(*) FILTER (WHERE account_id IS NULL) AS null_account_ids
FROM public.accounts;

SELECT
    COUNT(*) FILTER (WHERE subscription_id IS NULL) AS null_subscription_ids
FROM public.subscriptions;

SELECT
    COUNT(*) FILTER (WHERE churn_event_id IS NULL) AS null_churn_event_ids
FROM public.churn_events;

SELECT
    COUNT(*) FILTER (WHERE usage_record_id IS NULL) AS null_usage_record_ids,
    COUNT(*) FILTER (WHERE usage_id IS NULL) AS null_source_usage_ids
FROM public.feature_usage;

SELECT
    COUNT(*) FILTER (WHERE ticket_id IS NULL) AS null_ticket_ids
FROM public.support_tickets;


-- 4. FOREIGN KEY VALIDATION
-- Each orphan count should be zero.

SELECT COUNT(*) AS orphan_subscriptions
FROM public.subscriptions s
LEFT JOIN public.accounts a
    ON s.account_id = a.account_id
WHERE a.account_id IS NULL;

SELECT COUNT(*) AS orphan_churn_events
FROM public.churn_events c
LEFT JOIN public.accounts a
    ON c.account_id = a.account_id
WHERE a.account_id IS NULL;

SELECT COUNT(*) AS orphan_support_tickets
FROM public.support_tickets t
LEFT JOIN public.accounts a
    ON t.account_id = a.account_id
WHERE a.account_id IS NULL;

SELECT COUNT(*) AS orphan_feature_usage
FROM public.feature_usage f
LEFT JOIN public.subscriptions s
    ON f.subscription_id = s.subscription_id
WHERE s.subscription_id IS NULL;


-- 5. FEATURE USAGE SOURCE IDENTIFIER REVIEW
-- Repeated source IDs are expected to require investigation.
-- Do not delete these records automatically.

SELECT
    usage_id,
    COUNT(*) AS occurrences
FROM public.feature_usage
GROUP BY usage_id
HAVING COUNT(*) > 1
ORDER BY occurrences DESC, usage_id;


-- 6. MISSING VALUE REVIEW

SELECT
    COUNT(*) FILTER (WHERE end_date IS NULL) AS missing_end_dates,
    COUNT(*) AS total_subscriptions
FROM public.subscriptions;

SELECT
    COUNT(*) FILTER (WHERE feedback_text IS NULL) AS missing_feedback,
    COUNT(*) AS total_churn_events
FROM public.churn_events;

SELECT
    COUNT(*) FILTER (WHERE satisfaction_score IS NULL) AS missing_satisfaction,
    COUNT(*) AS total_support_tickets
FROM public.support_tickets;


-- 7. SUBSCRIPTION STATUS AND END DATE REVIEW

SELECT
    churn_flag,
    is_trial,
    COUNT(*) AS total_subscriptions,
    COUNT(*) FILTER (WHERE end_date IS NULL) AS missing_end_dates
FROM public.subscriptions
GROUP BY churn_flag, is_trial
ORDER BY churn_flag, is_trial;


-- 8. SUBSCRIPTION DATE CHRONOLOGY
-- Review any rows returned; do not automatically delete them.

SELECT
    subscription_id,
    start_date,
    end_date
FROM public.subscriptions
WHERE end_date IS NOT NULL
  AND end_date < start_date;


-- 9. SUPPORT TICKET DATE CHRONOLOGY

SELECT
    ticket_id,
    submitted_at,
    closed_at
FROM public.support_tickets
WHERE closed_at < submitted_at;


-- 10. CHURN EVENT DATE REVIEW

SELECT
    c.churn_event_id,
    c.account_id,
    c.churn_date,
    a.signup_date
FROM public.churn_events c
JOIN public.accounts a
    ON c.account_id = a.account_id
WHERE c.churn_date < a.signup_date;


-- 11. MRR AND ARR CONSISTENCY REVIEW
-- Diagnostic only. Billing rules must be confirmed first.

SELECT
    subscription_id,
    billing_frequency,
    mrr_amount,
    arr_amount,
    (mrr_amount * 12) AS annualized_mrr,
    (arr_amount - (mrr_amount * 12)) AS difference
FROM public.subscriptions
WHERE ABS(arr_amount - (mrr_amount * 12)) > 0.01
ORDER BY ABS(arr_amount - (mrr_amount * 12)) DESC;


-- 12. BASIC NUMERIC RANGE CHECKS

SELECT *
FROM public.accounts
WHERE seats <= 0;

SELECT *
FROM public.subscriptions
WHERE seats <= 0
   OR mrr_amount < 0
   OR arr_amount < 0;

SELECT *
FROM public.feature_usage
WHERE usage_count < 0
   OR usage_duration_secs < 0
   OR error_count < 0;

SELECT *
FROM public.support_tickets
WHERE resolution_time_hours < 0
   OR first_response_time_minutes < 0;


-- 13. RELATIONSHIP SUMMARY

SELECT
    (SELECT COUNT(*) FROM public.accounts) AS accounts,
    (SELECT COUNT(*) FROM public.subscriptions) AS subscriptions,
    (SELECT COUNT(*) FROM public.churn_events) AS churn_events,
    (SELECT COUNT(*) FROM public.feature_usage) AS feature_usage,
    (SELECT COUNT(*) FROM public.support_tickets) AS support_tickets;


-- ============================================================
-- END OF VALIDATION
-- ============================================================