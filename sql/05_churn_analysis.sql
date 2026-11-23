-- ============================================================
-- PROJECT: SaaS Revenue & Subscription Analytics
-- FILE: 05_churn_analysis.sql
-- PURPOSE: Conservative churn-event and churned-MRR analysis
-- ============================================================
-- Rules:
-- * is_reactivation = TRUE is reactivation evidence, not a churn event.
-- * Multiple events for one account/date remain ambiguous.
-- * Churned MRR is attributed only to an eligible, non-reactivation event
--   with one same-account/subscription end-date match and no other
--   not-ended subscription at the event date.
-- * Candidate MRR is not refund-adjusted or a month-end revenue balance.


-- 1. EVENT SECTION: distinguish recorded events from unique churned accounts
WITH event_rows AS (
    SELECT
        *,
        DATE_TRUNC('month', churn_date)::DATE AS churn_month
    FROM public.churn_events
),
event_summary AS (
    SELECT
        churn_month,
        COUNT(*) AS recorded_event_rows,
        COUNT(*) FILTER (WHERE NOT is_reactivation) AS candidate_churn_event_rows,
        COUNT(*) FILTER (WHERE is_reactivation) AS reactivation_event_rows,
        COUNT(DISTINCT account_id) FILTER (WHERE NOT is_reactivation)
            AS unique_accounts_with_churn_events,
        COUNT(DISTINCT account_id) FILTER (WHERE is_reactivation)
            AS unique_accounts_with_reactivation_events
    FROM event_rows
    GROUP BY churn_month
),
account_month AS (
    SELECT
        account_id,
        DATE_TRUNC('month', churn_date)::DATE AS churn_month,
        COUNT(*) AS churn_event_rows,
        COUNT(*) FILTER (WHERE NOT is_reactivation) AS candidate_churn_event_rows
    FROM public.churn_events
    WHERE NOT is_reactivation
    GROUP BY account_id, churn_month
)
SELECT
    e.churn_month,
    e.recorded_event_rows,
    e.candidate_churn_event_rows,
    e.reactivation_event_rows,
    e.unique_accounts_with_churn_events,
    e.unique_accounts_with_reactivation_events,
    COUNT(*) FILTER (WHERE a.candidate_churn_event_rows = 1)
        AS unique_candidate_churn_accounts,
    COUNT(*) FILTER (WHERE a.candidate_churn_event_rows > 1)
        AS ambiguous_repeat_churn_accounts
FROM event_summary e
LEFT JOIN account_month a ON a.churn_month = e.churn_month
GROUP BY
    e.churn_month,
    e.recorded_event_rows,
    e.candidate_churn_event_rows,
    e.reactivation_event_rows,
    e.unique_accounts_with_churn_events,
    e.unique_accounts_with_reactivation_events
ORDER BY e.churn_month;


-- 2. REACTIVATION SECTION: sequence evidence only
WITH event_days AS (
    SELECT
        account_id,
        churn_date,
        COUNT(*) AS event_count,
        BOOL_OR(NOT is_reactivation) AS has_candidate_churn,
        BOOL_OR(is_reactivation) AS has_reactivation
    FROM public.churn_events
    GROUP BY account_id, churn_date
),
sequenced_days AS (
    SELECT
        account_id,
        churn_date,
        event_count,
        has_candidate_churn,
        has_reactivation,
        LAG(event_count) OVER (
            PARTITION BY account_id ORDER BY churn_date
        ) AS previous_event_count,
        LAG(has_candidate_churn) OVER (
            PARTITION BY account_id ORDER BY churn_date
        ) AS previous_has_candidate_churn
    FROM event_days
)
SELECT
    c.churn_event_id,
    c.account_id,
    c.churn_date,
    c.is_reactivation,
    d.event_count AS same_day_event_count,
    CASE
        WHEN d.event_count > 1 THEN 'same_day_order_ambiguous'
        WHEN d.previous_event_count IS NULL AND c.is_reactivation
            THEN 'reactivation_without_prior_event'
        WHEN d.previous_event_count IS NULL THEN 'initial_candidate_churn'
        WHEN d.previous_event_count > 1
            THEN 'previous_same_day_order_ambiguous'
        WHEN c.is_reactivation AND d.previous_has_candidate_churn
            THEN 'reactivation_after_candidate_churn'
        ELSE 'sequence_not_supported'
    END AS reactivation_treatment
FROM public.churn_events c
JOIN sequenced_days d
    ON d.account_id = c.account_id
   AND d.churn_date = c.churn_date
ORDER BY c.account_id, c.churn_date, c.churn_event_id;


-- 3. REVENUE SECTION: eligible event-to-subscription matches
WITH event_day_counts AS (
    SELECT account_id, churn_date, COUNT(*) AS event_count
    FROM public.churn_events
    GROUP BY account_id, churn_date
),
subscription_match_stats AS (
    SELECT
        c.churn_event_id,
        COUNT(s.subscription_id) AS exact_subscription_match_count,
        MIN(s.subscription_id) AS candidate_subscription_id,
        SUM(s.mrr_amount) AS candidate_departing_subscription_mrr
    FROM public.churn_events c
    LEFT JOIN public.subscriptions s
        ON s.account_id = c.account_id
       AND s.end_date = c.churn_date
       AND s.start_date <= c.churn_date
    WHERE NOT c.is_reactivation
    GROUP BY c.churn_event_id
),
eligible_events AS (
    SELECT
        c.churn_event_id,
        c.account_id,
        c.churn_date,
        DATE_TRUNC('month', c.churn_date)::DATE AS churn_month,
        m.candidate_subscription_id,
        m.candidate_departing_subscription_mrr,
        COUNT(o.subscription_id) AS other_not_ended_subscription_count
    FROM public.churn_events c
    JOIN event_day_counts d
      ON d.account_id = c.account_id
     AND d.churn_date = c.churn_date
    JOIN subscription_match_stats m
      ON m.churn_event_id = c.churn_event_id
    LEFT JOIN public.subscriptions o
      ON o.account_id = c.account_id
     AND o.subscription_id <> m.candidate_subscription_id
     AND o.start_date <= c.churn_date
     AND (o.end_date IS NULL OR o.end_date > c.churn_date)
    WHERE NOT c.is_reactivation
      AND d.event_count = 1
      AND m.exact_subscription_match_count = 1
    GROUP BY
        c.churn_event_id,
        c.account_id,
        c.churn_date,
        m.candidate_subscription_id,
        m.candidate_departing_subscription_mrr
)
SELECT
    c.churn_event_id,
    c.account_id,
    c.churn_date,
    DATE_TRUNC('month', c.churn_date)::DATE AS churn_month,
    CASE
        WHEN c.is_reactivation THEN 'reactivation_not_mapped'
        WHEN d.event_count > 1 THEN 'ambiguous_multiple_events_same_account_date'
        WHEN COALESCE(m.exact_subscription_match_count, 0) = 0
            THEN 'no_exact_same_account_end_date_match'
        WHEN m.exact_subscription_match_count > 1
            THEN 'ambiguous_multiple_subscription_matches'
        WHEN e.candidate_subscription_id IS NULL
            THEN 'not_eligible'
        ELSE 'eligible_churn_event'
    END AS mapping_status,
    e.candidate_subscription_id,
    e.candidate_departing_subscription_mrr,
    e.other_not_ended_subscription_count,
    CASE
        WHEN e.other_not_ended_subscription_count = 0
            THEN e.candidate_departing_subscription_mrr
    END AS candidate_account_churned_mrr
FROM public.churn_events c
JOIN event_day_counts d
  ON d.account_id = c.account_id
 AND d.churn_date = c.churn_date
LEFT JOIN subscription_match_stats m
  ON m.churn_event_id = c.churn_event_id
LEFT JOIN eligible_events e
  ON e.churn_event_id = c.churn_event_id
ORDER BY c.account_id, c.churn_date, c.churn_event_id;


-- 4. REVENUE SECTION: monthly unique-account churned-MRR rollup
WITH event_day_counts AS (
    SELECT account_id, churn_date, COUNT(*) AS event_count
    FROM public.churn_events
    GROUP BY account_id, churn_date
),
event_matches AS (
    SELECT
        c.churn_event_id,
        c.account_id,
        c.churn_date,
        DATE_TRUNC('month', c.churn_date)::DATE AS churn_month,
        COUNT(s.subscription_id) AS exact_subscription_match_count,
        MIN(s.subscription_id) AS candidate_subscription_id,
        SUM(s.mrr_amount) AS candidate_departing_subscription_mrr
    FROM public.churn_events c
    LEFT JOIN public.subscriptions s
      ON s.account_id = c.account_id
     AND s.end_date = c.churn_date
     AND s.start_date <= c.churn_date
    WHERE NOT c.is_reactivation
    GROUP BY c.churn_event_id, c.account_id, c.churn_date
),
eligible_events AS (
    SELECT m.*
    FROM event_matches m
    JOIN event_day_counts d
      ON d.account_id = m.account_id
     AND d.churn_date = m.churn_date
    WHERE d.event_count = 1
      AND m.exact_subscription_match_count = 1
      AND NOT EXISTS (
          SELECT 1
          FROM public.subscriptions s
          WHERE s.account_id = m.account_id
            AND s.subscription_id <> m.candidate_subscription_id
            AND s.start_date <= m.churn_date
            AND (s.end_date IS NULL OR s.end_date > m.churn_date)
      )
),
deduplicated_account_month AS (
    SELECT
        churn_month,
        account_id,
        COUNT(*) AS eligible_event_count,
        SUM(candidate_departing_subscription_mrr)
            AS account_churned_mrr
    FROM eligible_events
    GROUP BY churn_month, account_id
)
SELECT
    churn_month,
    COUNT(*) FILTER (WHERE eligible_event_count = 1)
        AS unique_churned_accounts,
    COUNT(*) FILTER (WHERE eligible_event_count > 1)
        AS repeat_event_accounts_excluded_from_mrr,
    SUM(account_churned_mrr)
        FILTER (WHERE eligible_event_count = 1) AS churned_mrr
FROM deduplicated_account_month
GROUP BY churn_month
ORDER BY churn_month;
