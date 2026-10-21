-- NYC 311 Street Maintenance Operations Analysis
-- Maintenance Category Analysis
--
-- Scope: NYC DOT requests created in 2025.
-- Statuses reflect the October 21, 2026 extraction.
-- Closure times represent administrative closure, not physical repair.

-- Query 1: Request volume, closure rate, and unresolved workload
SELECT
    descriptor AS maintenance_category,
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
GROUP BY descriptor
ORDER BY total_requests DESC;


-- Query 2: Average closure time by maintenance category
-- Only valid administratively closed requests are included.
SELECT
    descriptor AS maintenance_category,
    COUNT(*) AS eligible_closed_requests,
    ROUND(AVG(closure_hours), 2) AS avg_closure_hours,
    ROUND(AVG(closure_days), 2) AS avg_closure_days,
    ROUND(MAX(closure_days), 2) AS max_closure_days
FROM street_requests
WHERE has_valid_closure_time = 1
GROUP BY descriptor
ORDER BY avg_closure_days DESC;


-- Query 3: Median closure time by maintenance category
-- Window functions identify the middle observation(s) per category.
WITH ranked_requests AS (
    SELECT
        descriptor,
        closure_days,
        ROW_NUMBER() OVER (
            PARTITION BY descriptor
            ORDER BY closure_days
        ) AS row_num,
        COUNT(*) OVER (
            PARTITION BY descriptor
        ) AS total_rows
    FROM street_requests
    WHERE has_valid_closure_time = 1
)
SELECT
    descriptor AS maintenance_category,
    ROUND(AVG(closure_days), 2) AS median_closure_days
FROM ranked_requests
WHERE row_num IN (
    CAST((total_rows + 1) / 2 AS INTEGER),
    CAST((total_rows + 2) / 2 AS INTEGER)
)
GROUP BY descriptor
ORDER BY median_closure_days DESC;


-- Query 4: Requests taking more than seven days to close
-- Measures the long-running share among valid closed requests.
SELECT
    descriptor AS maintenance_category,
    COUNT(*) AS eligible_closed_requests,
    SUM(
        CASE WHEN closure_days > 7 THEN 1 ELSE 0 END
    ) AS requests_over_7_days,
    ROUND(
        100.0 * SUM(
            CASE WHEN closure_days > 7 THEN 1 ELSE 0 END
        ) / COUNT(*),
        2
    ) AS over_7_days_pct
FROM street_requests
WHERE has_valid_closure_time = 1
GROUP BY descriptor
ORDER BY over_7_days_pct DESC;
