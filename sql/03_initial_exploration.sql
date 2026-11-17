
-- Day 4: Support Tickets Initial SQL Exploration
-- Table prerequisite: support_tickets
-- Load data/interim/support_tickets_clean.csv into this table first.

-- 1. Total number of support tickets
SELECT COUNT(*) AS total_tickets
FROM support_tickets;

-- 2. Check unique ticket IDs
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT ticket_id) AS unique_ticket_ids
FROM support_tickets;

-- 3. Missing values by important field
SELECT
    SUM(CASE WHEN ticket_id IS NULL THEN 1 ELSE 0 END) AS missing_ticket_ids,
    SUM(CASE WHEN account_id IS NULL THEN 1 ELSE 0 END) AS missing_account_ids,
    SUM(CASE WHEN satisfaction_score IS NULL THEN 1 ELSE 0 END) AS missing_satisfaction_scores
FROM support_tickets;

-- 4. Tickets grouped by priority
SELECT
    priority,
    COUNT(*) AS ticket_count
FROM support_tickets
GROUP BY priority
ORDER BY ticket_count DESC;

-- 5. Average resolution time by priority
SELECT
    priority,
    COUNT(*) AS ticket_count,
    ROUND(AVG(resolution_time_hours), 2) AS avg_resolution_hours
FROM support_tickets
GROUP BY priority
ORDER BY avg_resolution_hours DESC;

-- 6. Average first response time by priority
SELECT
    priority,
    ROUND(AVG(first_response_time_minutes), 2) AS avg_first_response_minutes
FROM support_tickets
GROUP BY priority
ORDER BY avg_first_response_minutes DESC;

-- 7. Escalation distribution
SELECT
    escalation_flag,
    COUNT(*) AS ticket_count
FROM support_tickets
GROUP BY escalation_flag;

-- 8. Monthly ticket volume
SELECT
    strftime('%Y-%m', submitted_at) AS submission_month,
    COUNT(*) AS ticket_count
FROM support_tickets
GROUP BY submission_month
ORDER BY submission_month;

-- 9. Satisfaction score distribution
SELECT
    satisfaction_score,
    COUNT(*) AS response_count
FROM support_tickets
WHERE satisfaction_score IS NOT NULL
GROUP BY satisfaction_score
ORDER BY satisfaction_score;

-- 10. Account-wise ticket volume
SELECT
    account_id,
    COUNT(*) AS ticket_count
FROM support_tickets
GROUP BY account_id
ORDER BY ticket_count DESC
LIMIT 20;

-- 11. Check for invalid ticket durations
SELECT COUNT(*) AS invalid_duration_records
FROM support_tickets
WHERE resolution_time_hours < 0
   OR first_response_time_minutes < 0;

-- 12. Check for tickets closed before submission
SELECT COUNT(*) AS invalid_timestamp_records
FROM support_tickets
WHERE datetime(closed_at) < datetime(submitted_at);
