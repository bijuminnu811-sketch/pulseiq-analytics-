# PulseIQ Analytics

An end-to-end HR, finance and delivery analytics project built as part of my Data Analytics internship. PulseIQ turns raw company data into a governed data model, quality-checked KPIs, AI-driven risk signals and an executive health scorecard.

**Author:** Minnu Biju

---

## Highlights

- Star-schema data model with 29 CSV tables (dimensions and facts) loaded into DuckDB
- Automated data quality gatekeeper with a catalog of checks and a test harness
- Metric layer with a KPI dictionary and traffic-light targets
- HR analytics: leave, attrition, exits and tenure, predicted risk
- Delivery analytics: sprint rework, velocity and cycle time
- Finance analytics: budget variance, P&L, invoices, ageing and cash flow
- AI signals: anomaly detection, attrition risk and forecast error
- Executive Health Scorecard that brings every area into one view

## Tech Stack

Python, Pandas, DuckDB, SQL, Streamlit, Excel/CSV, ReportLab (PDF reports), Git and GitHub

## Project Structure

```
pulseiq_new
|-- Phase_1                  Data foundation
|   |-- 03_Data              PulseIQ_Dataset.xlsx and csv/
|   |-- 05_Starter           etl.py, load_to_duckdb.py, requirements.txt
|   `-- docs                 Data quality, metric layer, star schema, Phase 1 report
|
|-- Phase_2                  People, delivery and budget analytics
|   |-- Task 6               Leave patterns and unusual activity
|   |-- Task 7               Exits, tenure and predicted attrition risk
|   |-- Task 8               Sprint rework, velocity and cycle time
|   |-- Task 9               KPI reconciliation and trend audit
|   `-- Task 10              Budget variance ranking and recommendations
|
|-- Phase_3                  Finance, AI signals and executive view
|   |-- Task11_Profit_Loss
|   |-- Task12_Invoices_Receivables_Cash_Flow
|   |-- Task13_Cross_Department_Impact
|   |-- Task14_AI_Signals
|   `-- Task15_Executive_Health_Scorecard
|
|-- pages                    Streamlit dashboard pages
`-- README.md
```

## Phase Summary

### Phase 1: Data Foundation
Designed the star schema, built the ETL pipeline, loaded the data into DuckDB, defined the metric layer and added an automated data quality gatekeeper that was proven with deliberately corrupted test rows.

### Phase 2: Analytics (Tasks 6 to 10)

| Task | Focus |
|------|-------|
| 6 | Leave trends and unusual leave |
| 7 | Exits, tenure, predicted risk |
| 8 | Sprint rework, velocity, cycle time |
| 9 | KPI reconciliation and trend audit |
| 10 | Budget variance ranking and recommendations |

### Phase 3: Finance, AI and Executive View (Tasks 11 to 15)

| Task | Focus |
|------|-------|
| 11 | Profit and loss, expense analysis, top vendors |
| 12 | Invoices, receivables ageing, cash flow by client |
| 13 | Cross-department impact: overtime vs attrition |
| 14 | AI signals: anomaly money risk, attrition risk, forecast vs actual error |
| 15 | Executive Health Scorecard |

Every task folder contains dashboard screenshots and a written report with findings.

## Reports

- Phase_1/docs/DataAnalytics_Minnu_Phase1_Report.pdf
- Phase_2/DataAnalytics_MinnuBiju_Phase2_Report.pdf
- Phase_3/DataAnalytics_MinnuBiju_Phase3_Report.pdf

## How to Run

```bash
git clone https://github.com/bijuminnu811-sketch/pulseiq-analytics-.git
cd pulseiq-analytics-

python -m venv .venv
.venv\Scripts\activate
pip install -r Phase_1/05_Starter/requirements.txt

python Phase_1/05_Starter/etl.py
python Phase_1/05_Starter/load_to_duckdb.py

streamlit run pages/12_Executive_Health_Scorecard.py
```

## Key Learnings

- Modeling data as a star schema keeps KPIs consistent across teams
- Automated data quality checks catch bad data before it reaches a dashboard
- Reconciling every KPI back to its source builds trust in the numbers
- A single executive scorecard makes cross-department trade-offs visible

## Contact

**Minnu Biju**
GitHub: [bijuminnu811-sketch](https://github.com/bijuminnu811-sketch)