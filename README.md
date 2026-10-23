# PulseIQ Analytics: Workspace Setup & Validated ETL Pipeline (Task 1)

## 1. Project Overview & Objective
PulseIQ is an enterprise data analytics platform covering HR, finance, engineering ops, and workforce metrics. 

**Task 1 Objective:**
Set up the analytics workspace and version control, load all raw source feeds into a local DuckDB analytical database, and build an automated, repeatable ETL pipeline that enforces column-level **data contracts**. Any rows failing validation are routed to a **quarantine table** with written reasons, ensuring that **no row disappears silently**.

---

## 2. Architecture & Directory Structure

```text
pulseiq/
├── .gitignore               # Ignores .venv, duckdb databases, logs
├── README.md                # Task 1 report, data contract notes, & design decisions
├── etl.py                   # Main repeatable ETL pipeline & contract validator
├── 03_Data/
│   ├── PulseIQ_Dataset.xlsx # Master workbook with documentation & metadata
│   └── csv/                 # 29 raw source feeds (dimensions, facts, dictionaries)
└── 05_Starter/
    ├── etl.py               # Runner copy for 05_Starter execution
    ├── load_to_duckdb.py    # Starter raw loader script
    └── requirements.txt     # Python dependencies (DuckDB, Pandas, openpyxl, etc.)
```

### Data Layer Design (Medallion Pattern)
- **`raw` (Bronze Layer):** Raw CSV feeds ingested verbatim using DuckDB's native auto-detection without loss of source fidelity.
- **`clean` (Silver Layer):** Rows that meet 100% of the contractual data promises and validation rules.
- **`quarantine` (Dead-letter / Quarantine Layer):** Records that violated one or more contractual rules, annotated with explicit `quarantine_reason` text and timestamps for audit and remediation.
- **`clean.etl_summary`:** Audit table capturing `rows_in`, `rows_passed`, `rows_quarantined`, and data integrity check status.

---

## 3. Data Contract Notes for 3 Tables

Below are the column-level contract promises documented from the `README` and `data_contracts` specifications:

### Table 1: Task Board Feed (`fact_task`)
*Grain: One row per task on engineering team task boards.*

| Column Name | Data Type | Nullable? | Allowed Values / Validation Rules | Business Promise / Description |
| :--- | :--- | :--- | :--- | :--- |
| `task_id` | STRING | No | Unique, format `TASK-nnnnn` | Primary row identifier |
| `team_id` | STRING | No | Foreign Key in `dim_team` | Assigned product/delivery team |
| `sprint_id` | STRING | No | Foreign Key in `dim_sprint` | Sprint cycle identifier |
| `assignee_employee_id` | STRING | No | Foreign Key in `dim_employee` | Task owner/developer |
| `task_type` | STRING | No | `Feature`, `Bug`, `Chore`, `Spike` | Work category |
| `priority` | STRING | No | `P1`, `P2`, `P3`, `P4` | Urgency tier |
| `story_points` | INTEGER | No | `1, 2, 3, 5, 8, 13` (Fibonacci) | Estimated effort |
| `created_date` | DATE | No | Must be `<= started_date` (when started) | Task intake date |
| `started_date` | DATE | Yes | Blank only when `status = 'To Do'` | Work commencement date |
| `due_date` | DATE | No | Must match sprint end date | Target delivery deadline |
| `completed_date` | DATE | Yes | Required when `status = 'Done'`; must be `>= started_date` | Closure timestamp |
| `status` | STRING | No | `Done`, `In Progress`, `Blocked`, `To Do`, `Cancelled` | Workflow lifecycle state |
| `reopened_count` | INTEGER | No | Integer `>= 0` | Defect/rework counter |

### Table 2: AI Anomaly Results (`fact_anomaly`)
*Grain: One row per scored monthly anomaly record.*

| Column Name | Data Type | Nullable? | Allowed Values / Validation Rules | Business Promise / Description |
| :--- | :--- | :--- | :--- | :--- |
| `result_id` | STRING | No | Unique, format `AN-nnnn` | Anomaly inference ID |
| `source_dataset` | STRING | No | `attendance_monthly_features` \| `payroll_monthly_features` | Source dataset scored |
| `record_id` | STRING | No | Exists in source feature dataset | Traceable record identifier |
| `employee_id` | STRING | No | Exists in `dim_employee` | Subject employee |
| `period` | DATE | No | Month start or end date | Accounting/payroll period |
| `anomaly_score` | DECIMAL(4,3) | No | Normalized range `0.000` to `1.000` | Higher values indicate severe abnormality |
| `flagged` | CHAR(1) | No | `Y` or `N` | Whether anomaly threshold was breached |
| `reason_code` | STRING | No | Published catalog machine code | Algorithmic trigger code |
| `reason_text` | STRING | No | Plain English string | Human-readable explanation |
| `money_at_risk` | DECIMAL(14,2)| Yes | Numeric `>= 0`; blank for attendance rows | Financial exposure estimate |
| `model_version` | STRING | No | Semantic versioning string (e.g. `v1.2.0`) | Model artifact release tag |
| `scored_at` | TIMESTAMP | No | UTC timestamp | Model run completion time |

### Table 3: AI Attrition Risk (`fact_attrition_risk`)
*Grain: One row per employee 12-month turnover risk inference.*

| Column Name | Data Type | Nullable? | Allowed Values / Validation Rules | Business Promise / Description |
| :--- | :--- | :--- | :--- | :--- |
| `prediction_id` | STRING | No | Unique, format `AR-nnnn` | Batch prediction row ID |
| `employee_id` | STRING | No | Exists in `dim_employee` and active | Target employee |
| `department_id` | STRING | No | Exists in `dim_department` | Department as of prediction date |
| `as_of_date` | DATE | No | Consistent batch date | Scoring cohort cutoff date |
| `risk_score_12m` | DECIMAL(4,3) | No | Probability range `0.000` to `1.000` | Predicted 12-month attrition probability |
| `risk_band` | STRING | No | `Low`, `Medium`, `High` | High = Top 10%, Medium = Next 20% |
| `top_reason_1..3` | STRING | Yes | Plain English strings | Top SHAP / feature attribution drivers |
| `model_version` | STRING | No | Version text identifier | Classifier artifact version |

---

## 4. Think for Yourself: Handling Unexpected Feed Columns

> **Question:** *A feed arrives with a new, unexpected column. Should the pipeline stop, warn, or ignore it? Decide and explain.*

### Decision: **Warn and Quarantine/Staging (Schema Evolution via Managed Contract Enforcement)**

#### 1. Why NOT Silently Ignore?
Silently ignoring an unexpected column is dangerous in enterprise analytics. The new column could contain:
- Highly confidential Personally Identifiable Information (PII) or salary data accidentally leaked upstream.
- A critical business field (e.g., currency code, revised status) that shifts the meaning of existing columns.
- Silent schema drift that leads to unmonitored downstream miscalculations.

#### 2. Why NOT Immediately Hard Stop the Whole Pipeline?
Completely halting ingestion of large operational feeds for non-breaking additive changes can cause service outages, breaking daily executive dashboards and SLAs.

#### 3. Recommended Production Pattern:
1. **Preserve Untouched in Raw (Bronze Layer):** Ingest the incoming file into the `raw` schema with all columns intact, ensuring no operational data is permanently lost.
2. **Log High-Severity Warning & Alert Contract Owners:** Generate structured monitoring alerts (Slack/PagerDuty/DataOps logs) notifying data engineers that an uncontracted column was detected.
3. **Enforce Contract Conformance at Clean (Silver Layer):** The pipeline only promotes pre-negotiated, contract-compliant columns to `clean`, preventing downstream query breakage.
4. **Governance Triage:** The data producer and consumer review whether the new column should be formally added to `data_contracts.csv` in an updated contract version.

---

## 5. Pipeline Execution & Count Summary

### Running the Pipeline
The entire pipeline runs using a single command from the project root:

```bash
python etl.py
```
*(Optionally include all 12 warehouse facts: `python etl.py --all-facts`)*

### Count Summary Output
```text
====================================================================================
                    PULSEIQ ETL PIPELINE - AUDIT COUNT SUMMARY
====================================================================================
Table Name                   |   Rows In |    Passed | Quarantined | Integrity Check
------------------------------------------------------------------------------------
fact_task                    |     28868 |     28848 |          20 | MATCH (100%)
fact_anomaly                 |       405 |       405 |           0 | MATCH (100%)
fact_attrition_risk          |       430 |       430 |           0 | MATCH (100%)
fact_forecast                |        72 |        72 |           0 | MATCH (100%)
====================================================================================
[SUCCESS] Invariant Verified: Rows In = Rows Passed + Rows Quarantined across all tables.
```

### Quarantined Rows Audit Trail
In `fact_task`, 20 planted defect rows were caught and routed to `quarantine.fact_task` with written reasons:
- **12 rows** failed: `completed_date earlier than started_date;` (e.g., `TASK-02741`, `TASK-02895`, `TASK-06380`)
- **8 rows** failed: `Status is Done but completed_date is NULL;` (e.g., `TASK-03925`)

---

## 6. Completion Checklist Verification
- [x] **Pipeline runs from one command:** Executed via `python etl.py`.
- [x] **For every table, rows in = passed + quarantined:** Invariant 100% verified across all tables.
- [x] **Quarantined rows have a written reason:** Captured in `quarantine_reason` column with explicit diagnostic details.
- [x] **Idempotence proved:** Running the pipeline multiple times produces identical, collision-free counts and tables.
- [x] **Git Repository initialized & committed.**

---

## 7. Task 2: Star-Schema Analytical Warehouse (`warehouse.py`)

- **Architecture:** Built conformed dimensions (`dim_employee` SCD Type 2, `dim_department`, `dim_date`, etc.) and 12 conformed fact models joined via surrogate keys.
- **Mermaid ER Diagram:** Documented in [docs/star_schema_diagram.md](file:///c:/Users/binit/OneDrive/New%20folder/pulseiq_new/docs/star_schema_diagram.md).
- **Row Count Reconciliation:** 100% matched across all 12 fact tables against Task 1 clean outputs.
- **Orphan Resolution:**
  - `fact_payroll`: 2 orphan employee records (`PI-X0003`, `PI-X0004`) gracefully mapped to default unknown dimension member `(-1, 'EMP-UNKNOWN')`.
  - `fact_forecast`: 12 company-wide forecast rows resolved by adding consolidated member `'ALL'`.
  - `fact_invoice_payment`: 1 payment references `INV-00385`, which was quarantined in Task 1 for payment mismatch. Zero unexplained orphans.
- **Department Transfer Cost Rule:** Under the Economic Value Matching Principle and SCD Type 2 surrogate key mapping (`valid_from` to `valid_to`), an employee who transferred from Sales to Support on July 1st has their June compensation allocated **100% to Sales**.

---

## 8. Task 3: Automated Data Quality Gatekeeper (`dq_gatekeeper.py`)

- **14 Automated Tests:** Evaluates Completeness, Validity, Uniqueness, and Consistency across incoming tables.
- **Audit Table:** Results logged to `clean.dq_results` and `warehouse.dq_results`.
- **Test Harness:** Injected 7 deliberate defect rows into isolated shadow tables, confirming 100% detection rate.
- **Planted Issues Comparison:** All 11 planted defects from `04_Validation_Vault` (`dq_known_issues`) identified, audited, and cataloged in [docs/data_quality_report.md](file:///c:/Users/binit/OneDrive/New%20folder/pulseiq_new/docs/data_quality_report.md).
- **Stop vs. Warn Policy:** Defined 7 Hard Stops (balance sheet imbalances, duplicates, orphan entities, SCD overlaps) and 7 Soft Warnings (individual transaction defects routed to quarantine).

---

## 9. Task 4: Governed Metric Layer (`metric_layer.py`)

- **28 Governed Views:** Centralized under DuckDB schema `metrics.*`.
- **Metric Catalog:** Exposed via `metrics.metric_catalog` with grains, formulas, and owners.
- **Privacy Small-Group Masking:** Automatically suppresses cells where `distinct_employees < minimum_group_size` with `NULL` and `is_privacy_masked = TRUE` (e.g. protecting CEO in `D00`).
- **5 Hand-Checked Verifications:**
  1. `M01 (Headcount Sep 2026)` = 441
  2. `M07 (Gross Pay Apr 2025)` = INR 52,740,110.43 (Exact match to reconciliation key)
  3. `M09 (Payroll Cost Apr 2025)` = INR 53,363,392.08 (Exact match to reconciliation key)
  4. `M13 (Attendance Rate Sep 2026)` = 95.19%
  5. `M24 (Velocity T04 SP-38)` = 227 story points
- **Attrition Denominator Standard:** Standardized on average headcount ($H_{\text{avg}}$) over start or end headcount to prevent growth dilution or small-cohort distortion. Detailed in [docs/metric_layer_report.md](file:///c:/Users/binit/OneDrive/New%20folder/pulseiq_new/docs/metric_layer_report.md).

---

## 10. Task 5: Executive Workforce Dashboard (`app.py`)

- **Web App:** Multi-page Streamlit portal running at `http://localhost:8501`.
- **Governance:** Reads 100% from `metrics.*` views; zero raw table access.
- **3-Colour Discipline:** Corporate Navy (`#1E3A8A`), Growth Emerald (`#10B981`), and Alert Coral (`#EF4444`).
- **Pages:**
  - `app.py`: Workforce, Headcount & Talent Dynamics (5 CEO Questions Answered, KPI Cards, Growth Trend, Department Mix, Location Tier, Work Mode).
  - `pages/1_Data_Quality_Gatekeeper.py`: Live audit status table and planted issue tracker.
  - `pages/2_Metric_Catalog.py`: Searchable, filterable 28-metric catalog.

