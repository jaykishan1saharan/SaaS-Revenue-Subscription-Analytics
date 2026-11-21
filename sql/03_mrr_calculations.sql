
-- ============================================================
-- PROJECT: SaaS Revenue & Subscription Analytics
-- WEEK 2 DAY 7: MONTHLY RECURRING REVENUE (MRR)
-- FILE: 03_mrr_calculations.sql
-- PURPOSE: Build monthly subscription-level MRR snapshots
-- RULE STATUS: PROVISIONAL - END-DATE INCLUSIVITY PENDING
-- ============================================================

-- IMPORTANT BUSINESS RULES:
-- 1. mrr_amount is already monthly recurring revenue.
-- 2. Do NOT divide annual billing MRR by 12 again.
-- 3. Do NOT multiply MRR by seats.
-- 4. Include eligible zero-MRR trial subscriptions.
-- 5. Exclude refunds from MRR.
-- 6. Currency is unknown; do not add currency symbols.
-- 7. Inclusive end-date logic is PROVISIONAL pending approval.

-- ============================================================
-- 1. GENERATE MONTH-END REPORTING PERIODS
-- ============================================================

DROP TABLE IF EXISTS public.monthly_subscription_mrr;

CREATE TABLE public.monthly_subscription_mrr AS

WITH reporting_months AS (

    SELECT
        month_start::DATE AS period_start,

        (
            month_start
            + INTERVAL '1 month'
            - INTERVAL '1 day'
        )::DATE AS snapshot_date

    FROM generate_series(

        (
            SELECT DATE_TRUNC('month', MIN(start_date))::DATE
            FROM public.subscriptions
        ),

        (
            SELECT DATE_TRUNC('month', MAX(start_date))::DATE
            FROM public.subscriptions
        ),

        INTERVAL '1 month'

    ) AS months(month_start)
),

-- ============================================================
-- 2. SELECT PROVISIONALLY ACTIVE SUBSCRIPTIONS
-- ============================================================

eligible_subscriptions AS (

    SELECT
        rm.period_start,
        rm.snapshot_date,
        s.subscription_id,
        s.account_id,
        s.plan_tier,
        s.billing_frequency,
        s.is_trial,

        s.mrr_amount AS mrr_source_amount,
        s.arr_amount AS arr_source_amount

    FROM reporting_months rm

    INNER JOIN public.subscriptions s

        ON s.start_date <= rm.snapshot_date

       AND (
            s.end_date IS NULL
            OR s.end_date >= rm.snapshot_date
       )
)

-- ============================================================
-- 3. MONTHLY MRR AGGREGATION
-- ============================================================

SELECT

    period_start AS report_month,

    snapshot_date,

    COUNT(DISTINCT subscription_id)
        AS active_subscriptions,

    COUNT(DISTINCT account_id)
        AS active_accounts_all,

    COUNT(DISTINCT account_id) FILTER (
        WHERE mrr_source_amount > 0
    ) AS active_paid_accounts,

    SUM(mrr_source_amount)
        AS mrr_source_amount,

    SUM(arr_source_amount)
        AS arr_source_amount,

    SUM(mrr_source_amount) FILTER (
        WHERE LOWER(plan_tier) = 'basic'
    ) AS basic_mrr_source_amount,

    SUM(mrr_source_amount) FILTER (
        WHERE LOWER(plan_tier) = 'pro'
    ) AS pro_mrr_source_amount,

    SUM(mrr_source_amount) FILTER (
        WHERE LOWER(plan_tier) = 'enterprise'
    ) AS enterprise_mrr_source_amount,

    NULL::TEXT AS source_currency,

    'mrr_v1_provisional_inclusive_end_date'
        AS definition_version

FROM eligible_subscriptions

GROUP BY
    period_start,
    snapshot_date

ORDER BY
    snapshot_date;


-- ============================================================
-- 4. ADD PRIMARY KEY
-- ============================================================

ALTER TABLE public.monthly_subscription_mrr
ADD PRIMARY KEY (report_month);


-- ============================================================
-- 5. DISPLAY MONTHLY MRR RESULTS
-- ============================================================

SELECT
    report_month,
    snapshot_date,
    active_subscriptions,
    active_accounts_all,
    active_paid_accounts,
    mrr_source_amount,
    arr_source_amount,
    basic_mrr_source_amount,
    pro_mrr_source_amount,
    enterprise_mrr_source_amount,
    source_currency,
    definition_version

FROM public.monthly_subscription_mrr

ORDER BY report_month;


-- ============================================================
-- 6. VALIDATE PLAN-LEVEL MRR RECONCILIATION
-- ============================================================

SELECT

    report_month,

    mrr_source_amount,

    COALESCE(basic_mrr_source_amount, 0)
        + COALESCE(pro_mrr_source_amount, 0)
        + COALESCE(enterprise_mrr_source_amount, 0)
        AS plan_mrr_total,

    mrr_source_amount - (
        COALESCE(basic_mrr_source_amount, 0)
        + COALESCE(pro_mrr_source_amount, 0)
        + COALESCE(enterprise_mrr_source_amount, 0)
    ) AS reconciliation_difference

FROM public.monthly_subscription_mrr

ORDER BY report_month;


-- ============================================================
-- 7. VALIDATE BILLING FREQUENCY
-- ============================================================

SELECT

    billing_frequency,

    COUNT(*) AS subscription_count,

    SUM(mrr_amount) AS mrr_source_amount

FROM public.subscriptions

GROUP BY billing_frequency

ORDER BY billing_frequency;


-- ============================================================
-- 8. VALIDATE TRIAL REVENUE
-- ============================================================

SELECT

    COUNT(*) AS trial_subscription_count,

    COUNT(*) FILTER (
        WHERE mrr_amount <> 0
           OR arr_amount <> 0
    ) AS trials_with_nonzero_revenue

FROM public.subscriptions

WHERE is_trial = TRUE;


-- ============================================================
-- 9. VERIFY MONTHLY SNAPSHOT GRAIN
-- ============================================================

SELECT

    COUNT(*) AS monthly_rows,

    COUNT(DISTINCT report_month)
        AS unique_reporting_months,

    COUNT(*) FILTER (
        WHERE report_month <> DATE_TRUNC(
            'month', report_month
        )::DATE
    ) AS invalid_month_start_values,

    COUNT(*) FILTER (
        WHERE snapshot_date <> (
            report_month
            + INTERVAL '1 month'
            - INTERVAL '1 day'
        )::DATE
    ) AS invalid_snapshot_dates

FROM public.monthly_subscription_mrr;


-- ============================================================
-- END OF WEEK 2 DAY 7 MRR SQL
-- ============================================================
