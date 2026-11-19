# Task 16: Automated Report Builder & Release Candidate (v1.0.0-rc1)

**Author:** Minnu Biju  
**Project:** PulseIQ Workforce Analytics  
**Phase:** 4 — Release (Task 16)  
**Release Tag:** `v1.0.0-rc1`  
**Execution Date:** November 2026  

---

## 1. Overview & Objective
Task 16 implements an automated monthly report builder (`build_report.py`) that compiles an executive-ready monthly report pack in both **PDF** and **Markdown** formats using a single CLI command.

The report extracts verified metrics strictly from the conformed PulseIQ warehouse and governed metric layer (`pulseiq.duckdb`), presenting unified cross-domain intelligence across HR, Finance, Commercial Invoicing, and Engineering Delivery.

---

## 2. One-Command Execution & Verification

### Command Used:
```bash
# Default execution (extracts latest available month: 2026-09)
python build_report.py

# Explicit month selection
python build_report.py --month 2026-09 --output-dir Phase_4/Task16_Automated_Report
```

### Execution Log Output:
```text
[*] Connecting to pulseiq.duckdb...
[*] Extracting governed metrics for reporting month: 2026-09...
[*] Generating 3-page publication-grade PDF report...
[+] Successfully generated executive PDF report: Phase_4\Task16_Automated_Report\PulseIQ_Monthly_Report_2026-09.pdf
[*] Generating companion Markdown report...
[+] Successfully generated executive Markdown report: Phase_4\Task16_Automated_Report\PulseIQ_Monthly_Report_2026-09.md

======================================================================
 [✓] TASK 16 REPORT GENERATION COMPLETED SUCCESSFULLY
 PDF Report:      Phase_4\Task16_Automated_Report\PulseIQ_Monthly_Report_2026-09.pdf
 Markdown Report: Phase_4\Task16_Automated_Report\PulseIQ_Monthly_Report_2026-09.md
 Reporting Month: 2026-09 | Cut-off: 2026-09-30 23:59:59 UTC
======================================================================
```

---

## 3. Report Pack Contents & 5 Selected Core Tables

| Table # | Table Title | Business Purpose & Domain | Key Metrics Highlighted |
| :---: | :--- | :--- | :--- |
| **Table 1** | **Executive KPI Performance Scorecard** | High-level executive scorecard tracking performance vs target benchmarks across People, Finance, Commercial, Cash Flow, and Delivery. | Closing Headcount (441), Monthly Attrition (0.68%), Total Payroll (INR 58.0M), Revenue (INR 99.0M), Operating Margin (22.6%), DSO (58.4 days), On-Time Delivery (89.3%). |
| **Table 2** | **Dynamic Departmental Workforce Distribution** | Department-level headcount, recruitment additions, exits, and attrition rates. | Closing Headcount per department (D01: 167 down to D10: 7). Enforces privacy masking (`[SUPPRESSED]`) for cohorts under 10. |
| **Table 3** | **Departmental Payroll & Cost Structure** | Statutory compensation breakdown showing cost allocation and overtime exposure. | Paid Staff, Gross Pay, Employer PF, Employer Cost, and Overtime Ratio (Customer Support at 3.4% overtime). |
| **Table 4** | **Engineering & Delivery Velocity by Team** | Sprint performance, story point throughput, and turnaround time by engineering squad. | Teams T01–T08: Total Tasks, Completed Tasks, Story Points Velocity, On-Time Completion Rate (89.3%), Average Cycle Time (3.8 days). |
| **Table 5** | **Working Capital, Invoicing & Receivables Aging** | Commercial liquidity, billing volume, and accounts receivable risk profile. | Recognized Revenue (INR 99.0M), Operating Expenses (INR 76.6M), Net Profit (INR 22.4M), Overdue Receivables, DSO (58.4 days). |

---

## 4. Dynamic Department Handling (Next Month Extensibility)

### Architectural Design:
A frequent point of failure in reporting scripts is hardcoding department lists (e.g. `['D01', 'D02', ..., 'D10']`). In `build_report.py`, dynamic department discovery is enforced via outer dimensional joins:

```sql
SELECT 
    d.department_id,
    d.department_name,
    COALESCE(h.headcount_end, 0) AS headcount,
    COALESCE(h.hires, 0) AS hires,
    COALESCE(h.exits, 0) AS exits,
    CASE 
        WHEN COALESCE(h.headcount_start, 0) >= 10 
        THEN ROUND((CAST(COALESCE(h.exits, 0) AS DOUBLE) / h.headcount_start) * 100.0, 1)
        ELSE NULL 
    END AS attrition_rate_pct,
    CASE WHEN COALESCE(h.headcount_start, 0) < 10 THEN TRUE ELSE FALSE END AS is_masked
FROM warehouse.dim_department d
LEFT JOIN warehouse.fact_headcount_monthly h 
    ON d.department_id = h.department_id 
   AND h.month_start_date = CAST(? AS DATE)
WHERE d.department_id != 'ALL'
ORDER BY d.department_id
```

### Benefit:
If the business opens a new department next month (e.g., `D11 - Robotics & AI Labs`), it will be inserted into `dim_department`. The very next time `python build_report.py` executes:
- `D11` will immediately appear in Table 2 and Table 3 without any code or query changes.
- If no hires/headcount exist yet for that month, `COALESCE` safely defaults to `0`, preventing `NULL` crashes or missing department rows.

---

## 5. Dependency Pinning & Clean-Environment Notes

Dependencies in `requirements.txt` have been pinned to exact, tested production versions:
```text
duckdb==2.0.0
pandas==3.0.6
streamlit==1.66.1
plotly==7.1.0
openpyxl==3.1.5
reportlab==5.0.1
fastapi==0.158.2
uvicorn==0.54.0
pydantic==2.14.1
matplotlib==3.11.2
requests==2.34.2
```

### Clean-Environment Installation Test:
1. Clone repository to a fresh directory.
2. Initialize virtual environment: `python -m venv .venv`
3. Install pinned packages: `pip install -r requirements.txt`
4. Run report generator: `python build_report.py`
5. Verified: Exit code `0`, clean PDF and Markdown outputs created in under 3 seconds.

---

## 6. Git Release Candidate Tag

Git tag `v1.0.0-rc1` has been prepared and marked for the repository release candidate.

