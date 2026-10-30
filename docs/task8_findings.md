# Task 8: Team Productivity & Delivery Health Findings

**Date:** 2026-10-30  
**Scope:** 16 Agile Delivery Teams across 38 Sprints (`SP-01` to `SP-38`)  
**Data Sources:** `warehouse.fact_task` (28,848 tasks), `warehouse.dim_team`, `warehouse.dim_sprint`  
**Governed Metric Views:** `metrics.m22_task_completion_rate`, `metrics.m23_on_time_delivery_rate`, `metrics.m24_velocity`, `metrics.m25_average_cycle_time`

---

## 1. Executive Summary

This report analyzes agile engineering delivery, flow efficiency, and quality signals across all 16 product teams and 38 sprint cycles at GrowMar. Delivery is evaluated multidimensionally: **throughput** (story points velocity), **speed** (cycle time in days), **predictability** (on-time delivery rate), and **stability** (reopened rework rate and blocked bottlenecks).

---

## 2. Dashboard Screenshots

![Team velocity and cycle time](screenshots/task8_velocity_cycletime.png)

![Sprint trends and rework analysis](screenshots/task8_sprints_rework.png)

---

## 3. Three Verified Numerical Findings

### Finding 1: Headcount-Driven Velocity vs. Individual Throughput Efficiency
- **The Numbers:**  
  On gross output, **Support Tooling (T12)** generated the highest total velocity in the company with **10,274 story points** across 38 sprints (averaging **270.4 points/sprint**), followed by **Sales Enablement (T16)** with **8,419 story points** (averaging **221.6 points/sprint**).  
- **Context & Per-Capita Reality:**  
  However, both teams are the largest in the company (58 and 45 members, respectively). Normalizing by team size reveals that T12 delivers **4.66 points per member per sprint**, which is actually below the company median of **5.30 points**.  
  In contrast, smaller squads achieve significantly higher per-capita flow: **Product Squad (T06)** (15 members) delivered **6.29 points/member/sprint**, and **Design Systems (T07)** (10 members) delivered **5.94 points/member/sprint**. Gross velocity reflects team scale, not necessarily higher individual engineering speed.

### Finding 2: Flow Bottleneck & Impediment Concentration in Support Tooling
- **The Numbers:**  
  Across the 38 sprints, **177 tasks in Support Tooling (T12)** were flagged with `status = 'Blocked'`, representing **17.7% of all blocked work in the entire company** (999 blocked tasks total). Similarly, **Internal IT (T15)** experienced **111 blocked tasks** (11.1% of company total).  
- **What It Indicates:**  
  Teams supporting external operations or cross-functional systems suffer from high dependency bottlenecks and waiting times. Furthermore, T11 (Growth Marketing) logged the longest average cycle time across the company at **5.06 days** (along with the lowest on-time delivery rate of **91.30%**), demonstrating that marketing automation tasks suffer from external approval latency.

### Finding 3: Exemplary Flow Predictability in QA Automation and Data Platform
- **The Numbers:**  
  **Data Platform (T08)** achieved the highest on-time delivery rate in the organization at **94.81%** (840 of 886 completed tasks delivered on time), accompanied by the fastest average cycle time of **4.42 days** (well below the company average of 4.80 days).  
  Similarly, **QA Automation (T04)** achieved an exceptional **94.01% on-time delivery rate** and maintained the lowest blocked task count in the engineering organization (only **14 blocked tasks** across all 38 sprints, compared to an average of 62.4 per team). Clean technical ownership and automated CI/CD pipelines yield superior delivery predictability.

---

## 4. Think for Yourself: Defending Team Health

> **Question:** *"Team A has the best velocity but the most reopened tasks. Which team is healthier? Defend your view."*

### The Dilemma:
In agile organizations, managers often gravitate toward velocity as a proxy for success. However, high throughput accompanied by frequent reopening represents a critical operational risk.

### My Position:
**Team A is NOT the healthier team.** A team with moderate, predictable velocity and low rework (such as Team B, e.g., QA Automation / Platform Core) is significantly healthier, more sustainable, and more valuable to the organization.

### Defense & Supporting Logic:
1. **The Phantom Velocity Illusion:**  
   When a task is reopened, it means user acceptance testing (UAT) or quality assurance failed. The team marked story points as "delivered," but those story points immediately generated unbudgeted defect triage, context switching, and regression risk in subsequent sprints. The velocity was partially an accounting illusion because the "definition of done" was violated.
2. **The Compounding Cost of Context Switching:**  
   Empirical software research shows that context switching between new feature development and fixing recently "completed" bugs consumes 20% to 40% of cognitive bandwidth. Reopened tasks disrupt sprint commitments, inflate lead times, and erode stakeholder trust.
3. **Engineering Morale and Burnout:**  
   Teams with chronic rework experience higher burnout. Developers are forced into firefighting mode, testing cycles become stressful, and technical debt compounds.
4. **Conclusion:**  
   True team health is defined by **Flow Predictability and Quality (First-Time-Right delivery)**, not raw volume. High on-time delivery, low cycle time variance, and minimal rework represent genuine organizational health.

---

## 5. Fair Team Comparison Principles & Contextual Factors

Comparing teams directly on raw metrics without context leads to dysfunctional behavior and distorted rankings. When analyzing PulseIQ data:

1. **Team Size Disparities:**  
   Teams vary from 10 members (`Design Systems`) to 58 members (`Support Tooling`). Gross velocity cannot be compared directly without per-member normalization.
2. **Work Type & Cognitive Complexity:**  
   `fact_task` contains 4 distinct task types: **Feature (12,899)**, **Bug (8,773)**, **Chore (4,325)**, and **Spike (2,851)**. A team working predominantly on research Spikes or complex architecture (e.g., `ML Services` or `Platform Core`) naturally has different cycle times than a team executing operational Chores (`Internal IT`).
3. **Estimation Baselining:**  
   Story points are relative to each team's internal estimation poker. A 5-point story in Team T01 does not equal a 5-point story in Team T07. Comparison across teams should focus on sprint-over-sprint trend consistency and delivery reliability rather than raw point counts.

---

## 6. Checklist & References

- [x] Written rules and metric definitions visible
- [x] Explicit treatment of cancelled tasks documented
- [x] 2 teams verified by hand from database records (`docs/task8_verification_table.md`)
- [x] 3 numerical findings documented with verified numbers
- [x] Defended position on velocity vs. rework

### Reference Links:
- [Streamlit](https://github.com/streamlit/streamlit) · https://github.com/streamlit/streamlit
- [Plotly](https://github.com/plotly/plotly.py) · https://github.com/plotly/plotly.py
- [DuckDB](https://github.com/duckdb/duckdb) · https://github.com/duckdb/duckdb

