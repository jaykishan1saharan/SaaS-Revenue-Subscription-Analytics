-- ============================================================
-- DAY 6: SUPPORT TICKET DEEP-DIVE ANALYSIS
-- Scope: Support ticket trends, escalation, satisfaction,
--        and resolution-time distribution.
-- Notes: Descriptive analysis only; no SLA target is assumed.
-- ============================================================

-- 1. Monthly ticket volume and escalation trend
SELECT
    strftime('%Y-%m', submitted_at) AS ticket_month,
    COUNT(*) AS total_tickets,
    SUM(
        CASE
            WHEN lower(CAST(escalation_flag AS TEXT)) IN ('true', '1')
            THEN 1 ELSE 0
        END
    ) AS escalated_tickets,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN lower(CAST(escalation_flag AS TEXT)) IN ('true', '1')
                THEN 1 ELSE 0
            END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS escalation_rate_pct
FROM support_tickets
GROUP BY strftime('%Y-%m', submitted_at)
ORDER BY ticket_month;


-- 2. Escalation rate by priority
SELECT
    priority,
    COUNT(*) AS total_tickets,
    SUM(
        CASE
            WHEN lower(CAST(escalation_flag AS TEXT)) IN ('true', '1')
            THEN 1 ELSE 0
        END
    ) AS escalated_tickets,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN lower(CAST(escalation_flag AS TEXT)) IN ('true', '1')
                THEN 1 ELSE 0
            END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS escalation_rate_pct
FROM support_tickets
GROUP BY priority
ORDER BY escalation_rate_pct DESC;


-- 3. Satisfaction by priority and escalation status
-- NULL satisfaction scores remain excluded from the average;
-- response coverage is shown separately.
SELECT
    priority,
    escalation_flag,
    COUNT(*) AS total_tickets,
    COUNT(satisfaction_score) AS satisfaction_responses,
    ROUND(AVG(satisfaction_score), 2) AS average_satisfaction_score,
    ROUND(
        100.0 * COUNT(satisfaction_score) / NULLIF(COUNT(*), 0),
        2
    ) AS satisfaction_response_rate_pct
FROM support_tickets
GROUP BY priority, escalation_flag
ORDER BY priority, escalation_flag;


-- 4. Resolution-time distribution
SELECT
    CASE
        WHEN resolution_time_hours <= 24 THEN '0-24 hours'
        WHEN resolution_time_hours <= 48 THEN '24-48 hours'
        ELSE 'Over 48 hours'
    END AS resolution_time_band,
    COUNT(*) AS total_tickets,
    ROUND(
        100.0 * COUNT(*) / (SELECT COUNT(*) FROM support_tickets),
        2
    ) AS ticket_share_pct
FROM support_tickets
GROUP BY resolution_time_band
ORDER BY
    CASE resolution_time_band
        WHEN '0-24 hours' THEN 1
        WHEN '24-48 hours' THEN 2
        ELSE 3
    END;
