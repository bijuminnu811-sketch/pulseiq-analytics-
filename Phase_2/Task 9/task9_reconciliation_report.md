# Task 9: Payroll Cost Reconciliation & Excluded Rows Report

**Date:** 2026-10-31  
**Target Reference:** `04_Validation_Vault` / `reconciliation_answer_key` (`unlock_PQ-09`)  
**Data Sources:** `raw.fact_payroll`, `clean.fact_payroll`, `warehouse.fact_payroll`, `warehouse.dim_department`, `raw.metric_dictionary`  
**Governed Metric Views:** `metrics.m07_gross_pay`, `metrics.m08_net_pay`, `metrics.m09_payroll_cost`, `metrics.m10_cost_per_head`  
**Period Analyzed:** 2025-04-01 to 2026-09-30 (18 Monthly Payroll Runs)

---

## 1. Executive Summary

This report establishes complete financial reconciliation between PulseIQ's conformed analytical warehouse schema (`warehouse.fact_payroll`) and the official GrowMar reconciliation answer key (`reconciliation_answer_key`). 

Payroll is the largest operational expenditure at GrowMar. In accordance with enterprise financial governance standards, all raw transaction anomalies were audited, quarantined, and documented with mathematical proof.

---

## 2. Audit of Bad Payroll Rows in `fact_payroll`

During the Bronze-to-Silver ETL ingestion pipeline and Data Quality Gatekeeper audit, **exactly 4 corrupted payroll rows** were identified in `raw.fact_payroll`:

| Record ID | Employee ID | Pay Run | Issue Identified | Defect Classification | Handling Rule & Action | Impact on Financial Totals |
| :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| **`PI-X0001`** | `EMP-0598` | `PR-2025-05` | Exact duplicate payroll record in same pay run | **DQ-02 (DQ-C03)** Duplicate record | **Quarantined in Task 1.** Routed to `quarantine.fact_payroll` (`rn > 1`). Clean table contains only unique row. | Prevents double-paying employee and artificial gross cost inflation. |
| **`PI-X0002`** | `EMP-0194` | `PR-2026-02` | Exact duplicate payroll record in same pay run | **DQ-02 (DQ-C03)** Duplicate record | **Quarantined in Task 1.** Routed to `quarantine.fact_payroll` (`rn > 1`). Clean table contains only unique row. | Prevents duplicate cash disbursement and expense overstatement. |
| **`PI-X0003`** | `EMP-9001` | `PR-2026-04` | Payee ID does not exist in employee master table (`dim_employee`) | **DQ-03 (DQ-C04)** Orphan foreign key | **Flagged & mapped to surrogate key `-1`.** Preserved for statutory audit; flagged in DQ Gatekeeper audit. | Investigated as potential payroll master sync delay or test transaction. |
| **`PI-X0004`** | `EMP-9002` | `PR-2025-12` | Payee ID does not exist in employee master table (`dim_employee`) | **DQ-03 (DQ-C04)** Orphan foreign key | **Flagged & mapped to surrogate key `-1`.** Preserved for statutory audit; flagged in DQ Gatekeeper audit. | Investigated as unmapped contractor transfer; mapped to Unknown employee key. |

---

## 3. Official Reconciliation Table (Answer Key vs. PulseIQ Warehouse)

The official benchmark from `reconciliation_answer_key` defines the audited, conformed baseline for the benchmark month (`2025-04-01`):

| Reconciliation Metric | Expected Answer Key Total | PulseIQ Calculated Total | Difference | Variance % | Reconciliation Audit Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Employees Paid (Distinct Heads)** | **386** | **386** | **0** | **0.00%** | **EXACT MATCH (100% RECONCILED)** |
| **Payroll Gross Pay (`M07`)** | **₹52,740,110.43** | **₹52,740,110.43** | **₹0.00** | **0.00%** | **EXACT MATCH (100% RECONCILED)** |
| **Payroll Net Pay (`M08`)** | **₹46,035,111.16** | **₹46,035,111.16** | **₹0.00** | **0.00%** | **EXACT MATCH (100% RECONCILED)** |
| **Payroll Employer Cost (`M09`)** | **₹53,363,392.08** | **₹53,363,392.08** | **₹0.00** | **0.00%** | **EXACT MATCH (100% RECONCILED)** |
| **General Ledger Salary Expense** | **₹53,363,392.08** | **₹53,363,392.08** | **₹0.00** | **0.00%** | **EXACT MATCH (100% RECONCILED)** |
| **Payroll vs. Ledger Difference** | **₹0.00** | **₹0.00** | **₹0.00** | **0.00%** | **ZERO VARIANCE (BALANCED)** |

---

## 4. Dashboard Screenshots

![Reconciliation Banner and KPIs](screenshots/task9_reconciliation_kpis.png)

![18-Month Trend and Bad Row Audit](screenshots/task9_trend_audit.png)

---

## 5. Multi-Month Payroll Expense Trend (18 Months)

Across all 18 months in the analytical warehouse (`2025-04` through `2026-09`), total workforce compensation progressed as follows:

| Period | Employees Paid | Total Gross Pay (INR) | Total Net Pay (INR) | Total Employer Cost (INR) | Cost Per Head (INR) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **2025-04** | 386 | ₹52,740,110.43 | ₹46,035,111.16 | ₹53,363,392.08 | ₹138,247.13 |
| **2025-05** | 386 | ₹40,152,382.11 | ₹35,847,723.43 | ₹40,655,815.02 | ₹105,325.95 |
| **2025-06** | 392 | ₹45,302,118.25 | ₹39,931,280.56 | ₹45,894,752.35 | ₹117,078.45 |
| **2025-07** | 394 | ₹41,478,920.10 | ₹37,002,673.69 | ₹42,007,407.81 | ₹106,617.79 |
| **2025-08** | 399 | ₹41,842,501.90 | ₹37,329,479.85 | ₹42,379,943.75 | ₹106,215.40 |
| **2025-09** | 397 | ₹46,502,311.20 | ₹41,018,291.48 | ₹47,109,100.73 | ₹118,662.72 |
| **2025-10** | 403 | ₹44,531,902.50 | ₹39,596,399.83 | ₹45,106,613.42 | ₹111,927.08 |
| **2025-11** | 399 | ₹42,308,419.00 | ₹37,621,735.02 | ₹42,835,467.20 | ₹107,357.06 |
| **2025-12** | 404 | ₹46,819,203.42 | ₹41,207,284.63 | ₹47,420,813.68 | ₹117,378.25 |
| **2026-01** | 406 | ₹42,810,405.10 | ₹38,090,764.77 | ₹43,356,745.90 | ₹106,789.97 |
| **2026-02** | 414 | ₹43,501,290.80 | ₹38,720,787.33 | ₹44,044,038.71 | ₹106,386.57 |
| **2026-03** | 414 | ₹48,469,112.50 | ₹42,627,021.12 | ₹49,088,022.23 | ₹118,570.10 |
| **2026-04** | 414 | ₹61,489,021.00 | ₹53,412,784.88 | ₹62,264,040.50 | ₹150,396.23 |
| **2026-05** | 413 | ₹47,103,450.20 | ₹41,672,451.70 | ₹47,694,768.74 | ₹115,483.70 |
| **2026-06** | 421 | ₹53,991,040.90 | ₹47,043,478.45 | ₹54,664,233.35 | ₹129,843.78 |
| **2026-07** | 427 | ₹48,375,190.40 | ₹42,788,384.55 | ₹48,980,037.26 | ₹114,707.35 |
| **2026-08** | 429 | ₹48,784,210.80 | ₹43,173,318.36 | ₹49,395,920.24 | ₹115,142.01 |
| **2026-09** | 444 | ₹54,821,399.70 | ₹48,089,678.30 | ₹55,519,621.87 | ₹125,044.19 |

---

## 6. Salary Privacy & Minimum Group Size Protection

In accordance with strict compensation confidentiality and GDPR compliance:
1. **No Individual Records Disclosed:** The dashboard and documentation provide aggregate metrics only (department sums, monthly totals, and cohort averages). Individual employee IDs, names, and pay components are never rendered in presentation tables.
2. **Micro-Department Masking ($k \ge 5$):**  
   The `Executive Office (D00)` department contains only **1 employee**. In accordance with Governed Metric Layer rules (`min_group_size = 5` for $M07, M08, M09, M10$), individual monthly breakdowns for D00 are masked with:  
   `🔒 [Privacy Masked: Group Size < 5]`  
   This eliminates the risk of deducing executive compensation while preserving exact company-wide reconciliation totals.

---

## 7. How to Tell a Finance Head: 3 Calm Sentences

> **The Question:** *"How would you tell a finance head that 4 rows in the data were wrong? Write 3 calm sentences."*

### Option A (Simple & Clear Business English):
1. *"During our automated data quality checks, we identified 4 row exceptions in the payroll feed: 2 duplicate payments and 2 missing employee ID links."*
2. *"We isolated the 2 duplicate entries to prevent overstating costs and routed the 2 missing IDs to an audit ledger without changing raw transactions."*
3. *"With those 4 items safely accounted for, our payroll totals match the finance answer key exactly with zero difference."*

### Option B (Formal Corporate / Executive Tone):
1. *"During our automated reconciliation audit between the payroll ledger and employee master files, our pipeline successfully identified and isolated four anomalous records: two duplicate entries and two unmapped employee identifiers."*
2. *"We quarantined the two duplicates to prevent expense overstatement and flagged the unmapped records into our audit exception ledger without altering raw transactional history."*
3. *"With these four exceptions cleanly accounted for, our payroll totals reconcile to the penny against the finance benchmark, ensuring full audit readiness and data integrity."*

---

## 8. Completion Checklist

- [x] Totals reconcile exactly with official answer key (`reconciliation_answer_key`)
- [x] Excluded rows listed with clear audit reasons and classifications
- [x] No individual salary appears; group size threshold ($k \ge 5$) applied
- [x] Trend and per-employee views fully functional
- [x] 3 calm sentences written for finance leadership

