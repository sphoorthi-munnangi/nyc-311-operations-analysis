# NYC 311 Street Maintenance — KPI Definitions

## 1. Analysis Scope

- **Source:** NYC Open Data, 311 Service Requests (2020–Present)
- **Agency:** Department of Transportation (DOT)
- **Complaint type:** Street Condition
- **Descriptors:** Pothole, Cave-in, Failed Street Repair
- **Request creation period:** January 1–December 31, 2025
- **Data extraction:** October 21, 2026 (UTC)
- **Unit of analysis:** One unique 311 service request
- **Total requests:** 51,572

The dataset is a snapshot of requests created during 2025, with
statuses and closure dates available at extraction time.

## 2. Core KPIs

### KPI 1: Total Request Volume

**Definition:** Number of unique 311 requests in the analysis scope.

**Calculation:** COUNT(DISTINCT unique_key)

**Denominator:** Not applicable.

**Include:** All 51,572 requests, including unresolved requests and
records flagged for date inconsistencies.

**Business purpose:** Measure reported street maintenance demand.

### KPI 2: Administrative Closure Rate

**Definition:** Percentage of requests currently marked Closed.

**Calculation:**

    Closed requests / Total requests * 100

**Numerator:** Requests with is_closed = 1.

**Denominator:** All requests in scope.

**Baseline:** 48,430 / 51,572 = approximately 93.9%.

**Important:** Closure status reflects administrative processing,
not necessarily physical completion of a street repair.

### KPI 3: Median Administrative Closure Time

**Definition:** Median elapsed time between request creation and
administrative closure, expressed in days.

**Calculation:** MEDIAN(closure_days)

**Include only:** has_valid_closure_time = 1.

**Exclude from this calculation:**
- Requests not marked Closed.
- Missing or invalid closure timestamps.
- Negative closure durations.

**Baseline eligible records:** 48,424.

**Business purpose:** Evaluate typical administrative processing speed
without allowing unusually long cases to dominate the metric.

### KPI 4: Average Administrative Closure Time

**Definition:** Arithmetic mean of valid closure durations in days.

**Calculation:** AVG(closure_days)

**Include only:** has_valid_closure_time = 1.

**Business purpose:** Compare with the median to identify the
influence of long-running requests.

### KPI 5: Unresolved Request Count

**Definition:** Number of requests not marked Closed at extraction.

**Calculation:** SUM(is_unresolved)

**Baseline:** 3,142.

**Business purpose:** Quantify unresolved workload for the
2025-created request cohort.

**Important:** This is not the historical backlog as of
December 31, 2025.

### KPI 6: Unresolved Request Rate

**Definition:** Percentage of requests not marked Closed.

**Calculation:**

    Unresolved requests / Total requests * 100

**Baseline:** 3,142 / 51,572 = approximately 6.1%.

### KPI 7: Request Volume by Category

**Definition:** Count of requests grouped by descriptor.

**Calculation:** COUNT(*) GROUP BY descriptor

**Validated baseline:**
- Pothole: 38,438
- Cave-in: 9,647
- Failed Street Repair: 3,487

**Business purpose:** Identify the types of reported maintenance
issues generating the greatest request volume.

### KPI 8: Request Volume by Borough

**Definition:** Count of requests grouped by standardized borough.

**Calculation:** COUNT(*) GROUP BY borough

**Handling:** Keep UNSPECIFIED as a separate category for
reconciliation. Exclude it only when explicitly comparing the five
named boroughs.

### KPI 9: Monthly Request Volume

**Definition:** Count of requests grouped by creation month.

**Calculation:** COUNT(*) GROUP BY created_month

**Business purpose:** Identify seasonality and demand peaks.

**Important:** Month refers to request creation, not closure.

## 3. Data Quality Rules

- Preserve all 51,572 unique requests.
- Exclude six negative-duration records from closure-time KPIs,
  but retain them in request-volume calculations.
- Preserve six non-Closed requests that contain closure dates;
  do not count them as administratively Closed.
- Preserve missing ZIP codes and unspecified boroughs.
- Treat UNKNOWN reporting channels as unknown, not as digital
  or telephone submissions.
- Use has_valid_closure_time = 1 for closure-duration metrics.
- Use is_closed and is_unresolved for status-based metrics.

## 4. Interpretation and Limitations

1. A 311 request represents reported demand, not necessarily a
   unique physical street defect.
2. Administrative closure does not prove that physical repair
   was completed.
3. Request statuses reflect the extraction snapshot, not
   necessarily their status at the end of 2025.
4. Closure-time comparisons may be affected by request
   complexity, routing practices, and unresolved cases.
5. Geographic comparisons reflect reported requests and are
   not normalized by population, road mileage, or traffic.
6. Median and average closure times describe requests with
   valid completed administrative closures, not all requests.

## 5. Planned Analysis Dimensions

We will compare these KPIs by:

- Maintenance category
- Borough
- Creation month
- Reporting channel, where meaningful

SQL, Python, and Tableau calculations should follow these
definitions consistently.
