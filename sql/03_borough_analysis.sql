-- NYC 311 Street Maintenance Operations Analysis
-- Borough-Level Analysis
--
-- Scope: NYC DOT street maintenance requests created in 2025.
-- Statuses reflect the October 21, 2026 extraction.
-- Closure time measures administrative closure, not physical repair.
-- UNSPECIFIED boroughs are retained for accurate totals.

-- Query 1: Request volume and closure status by borough
SELECT
    borough,
    COUNT(*) AS total_requests,
    ROUND(
        100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM street_requests),
        2
    ) AS share_of_all_requests_pct,
    SUM(is_closed) AS closed_requests,
    SUM(is_unresolved) AS unresolved_requests,
    ROUND(
        100.0 * SUM(is_closed) / COUNT(*),
        2
    ) AS closure_rate_pct,
    ROUND(
        100.0 * SUM(is_unresolved) / COUNT(*),
        2
    ) AS unresolved_rate_pct
FROM street_requests
GROUP BY borough
ORDER BY total_requests DESC;


-- Query 2: Average administrative closure time by borough
SELECT
    borough,
    COUNT(*) AS eligible_closed_requests,
    ROUND(AVG(closure_days), 2) AS avg_closure_days,
    ROUND(MAX(closure_days), 2) AS max_closure_days
FROM street_requests
WHERE has_valid_closure_time = 1
GROUP BY borough
ORDER BY avg_closure_days DESC;


-- Query 3: Median administrative closure time by borough
-- Window functions identify the middle observation(s) per borough.
WITH ranked_requests AS (
    SELECT
        borough,
        closure_days,
        ROW_NUMBER() OVER (
            PARTITION BY borough
            ORDER BY closure_days
        ) AS row_num,
        COUNT(*) OVER (
            PARTITION BY borough
        ) AS total_rows
    FROM street_requests
    WHERE has_valid_closure_time = 1
)
SELECT
    borough,
    ROUND(AVG(closure_days), 2) AS median_closure_days
FROM ranked_requests
WHERE row_num IN (
    CAST((total_rows + 1) / 2 AS INTEGER),
    CAST((total_rows + 2) / 2 AS INTEGER)
)
GROUP BY borough
ORDER BY median_closure_days DESC;


-- Query 4: Maintenance category mix by borough
SELECT
    borough,
    descriptor AS maintenance_category,
    COUNT(*) AS total_requests,
    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (PARTITION BY borough),
        2
    ) AS share_within_borough_pct
FROM street_requests
GROUP BY borough, descriptor
ORDER BY borough, total_requests DESC;


-- Query 5: Unresolved requests by borough and category
SELECT
    borough,
    descriptor AS maintenance_category,
    COUNT(*) AS unresolved_requests
FROM street_requests
WHERE is_unresolved = 1
GROUP BY borough, descriptor
ORDER BY unresolved_requests DESC;
