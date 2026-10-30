# Task 8: Verification Table for Two Teams

**Date of Verification:** 2026-10-30  
**Data Sources:** `warehouse.fact_task`, `warehouse.dim_team`, `warehouse.dim_sprint`  
**Target Sprint:** `SP-38` (Sprint 38, Active Sprint)  
**Teams Audited:**
1. **Team A: Team T01 (Platform Core)** — Active Members: 35
2. **Team B: Team T04 (QA Automation)** — Active Members: 33

---

## 1. Documented Metric Rules & Definitions

| Metric Name | Business Definition & Formula | Treatment of Cancelled Tasks |
| :--- | :--- | :--- |
| **Velocity** | Total story points completed in the sprint: $$\sum_{\text{status} = 'Done'} \text{story\_points}$$ | **EXCLUDED:** Cancelled tasks contribute 0 story points. |
| **Cycle Time** | Average working/calendar days from task start to completion: $$\frac{1}{N_{\text{done}}} \sum_{\text{status} = 'Done'} (\text{completed\_date} - \text{started\_date})$$ | **EXCLUDED:** Incomplete/abandoned tasks have no valid completion date. |
| **On-Time Delivery Rate** | Percentage of completed tasks delivered on or before due date: $$\frac{N_{\text{done, on\_time}}}{N_{\text{done}}} \times 100\%$$ | **EXCLUDED:** Denominator is strictly completed deliverables. |
| **Planned Task Completion Rate** | Percentage of committed work delivered: $$\frac{N_{\text{done}}}{N_{\text{total}} - N_{\text{cancelled}}} \times 100\%$$ | **REMOVED FROM DENOMINATOR:** Scope de-scoped or cancelled is not penalized as failed delivery. |
| **Blocked Work** | Count of tasks flagged with impediment status: $$\text{COUNT}(\text{status} = 'Blocked')$$ | **INDEPENDENT:** Tracked actively across sprint lifecycle. |
| **Reopened Work** | Count of tasks that required rework after testing: $$\text{COUNT}(\text{reopened\_count} > 0)$$ | **TRACKED:** Counts tasks reopened post-review. |

---

## 2. Hand-Calculated Verification Table (Sprint SP-38)

### Team T01: Platform Core (35 Members)
- **Total Tasks Ingested:** 64
- **Cancelled Tasks:** 1 (`TASK-28681`, Story Points: 5)
- **Planned Tasks:** 64 - 1 = **63**
- **Tasks by Status:** Done = 57, In Progress = 3, Blocked = 2, To Do = 1, Cancelled = 1.
- **Done Tasks Breakdown:**
  - Story Points sum: 57 completed tasks = **202 Story Points**
  - Cycle time sum: 285.0 days across 57 tasks $\rightarrow 285.0 / 57 =$ **5.00 Days**
  - On-time tasks (`completed_on_time = 'Y'`): **52 tasks** $\rightarrow 52 / 57 \times 100\% =$ **91.23%**
  - Reopened tasks (`reopened_count > 0`): **2 tasks** (`TASK-28659` with count 2, `TASK-28670` with count 1 = 3 reopen events).
  - Blocked tasks: **2 tasks** (`TASK-28666`, `TASK-28672`).

### Team T04: QA Automation (33 Members)
- **Total Tasks Ingested:** 66
- **Cancelled Tasks:** 1 (`TASK-28821`, Story Points: 3)
- **Planned Tasks:** 66 - 1 = **65**
- **Tasks by Status:** Done = 59, In Progress = 2, Blocked = 2, To Do = 2, Cancelled = 1.
- **Done Tasks Breakdown:**
  - Story Points sum: 59 completed tasks = **227 Story Points**
  - Cycle time sum: 266.0 days across 59 tasks $\rightarrow 266.0 / 59 =$ **4.51 Days**
  - On-time tasks (`completed_on_time = 'Y'`): **56 tasks** $\rightarrow 56 / 59 \times 100\% =$ **94.92%**
  - Reopened tasks (`reopened_count > 0`): **0 tasks** (0 reopen events).
  - Blocked tasks: **2 tasks** (`TASK-28833`, `TASK-28841`).

---

## 3. Side-by-Side Verification Matrix

| Team Name | Sprint | Metric | Hand Calculation | SQL / Dashboard Value | Discrepancy | Audit Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Platform Core (T01)** | `SP-38` | Total Tasks | 64 | 64 | 0 | **VERIFIED (100% MATCH)** |
| **Platform Core (T01)** | `SP-38` | Cancelled Tasks | 1 | 1 | 0 | **VERIFIED (100% MATCH)** |
| **Platform Core (T01)** | `SP-38` | Planned Tasks | 63 | 63 | 0 | **VERIFIED (100% MATCH)** |
| **Platform Core (T01)** | `SP-38` | Completed Tasks (Done) | 57 | 57 | 0 | **VERIFIED (100% MATCH)** |
| **Platform Core (T01)** | `SP-38` | **Velocity (Story Points)** | **202 pts** | **202 pts** | 0 | **VERIFIED (100% MATCH)** |
| **Platform Core (T01)** | `SP-38` | **Average Cycle Time** | **5.00 days** | **5.00 days** | 0.00 | **VERIFIED (100% MATCH)** |
| **Platform Core (T01)** | `SP-38` | **On-Time Delivery Rate** | **91.23%** (52/57) | **91.23%** | 0.00% | **VERIFIED (100% MATCH)** |
| **Platform Core (T01)** | `SP-38` | Task Completion Rate | **90.48%** (57/63) | **90.48%** | 0.00% | **VERIFIED (100% MATCH)** |
| **Platform Core (T01)** | `SP-38` | Blocked Tasks | 2 | 2 | 0 | **VERIFIED (100% MATCH)** |
| **Platform Core (T01)** | `SP-38` | Reopened Tasks | 2 (3 events) | 2 (3 events) | 0 | **VERIFIED (100% MATCH)** |
| **QA Automation (T04)** | `SP-38` | Total Tasks | 66 | 66 | 0 | **VERIFIED (100% MATCH)** |
| **QA Automation (T04)** | `SP-38` | Cancelled Tasks | 1 | 1 | 0 | **VERIFIED (100% MATCH)** |
| **QA Automation (T04)** | `SP-38` | Planned Tasks | 65 | 65 | 0 | **VERIFIED (100% MATCH)** |
| **QA Automation (T04)** | `SP-38` | Completed Tasks (Done) | 59 | 59 | 0 | **VERIFIED (100% MATCH)** |
| **QA Automation (T04)** | `SP-38` | **Velocity (Story Points)** | **227 pts** | **227 pts** | 0 | **VERIFIED (100% MATCH)** |
| **QA Automation (T04)** | `SP-38` | **Average Cycle Time** | **4.51 days** | **4.51 days** | 0.00 | **VERIFIED (100% MATCH)** |
| **QA Automation (T04)** | `SP-38` | **On-Time Delivery Rate** | **94.92%** (56/59) | **94.92%** | 0.00% | **VERIFIED (100% MATCH)** |
| **QA Automation (T04)** | `SP-38` | Task Completion Rate | **90.77%** (59/65) | **90.77%** | 0.00% | **VERIFIED (100% MATCH)** |
| **QA Automation (T04)** | `SP-38` | Blocked Tasks | 2 | 2 | 0 | **VERIFIED (100% MATCH)** |
| **QA Automation (T04)** | `SP-38` | Reopened Tasks | 0 | 0 | 0 | **VERIFIED (100% MATCH)** |

---

## 4. Verification Conclusion

Every metric calculated manually from underlying task row records matches the SQL metric definitions with zero error (discrepancy = 0). The business logic correctly isolates completed deliverables and excludes de-scoped cancelled tasks from denominator metrics.

