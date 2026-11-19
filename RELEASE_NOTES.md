# PulseIQ Analytics — Official Release Notes (v1.0.0)

**Product:** PulseIQ Enterprise Workforce, Finance & Delivery Intelligence  
**Author:** Minnu Biju (Data Analytics Track)  
**Organization:** Zenith Nova Technologies  
**Release Version:** `v1.0.0` (Production Gold Release)  
**Release Date:** November 2026  
**Git Tag:** `v1.0.0`  
**Previous Tag:** `v1.0.0-rc1` (Release Candidate)  
**Live URL:** [https://pulseiq-analytics.streamlit.app](https://pulseiq-analytics.streamlit.app)  
**GitHub Repository:** [https://github.com/bijuminnu811-sketch/pulseiq-analytics-.git](https://github.com/bijuminnu811-sketch/pulseiq-analytics-.git)  

---

## 1. What is Included in v1.0.0

PulseIQ v1.0.0 completes the full 20-task enterprise data analytics lifecycle across Phases 1, 2, 3, and 4:

### A. Data Foundation & Engineering (Tasks 1 – 5)
- **Contract-Driven ETL (`etl.py`):** Schema-validated pipeline ingesting 29 source tables with zero row loss; dead-letter quarantine (`quarantine.*`) logging reasons for defect rows.
- **Dimensional Warehouse (`warehouse.py`):** Star-schema model in DuckDB featuring SCD Type 2 `dim_employee`, conformed dimensions, and 12 fact tables verified with 100% row count parity.
- **Data Quality Gatekeeper (`dq_gatekeeper.py`):** 14 automated SQL integrity gates with hard-stop critical policies and a fault-injection test harness.
- **Governed Metric Layer (`metric_layer.py`):** 28 official centralized SQL metric views under the `metrics` schema with dynamic small-group privacy masking.
- **Executive Portal (`app.py`):** Multi-page Streamlit portal with 3-color enterprise palette (Navy `#1E3A8A`, Emerald `#10B981`, Coral `#EF4444`).

### B. Analytical Dashboards & Insights (Tasks 6 – 15)
- **Task 6:** Attendance & Leave Trends (`pages/3_Attendance_Leave_Trends.py`)
- **Task 7:** Attrition Analytics & Risk (`pages/4_Attrition_Analytics.py`)
- **Task 8:** Team Productivity & Sprint Delivery (`pages/5_Team_Productivity.py`)
- **Task 9:** Payroll Cost & Official Reconciliation (`pages/6_Payroll_Cost_Dashboard.py`)
- **Task 10:** Budget vs Actual Variance (`pages/7_Budget_vs_Actual_KPIs.py`)
- **Task 11:** Profit & Loss Analytics (`pages/8_Profit_Loss_Analytics.py`)
- **Task 12:** Invoices, Receivables & Cash Flow (`pages/9_Invoices_Receivables_Cash_Flow.py`)
- **Task 13:** Cross-Department Impact: Overtime vs Attrition (`pages/10_Cross_Department_Impact.py`)
- **Task 14:** AI Signals Dashboard: Churn Risk, Anomaly Money Risk (`pages/11_AI_Signals_Dashboard.py`)
- **Task 15:** Executive Health Scorecard (`pages/12_Executive_Health_Scorecard.py`)

### C. Release, Governance & Handover (Tasks 16 – 20)
- **Task 16:** Automated Monthly Report Pack Builder (`build_report.py`) compiling 3-page publication-grade PDF and Markdown packs in one CLI command.
- **Task 17:** Live Streamlit Cloud Deployment with mobile-responsive viewport styling, navigation guide, zero plain-text secrets, and automated data refresh schedule.
- **Task 18:** Self-Service Governed KPI Explorer (`pages/13_KPI_Explorer.py`) with Role-Based Access Control (`demo_users.csv`) and verified small-group suppression shields ($N < 5$ / $N < 10$).
- **Task 19:** Enterprise REST API (`api.py`) built with FastAPI, exposing 5 certified metrics, interactive Swagger documentation (`/docs`), multi-hop data lineage diagrams, and column-rename blast radius analysis.
- **Task 20:** Executive Board Pack (`PulseIQ_Executive_Board_Pack.pdf`), 10-slide landscape presentation, Release Notes, and System Diagnostic Tool (`pulseiq_doctor.py`).

---

## 2. What is NOT Included

To maintain analytical rigor and prevent speculative data leaps, the following components are deliberately out of scope for v1.0.0:
1. **Customer Acquisition Cost (CAC) & Marketing Lead Funnels:** CRM lead stage data (HubSpot/Salesforce) is not integrated in the current transactional warehouse.
2. **Qualitative Employee Sentiment & Exit Interview Transcripts:** Exit reasons are tracked as categorical attributes in HR feeds, but open-ended sentiment NLP is not modeled.
3. **Write-Back Transactional Posting:** PulseIQ is an analytical read-only reporting warehouse; write-back journal voucher posting to statutory ERP systems remains decoupled.

---

## 3. Known Limitations

1. **Monthly Aggregation Grain:** While daily tasks and attendance events are preserved in fact tables, executive headcount and attrition views operate on calendar monthly grains.
2. **DuckDB Concurrency Model:** DuckDB is an in-process analytical engine. In high-concurrency production deployments (>50 concurrent web writers), DuckDB operates in `read_only=True` mode, with batch writes handled via scheduled offline ETL cycles.
3. **Quarantine Edge Cases:** One legacy test payment (`INV-00385`) remains intentionally quarantined due to deliberate customer overpayment injected during Task 1 data validation testing.

---

## 4. Deployment Information

- **Primary Production Host:** Streamlit Community Cloud ([https://pulseiq-analytics.streamlit.app](https://pulseiq-analytics.streamlit.app))
- **Repository:** `https://github.com/bijuminnu811-sketch/pulseiq-analytics-.git`
- **Branch:** `main`
- **Entry Point:** `app.py`
- **Python Runtime:** Python 3.13 / 3.12 compatible
- **Database Engine:** Embedded DuckDB 2.0.0 (`pulseiq.duckdb`, 33.3 MB)
- **REST API Server:** FastAPI 0.158 served via Uvicorn (`python -m uvicorn api:app --port 8000`)
- **System Doctor Command:** `python pulseiq_doctor.py`

---

## 5. Important Assumptions & Standards

1. **Attrition Denominator Standard:** Standardized on average monthly headcount ($H_{\text{avg}} = \frac{H_{\text{start}} + H_{\text{end}}}{2}$) over simple start headcount to prevent small-cohort percentage distortion during high-growth periods.
2. **SCD Type 2 Value Matching Principle:** Transfers between departments allocate payroll costs to the source department for days worked prior to transfer, matching economic value generation.
3. **Small-Group Suppression Threshold:** Mandated minimum cohort size of 5 employees for compensation/headcount metrics and 10 employees for attrition/flight risk metrics. Micro-cohorts below these thresholds are strictly masked with `[SUPPRESSED]`.
4. **Data Cut-off Date:** All production data is conformed through **September 30, 2026 23:59:59 UTC**.

