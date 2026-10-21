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
