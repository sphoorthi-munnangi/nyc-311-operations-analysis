# NYC 311 Street Maintenance Operations Analysis
## Business Insights & Recommendations

### 1. Executive Summary

This project analyzes 51,572 New York City 311 street maintenance service requests created between January 1 and December 31, 2025. The analysis focuses on three complaint categories: Pothole, Cave-in, and Failed Street Repair.

The objective is to evaluate administrative closure performance, identify geographic differences in unresolved requests, examine processing times, and highlight opportunities for operational improvement.

Using Python, SQL, and Tableau, the analysis identified several important findings:

- **93.91% administrative closure rate:** Of the 51,572 requests, 48,430 were classified as closed as of the October 21, 2026 data extraction.
- **3,142 unresolved requests:** These requests remained unresolved at the extraction snapshot.
- **Queens accounted for approximately 84.3% of unresolved requests:** Queens had 2,649 unresolved requests, indicating a potential area for further investigation.
- **0.99-day median administrative closure time:** Most requests with valid closure durations were processed relatively quickly, although performance varied by request category and borough.
- **May recorded the highest request volume:** The dataset contained 5,558 requests created during May 2025.

### Business Significance

The findings suggest opportunities to strengthen operational monitoring, investigate geographic differences in unresolved workloads, and identify request categories associated with longer administrative closure times.

In particular, the concentration of unresolved requests in Queens warrants further investigation to determine whether differences in workflows, reporting practices, request complexity, or other operational factors contribute to the observed pattern.

These findings can support more targeted performance reviews and data-informed operational decisions.

**Important limitation:** Request statuses reflect the October 21, 2026 extraction snapshot, not necessarily the status at the end of 2025. Administrative closure measures the recorded completion of a service request in the 311 system; it does not independently confirm that physical street repairs were completed.

## 2. Detailed Operational Findings

### 2.1 Geographic Concentration of Unresolved Requests

Unresolved street maintenance requests were not evenly distributed across New York City's boroughs.

As of the October 21, 2026 extraction snapshot, Queens accounted for 2,649 of the 3,142 unresolved requests, representing approximately 84.3% of the citywide unresolved total.

| Borough | Total Requests | Unresolved Requests | Unresolved Rate |
|---|---:|---:|---:|
| Queens | 21,079 | 2,649 | 12.57% |
| Brooklyn | 12,929 | 22 | 0.17% |
| Manhattan | 7,201 | 208 | 2.89% |
| Bronx | 5,478 | 117 | 2.14% |
| Staten Island | 4,757 | 144 | 3.03% |

An additional 128 records did not have a specified borough, including two unresolved requests.

**Business implication:** Queens represents a priority for investigating unresolved workloads. However, the concentration alone does not establish whether the underlying cause is operational capacity, request complexity, data quality, or differences in administrative workflows.

### 2.2 Administrative Closure Time by Request Category

Administrative closure times varied across the three street maintenance request categories.

| Request Category | Total Requests | Median Closure Time | Average Closure Time |
|---|---:|---:|---:|
| Pothole | 38,438 | 0.91 days | 1.59 days |
| Cave-in | 9,647 | 2.32 days | 3.82 days |
| Failed Street Repair | 3,487 | 2.71 days | 5.37 days |

Failed Street Repair requests had the longest median and average administrative closure times.

The percentage of valid closed requests taking more than seven days to close also differed by category:

- Pothole: 1.73%
- Cave-in: 10.73%
- Failed Street Repair: 14.71%

**Business implication:** Cave-in and Failed Street Repair requests may benefit from additional workflow analysis because they show longer administrative processing times. These differences do not, by themselves, demonstrate inefficiency; the categories may involve different procedures or levels of complexity.

### 2.3 Borough-Level Closure Time Differences

The Bronx showed relatively long administrative closure times compared with other boroughs.

Its overall median administrative closure time was approximately 2.14 days, compared with a citywide median of 0.99 days.

Within the Bronx, the proportions of valid closed requests taking more than seven days were:

- Failed Street Repair: 27.76%
- Cave-in: 25.24%
- Pothole: 9.18%

**Business implication:** The Bronx may warrant a category-level review of administrative processing times. A useful next step would be to investigate whether case complexity, staffing, routing procedures, or other factors contribute to these differences.

### 2.4 Monthly Request Volume

Street maintenance request volume fluctuated throughout 2025.

May recorded the highest number of requests, with 5,558, followed closely by June with 5,512.

November recorded 2,589 requests, the lowest monthly volume in the dataset.

**Business implication:** Monthly demand patterns may help operations teams plan staffing, monitor workload changes, and prepare for periods of higher request volume.

However, one year of data is insufficient to establish a recurring seasonal pattern. Additional years should be analyzed before making long-term seasonal staffing decisions.

### 2.5 Data Interpretation and Limitations

The findings should be interpreted with several limitations in mind:

1. **Snapshot timing:** Request statuses reflect October 21, 2026, rather than December 31, 2025.
2. **Administrative closure:** A closed 311 request does not necessarily indicate that a physical repair was completed.
3. **Closure-time validation:** Six records with negative closure durations were excluded from closure-time calculations.
4. **Causation:** Differences across boroughs and categories do not establish the causes of operational performance.
5. **Scope:** The analysis covers selected NYC DOT Street Condition requests created during 2025, not all NYC 311 complaints.

These limitations are important when translating analytical results into operational recommendations.

## 3. Business Recommendations

The following recommendations are based on patterns observed in NYC 311 street maintenance requests created during 2025. They are proposed areas for investigation and improvement, not conclusions about the causes of operational performance.

### Recommendation 1: Prioritize a Review of Unresolved Requests in Queens

**Finding:** Queens accounted for 2,649 of the 3,142 unresolved requests (84.3%) as of October 21, 2026. Its unresolved rate was 12.57%, compared with substantially lower rates in the other boroughs.

**Recommended action:**

- Review unresolved requests in Queens by complaint category, creation month, and request age.
- Identify whether unresolved requests are concentrated in particular periods or geographic areas.
- Compare case assignment, status updates, and administrative workflows with other boroughs.
- Investigate whether differences in request complexity or data recording practices explain the concentration.

**Potential business value:** A targeted review could help operations teams identify the reasons for the unresolved workload and determine whether corrective action is necessary.

**Suggested success measures:** Number of unresolved requests, unresolved rate, age of unresolved requests, and percentage of older cases reviewed.

### Recommendation 2: Investigate Longer Closure Times for Specific Request Categories

**Finding:** Failed Street Repair and Cave-in requests had longer median administrative closure times than Pothole requests.

Failed Street Repair requests had a median closure time of 2.71 days, compared with 2.32 days for Cave-in and 0.91 days for Pothole requests.

**Recommended action:**

- Review the administrative workflows for Cave-in and Failed Street Repair requests.
- Examine whether certain processing stages contribute to longer closure times.
- Compare category-level closure times across boroughs.
- Determine whether different request types require separate performance targets.

**Potential business value:** Understanding differences in administrative processing could support more appropriate performance monitoring and help identify opportunities to streamline workflows.

**Suggested success measures:** Median closure time by category, percentage of valid closed requests exceeding seven days, and changes in these measures over time.

### Recommendation 3: Conduct a Targeted Closure-Time Review in the Bronx

**Finding:** The Bronx had a median administrative closure time of approximately 2.14 days, compared with the citywide median of 0.99 days.

The proportion of valid closed requests exceeding seven days was particularly high for Failed Street Repair (27.76%) and Cave-in (25.24%).

**Recommended action:**

- Examine closure times separately for each request category.
- Identify whether long-running requests are concentrated in specific months or operational workflows.
- Review whether request complexity, routing procedures, or staffing patterns contribute to the observed differences.
- Compare findings with boroughs showing shorter administrative closure times.

**Potential business value:** A focused review could help distinguish expected processing differences from potentially avoidable administrative delays.

**Suggested success measures:** Median closure time by category, percentage of requests exceeding seven days, and number of unusually long-running cases.

### Recommendation 4: Use Monthly Request Trends to Support Workload Planning

**Finding:** May and June recorded the highest request volumes, with 5,558 and 5,512 requests, respectively.

**Recommended action:**

- Monitor monthly request volumes by borough and complaint category.
- Compare demand patterns with staffing and operational capacity data, if available.
- Analyze multiple years of request data to determine whether high-volume periods recur.
- Use historical patterns to support workload forecasting and resource planning.

**Potential business value:** Better visibility into changes in request volume could help teams anticipate workload pressures and plan resources more effectively.

**Suggested success measures:** Monthly request volume, workload per operational team, and changes in administrative closure times during higher-volume periods.

### Recommendation 5: Establish a Consistent Operational KPI Monitoring Process

**Finding:** The analysis revealed substantial differences in unresolved rates and administrative closure times across boroughs and complaint categories.

**Recommended action:**

- Create a recurring dashboard review process for operational performance.
- Monitor total requests, administrative closure rate, unresolved requests, and median closure time.
- Segment performance by borough, complaint category, and reporting period.
- Establish clear definitions for each KPI and consistently document the reporting snapshot date.
- Investigate significant changes before interpreting them as performance improvements or declines.

**Potential business value:** Consistent KPI monitoring could improve visibility into administrative workloads and support more timely, evidence-based operational decisions.

**Suggested success measures:** Regularity of dashboard reviews, completeness of KPI reporting, and percentage of identified anomalies investigated.

### Recommended Implementation Priorities

| Priority | Recommendation | Rationale |
|---|---|---|
| High | Review unresolved requests in Queens | Largest concentration of unresolved requests |
| High | Investigate category-level closure times | Clear differences between request categories |
| Medium | Review Bronx closure times | Longer administrative processing times |
| Medium | Establish recurring KPI monitoring | Supports consistent operational visibility |
| Longer-term | Analyze multi-year demand patterns | Helps validate trends for resource planning |

These recommendations should be evaluated with operational stakeholders before implementation. Additional information about staffing, service procedures, request complexity, and physical repair outcomes would be needed to assess root causes and determine appropriate interventions.