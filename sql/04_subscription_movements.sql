-- ============================================================
-- PROJECT: SaaS Revenue & Subscription Analytics
-- FILE: 04_subscription_movements.sql
-- PURPOSE: Review account event sequences and conservative MRR matches
-- ============================================================

-- Proposed interpretation only:
--   * is_reactivation = TRUE is a reactivation-event record, not churn.
--   * A prior non-reactivation event is sequence evidence, not proof of
--     an actual account state transition.
--   * Same-account, same-date events have no documented tie-breaker.
--   * churn_events has no subscription_id. Exact account/date matches to
--     subscription end_date are candidates, not verified foreign-key links.
--   * Event MRR below is a departure candidate by churn_date month, not an
--     end-of-month MRR balance or a refund-adjusted revenue measure.


-- 1. Event sequence by account and date.
-- Same-day records are kept separate and marked ambiguous rather than
-- inventing an order from churn_event_id.

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
        ) AS previous_has_candidate_churn,
        LAG(has_reactivation) OVER (
            PARTITION BY account_id ORDER BY churn_date
        ) AS previous_has_reactivation,
        BOOL_OR(has_candidate_churn AND event_count = 1) OVER (
            PARTITION BY account_id
            ORDER BY churn_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prior_candidate_churn_exists
    FROM event_days
)
SELECT
    c.account_id,
    c.churn_date,
    c.churn_event_id,
    c.is_reactivation,
    d.event_count AS same_day_event_count,
    CASE
        WHEN d.event_count > 1
            THEN 'same_day_order_ambiguous'
        WHEN d.previous_event_count IS NULL AND c.is_reactivation
            THEN 'reactivation_without_prior_event'
        WHEN d.previous_event_count IS NULL
            THEN 'initial_candidate_churn'
        WHEN d.previous_event_count > 1
            THEN 'previous_same_day_order_ambiguous'
        WHEN c.is_reactivation AND d.previous_has_candidate_churn
            THEN 'reactivation_after_candidate_churn'
        WHEN c.is_reactivation
            THEN 'reactivation_after_reactivation'
        WHEN d.previous_has_reactivation
             AND COALESCE(d.prior_candidate_churn_exists, FALSE)
            THEN 'possible_repeated_churn_reactivation_cycle'
        WHEN d.previous_has_reactivation
            THEN 'candidate_churn_after_reactivation'
        ELSE 'repeated_candidate_churn_without_reactivation'
    END AS sequence_assessment
FROM public.churn_events c
JOIN sequenced_days d
    ON d.account_id = c.account_id
   AND d.churn_date = c.churn_date
ORDER BY c.account_id, c.churn_date, c.churn_event_id;


-- 2. Monthly event and sequence-evidence counts.

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
        ) AS previous_has_candidate_churn,
        LAG(has_reactivation) OVER (
            PARTITION BY account_id ORDER BY churn_date
        ) AS previous_has_reactivation,
        BOOL_OR(has_candidate_churn AND event_count = 1) OVER (
            PARTITION BY account_id
            ORDER BY churn_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prior_candidate_churn_exists
    FROM event_days
)
SELECT
    DATE_TRUNC('month', c.churn_date)::DATE AS event_month,
    COUNT(*) AS recorded_event_rows,
    COUNT(*) FILTER (WHERE NOT c.is_reactivation) AS candidate_churn_rows,
    COUNT(*) FILTER (WHERE c.is_reactivation) AS reactivation_rows,
    COUNT(*) FILTER (
        WHERE c.is_reactivation
          AND d.event_count = 1
          AND d.previous_event_count = 1
          AND d.previous_has_candidate_churn
    ) AS reactivation_rows_after_single_candidate_churn,
    COUNT(*) FILTER (
        WHERE NOT c.is_reactivation
          AND d.event_count = 1
          AND d.previous_event_count = 1
          AND d.previous_has_reactivation
          AND COALESCE(d.prior_candidate_churn_exists, FALSE)
    ) AS possible_repeated_cycle_churn_rows
FROM public.churn_events c
JOIN sequenced_days d
    ON d.account_id = c.account_id
   AND d.churn_date = c.churn_date
GROUP BY event_month
ORDER BY event_month;


-- 3. Exact account/end-date candidates for subscription MRR attribution.
-- Only a single event on the account/date and a single subscription whose
-- end_date equals churn_date are eligible. Other open-ended or later-ending
-- subscription rows block account-level churn MRR attribution; NULL end_date
-- is not asserted to mean active, but is sufficient reason not to claim that
-- the account has no remaining subscription population.

WITH event_day_counts AS (
    SELECT
        account_id,
        churn_date,
        COUNT(*) AS event_count
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
unique_candidates AS (
    SELECT
        c.churn_event_id,
        c.account_id,
        c.churn_date,
        m.candidate_subscription_id,
        m.candidate_departing_subscription_mrr
    FROM public.churn_events c
    JOIN event_day_counts d
        ON d.account_id = c.account_id
       AND d.churn_date = c.churn_date
    JOIN subscription_match_stats m
        ON m.churn_event_id = c.churn_event_id
    WHERE NOT c.is_reactivation
      AND d.event_count = 1
      AND m.exact_subscription_match_count = 1
),
other_open_subscription_rows AS (
    SELECT
        u.churn_event_id,
        COUNT(s.subscription_id) AS other_not_ended_row_count
    FROM unique_candidates u
    LEFT JOIN public.subscriptions s
        ON s.account_id = u.account_id
       AND s.subscription_id <> u.candidate_subscription_id
       AND s.start_date <= u.churn_date
       AND (s.end_date IS NULL OR s.end_date > u.churn_date)
    GROUP BY u.churn_event_id
)
SELECT
    c.churn_event_id,
    c.account_id,
    c.churn_date,
    DATE_TRUNC('month', c.churn_date)::DATE AS event_month,
    c.is_reactivation,
    CASE
        WHEN c.is_reactivation THEN 'reactivation_not_mapped'
        WHEN d.event_count > 1
            THEN 'ambiguous_multiple_events_same_account_date'
        WHEN COALESCE(m.exact_subscription_match_count, 0) = 0
            THEN 'no_exact_same_account_end_date_match'
        WHEN m.exact_subscription_match_count > 1
            THEN 'ambiguous_multiple_subscription_matches'
        ELSE 'unique_same_account_end_date_candidate'
    END AS mapping_status,
    CASE
        WHEN NOT c.is_reactivation
         AND d.event_count = 1
         AND m.exact_subscription_match_count = 1
            THEN m.candidate_subscription_id
    END AS candidate_subscription_id,
    CASE
        WHEN NOT c.is_reactivation
         AND d.event_count = 1
         AND m.exact_subscription_match_count = 1
            THEN m.candidate_departing_subscription_mrr
    END AS candidate_departing_subscription_mrr,
    o.other_not_ended_row_count
        AS other_subscription_rows_not_ended_by_event_date,
    CASE
        WHEN o.other_not_ended_row_count = 0
            THEN u.candidate_departing_subscription_mrr
    END AS candidate_account_churned_mrr
FROM public.churn_events c
JOIN event_day_counts d
    ON d.account_id = c.account_id
   AND d.churn_date = c.churn_date
LEFT JOIN subscription_match_stats m
    ON m.churn_event_id = c.churn_event_id
LEFT JOIN unique_candidates u
    ON u.churn_event_id = c.churn_event_id
LEFT JOIN other_open_subscription_rows o
    ON o.churn_event_id = c.churn_event_id
ORDER BY c.account_id, c.churn_date, c.churn_event_id;
