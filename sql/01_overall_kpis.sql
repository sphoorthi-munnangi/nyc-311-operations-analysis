-- NYC 311 Street Maintenance Operations Analysis
-- Overall Business KPIs
--
-- Scope: NYC DOT street maintenance requests created in 2025.
-- Statuses reflect the October 21, 2026 data extraction.
-- Closure time measures administrative closure, not physical repair.

-- Query 1: Overall operational KPIs
SELECT
    COUNT(*) AS total_requests,
    SUM(is_closed) AS closed_requests,
    SUM(is_unresolved) AS unresolved_requests,
    ROUND(
        100.0 * SUM(is_closed) / COUNT(*),
        2
    ) AS closure_rate_pct,
    ROUND(
        100.0 * SUM(is_unresolved) / COUNT(*),
        2
    ) AS unresolved_rate_pct,
    SUM(has_valid_closure_time) AS valid_closure_records
FROM street_requests;


-- Query 2: Average administrative closure time
-- Excludes unresolved requests and invalid closure durations.
SELECT
    COUNT(*) AS eligible_requests,
    ROUND(AVG(closure_hours), 2) AS avg_closure_hours,
    ROUND(AVG(closure_days), 2) AS avg_closure_days,
    ROUND(MIN(closure_days), 2) AS min_closure_days,
    ROUND(MAX(closure_days), 2) AS max_closure_days
FROM street_requests
WHERE has_valid_closure_time = 1;


-- Query 3: Median administrative closure time
-- SQLite does not provide a built-in MEDIAN() aggregate.
-- ROW_NUMBER() and COUNT() identify the middle observation(s).
WITH ordered_closures AS (
    SELECT
        closure_days,
        ROW_NUMBER() OVER (
            ORDER BY closure_days
        ) AS row_num,
        COUNT(*) OVER () AS total_rows
    FROM street_requests
    WHERE has_valid_closure_time = 1
)
SELECT
    ROUND(AVG(closure_days), 2) AS median_closure_days
FROM ordered_closures
WHERE row_num IN (
    CAST((total_rows + 1) / 2 AS INTEGER),
    CAST((total_rows + 2) / 2 AS INTEGER)
);


-- Query 4: Data quality summary
SELECT
    data_quality_flag,
    COUNT(*) AS request_count
FROM street_requests
GROUP BY data_quality_flag
ORDER BY request_count DESC;
