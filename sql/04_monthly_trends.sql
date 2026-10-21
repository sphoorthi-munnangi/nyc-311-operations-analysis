-- NYC 311 Street Maintenance Operations Analysis
-- Monthly Trends Analysis
--
-- Scope: NYC DOT street maintenance requests created in 2025.
-- Months represent request creation, not closure.
-- Statuses reflect the October 21, 2026 extraction snapshot.

-- Query 1: Monthly request volume and unresolved workload
SELECT
    created_month,
    COUNT(*) AS total_requests,
    SUM(is_closed) AS closed_requests,
    SUM(is_unresolved) AS unresolved_requests,
    ROUND(
        100.0 * SUM(is_unresolved) / COUNT(*),
        2
    ) AS unresolved_rate_pct
FROM street_requests
GROUP BY created_month
ORDER BY created_month;


-- Query 2: Monthly demand by maintenance category
SELECT
    created_month,
    descriptor AS maintenance_category,
    COUNT(*) AS total_requests
FROM street_requests
GROUP BY created_month, descriptor
ORDER BY created_month, total_requests DESC;


-- Query 3: Monthly median administrative closure time
-- Includes only requests with valid administrative closure times.
WITH ranked_requests AS (
    SELECT
        created_month,
        closure_days,
        ROW_NUMBER() OVER (
            PARTITION BY created_month
            ORDER BY closure_days
        ) AS row_num,
        COUNT(*) OVER (
            PARTITION BY created_month
        ) AS total_rows
    FROM street_requests
    WHERE has_valid_closure_time = 1
)
SELECT
    created_month,
    COUNT(*) AS median_observations,
    ROUND(AVG(closure_days), 2) AS median_closure_days
FROM ranked_requests
WHERE row_num IN (
    CAST((total_rows + 1) / 2 AS INTEGER),
    CAST((total_rows + 2) / 2 AS INTEGER)
)
GROUP BY created_month
ORDER BY created_month;


-- Query 4: Unresolved pothole requests by borough and creation month
-- Investigates the unresolved workload concentrated in Queens.
SELECT
    created_month,
    borough,
    COUNT(*) AS unresolved_pothole_requests
FROM street_requests
WHERE is_unresolved = 1
  AND descriptor = 'Pothole'
GROUP BY created_month, borough
ORDER BY created_month, unresolved_pothole_requests DESC;


-- Query 5: Monthly request volume by borough
SELECT
    created_month,
    borough,
    COUNT(*) AS total_requests
FROM street_requests
GROUP BY created_month, borough
ORDER BY created_month, total_requests DESC;
