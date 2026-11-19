# Task 18: Self-Service Governed KPI Explorer & Privacy Guardrail Report

**Author:** Minnu Biju  
**Project:** PulseIQ Workforce Analytics  
**Phase:** 4 — Release (Task 18)  
**Integrated Page:** `pages/13_KPI_Explorer.py`  
**Execution Date:** November 2026  

---

## 1. Overview & Business Objective
Task 18 delivers a self-service analytical explorer that allows stakeholders to query any of PulseIQ's 28 conformed metrics across arbitrary dimensional drill-downs:
$$\text{Company} \longrightarrow \text{Department} \longrightarrow \text{Team}$$

While self-service democratizes data access, unconstrained aggregation introduces severe **deanonymization risks**. If an employee or manager queries an aggregated metric (e.g. average gross salary, flight risk score, or exit percentage) over a micro-cohort of 1 to 3 people, the mathematical aggregation collapses into individual-level disclosure.

Task 18 solves this by embedding dynamic **Role-Based Access Control (RBAC)** and an automated **Small-Group Privacy Suppression Guardrail**.

---

## 2. Role-Based Access Control (RBAC) Architecture

Access behavior is configured via `demo_users.csv` covering 4 enterprise personas:

| User ID | Username | Persona Name | Assigned Role | Assigned Scope | Permitted Drill-Downs | Privacy Enforcement Behavior |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| **U01** | `admin_user` | System Administrator | **ADMIN** | Global Enterprise | Company → Dept → Team | Full platform access. Privacy masking active on public dashboards; full audit on quarantine. |
| **U02** | `tejas_ceo` | Tejas Chowdhury (CEO) | **EXECUTIVE** | Company-Wide Consolidated | Company → Department | Company-wide view, high-level summaries. Small cohorts (<5 or <10) masked. |
| **U03** | `hr_director` | Ananya Sen (HR Lead) | **HR** | People & Talent Ops | Company → Dept → Team | Deep workforce, leave, and attrition visibility. Sub-threshold team cohorts strictly masked. |
| **U04** | `eng_manager` | Bhavana DSouza | **MANAGER** | Dept D01 (Engineering) | Assigned Dept → Assigned Team | Scoped strictly to D01/T01. Cannot view other departments' sensitive records. |
| **U05** | `small_team_mgr` | Priya Sharma | **MANAGER** | Micro-Team T07 (Design Systems - 2 members) | Assigned Squad (2 members) | **Privacy Break-Test Persona.** Sensitive metrics intercepted and suppressed. |

---

## 3. Small-Group Privacy Suppression Rules

From the certified `metrics.metric_catalog`, every governed metric carries an explicit `min_group_size` constraint:

| Metric Category | Target Metrics | Minimum Group Size ($K$) | Rationale |
| :--- | :--- | :---: | :--- |
| **Headcount & Movement** | M01 (Headcount), M02 (Hires), M03 (Exits) | **5 employees** | Prevents pinpointing individual exit/join dates in small operational units. |
| **Compensation & Payroll** | M07 (Gross Pay), M08 (Net Pay), M09 (Payroll Cost), M10 (Cost/Head) | **5 employees** | Protects individual executive and employee compensation confidentiality. |
| **Turnover & Attrition Risk**| M04 (Monthly Attrition), M05 (Rolling Attrition), M06 (Voluntary), M27 (High Risk Share) | **10 employees** | High-sensitivity category. Small teams experience erratic % spikes that de-anonymize departures. |
| **Attendance & Leave** | M13 (Attendance), M14 (Late Arrivals), M15 (LOP Days) | **5 employees** | Protects personal medical and leave circumstances from casual team inspection. |

### Suppression Logic:
$$\text{Output}(C) = \begin{cases} 
\text{Metric Value}, & \text{if } \text{Cohort Size}(C) \ge K \\
\text{"[SUPPRESSED: Size } N < K \text{ to protect privacy]"}, & \text{if } \text{Cohort Size}(C) < K 
\end{cases}$$

---

## 4. Privacy Break-Test Lab Results

An adversary or curious manager was simulated attempting to query sensitive metrics across micro-cohorts of sizes 1, 2, and 3:

### Test 1: Executive Office (D00, Cohort Size = 1)
- **Target:** M01 (Headcount), M07 (Gross Pay), M09 (Employer Cost).
- **Adversary Goal:** Determine CEO Tejas Chowdhury's statutory compensation.
- **Guardrail Action:** Cohort size $N=1 < K=5$. The engine intercepted the query and output `[SUPPRESSED: Size 1 < 5]`.
- **Result:** **PASS (Zero compensation leak).**

### Test 2: Legal & Compliance (D10, Cohort Size = 7)
- **Target:** M04 (Monthly Attrition Rate, threshold = 10).
- **Adversary Goal:** Determine if an employee who resigned in D10 shows up in the department attrition percentage.
- **Guardrail Action:** Cohort size $N=7 < K=10$. Value masked to `[SUPPRESSED: Size 7 < 10]`.
- **Result:** **PASS (Departure shielded).**

### Test 3: Micro-Team T07 (Design Systems Squad, Cohort Size = 2)
- **Target:** Priya Sharma (Manager) querying squad attrition risk (M27) and average gross compensation (M07).
- **Adversary Goal:** Determine which of the two squad members has a "High Risk" attrition score.
- **Guardrail Action:** Cohort size $N=2 < K=10$ and $N=2 < K=5$. Both values suppressed.
- **Result:** **PASS (Identity protected).**

---

## 5. Strategic Decision: Manager with a Team of 3 Looking at Attrition

> **Core Scenario:** *What is the policy decision for a manager with a team of 3 when looking at attrition or another sensitive metric?*

### The Dilemma:
In a team of 3, if 1 employee resigns, the mathematical team attrition rate becomes:
$$\text{Attrition Rate} = \frac{1 \text{ exit}}{3 \text{ members}} \times 100\% = 33.33\%$$
If no one resigns, the attrition rate is $0.0\%$.

Because the manager directly supervises and interacts daily with all 3 individuals, publishing a team-level attrition metric of $33.3\%$ instantly confirms to the entire team and management who the departing individual is. Furthermore, if an AI predictive model publishes a $33.3\%$ High Attrition Risk score for that team, the manager can easily deduce which of their 3 direct reports was flagged, leading to unconscious bias, project isolation, or premature performance penalties.

### The PulseIQ Governance Decision:
1. **Mandatory Hard Suppression at the Team Level:**  
   The team-level attrition rate (M04/M05) and attrition risk (M27) **MUST BE STRICTLY SUPPRESSED** with the message:  
   `[SUPPRESSED: Team cohort size 3 < 10 to protect employee privacy]`.
2. **Elevation to Departmental Benchmarks:**  
   The manager is granted access to the **Department-level aggregate** (e.g. `D01 - Engineering`, 167 staff, 0.60% attrition). This allows the manager to evaluate organizational turnover trends without compromising the personal privacy of direct reports.
3. **Qualitative Channel Mandate:**  
   Career satisfaction, retention concerns, and departure logistics for micro-teams must be handled exclusively through confidential 1-on-1 conversations and private HR business partner workflows, never through public self-service dashboards.

---

## 6. Evidence Screenshots

1. **Executive / Admin View:**  
   `Phase_4/Task18_KPI_Explorer_Privacy/Task18_Role_View_Executive_Admin.png`  
   Demonstrates company-wide and departmental drill-downs where large departments show compliant metrics while micro-cohorts (e.g. `D00`, $n=1$) are masked.
2. **Manager Privacy Break-Test Lab:**  
   `Phase_4/Task18_KPI_Explorer_Privacy/Task18_Role_View_Manager_Privacy_Break_Test.png`  
   Demonstrates real-time interception of micro-team ($n=2$) compensation and attrition queries.

