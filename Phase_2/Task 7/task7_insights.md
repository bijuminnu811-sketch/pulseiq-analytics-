# Task 7: Attrition Analytics

**Page file:** `pages/4_Attrition_Analytics.py`  
**Data used:** `warehouse.fact_headcount_monthly`, `warehouse.fact_attrition_risk`, `warehouse.dim_employee`, `warehouse.dim_department`  
**Metric views:** `metrics.m03_exits`, `metrics.m04_attrition_rate_monthly`, `metrics.m27_high_risk_share`  
**Period analyzed:** 2020-01 to 2026-09 (Full historical) and 2025-04 to 2026-09 (Primary analysis window)

---

## 1. What I Built

- **Historical Exits & Attrition Rate Dashboard:** Stacked monthly exit volume distinguishing voluntary resignations (`Resigned`) from involuntary departures (`Terminated` and `Contract Ended`), combined with an overlay of monthly attrition percentage ($M04$).
- **Department Separation Analysis:** Horizontal breakdown ranking departments by total exits and voluntary separation ratio.
- **Tenure at Exit Analysis:** Grouped bar chart and statistics showing employee service length at departure across 5 brackets (`< 1 Year`, `1–2 Years`, `2–3 Years`, `3–5 Years`, and `5+ Years`).
- **Dedicated 'Predicted, not certain' Risk Feed:** An isolated, distinct section clearly highlighting machine learning 12-month attrition risk bands (`High`, `Medium`, `Low`).
- **Strict Privacy Masking (k-Anonymity):** An automated privacy rule that masks risk scores for any cohort with fewer than 10 employees to prevent re-identification.
- **Interactive Department and Date Controls:** Filterable by single department or consolidated company-wide total, with configurable analysis windows.

---

## 2. Screenshots

![Exit trends and tenure](screenshots/task7_exits_tenure.png)

![Predicted risk and privacy ledger](screenshots/task7_predicted_risk.png)

---

## 3. The 3 Biggest Findings with Numbers

1. **Voluntary Resignation Dominance (87.8% of Exits):**  
   Out of 304 recorded departures across the company's operating history, **267 exits (87.8%) were voluntary resignations**, while involuntary terminations accounted for only 24 (7.9%) and end-of-contracts accounted for 13 (4.3%). Attrition at GrowMar is overwhelmingly employee-initiated rather than driven by involuntary separations.

2. **Severe Risk Concentration in Customer Support (34.5% High Risk):**  
   In the predictive attrition feed (`fact_attrition_risk`), **Customer Support (D06)** exhibits the highest flight vulnerability by a wide margin. **34.5% of its workforce (20 out of 58 scored employees)** are classified in the High-Risk band with an average risk score of **23.56%** (nearly triple the company baseline of 8.9%). By contrast, Product & Design (D02), Finance (D08), and Legal (D10) have 0 employees in the High-Risk category.

3. **Critical 1-to-3 Year Retention Window (Average Voluntary Tenure 2.73 Years):**  
   Tenure analysis reveals that the primary resignation window occurs between **1 and 3 years of service**, with average voluntary exit tenure standing at **2.73 years** (median 2.4 years). Departures drop significantly once employees pass 3 years (representing only 24.3% of total exits), demonstrating that retention efforts must focus heavily on the 12-to-36 month onboarding and career progression milestone.

---

## 4. Think for Yourself: A department has only 4 people. What do you show, and why?

### What I Show:
I show the cohort size (e.g., `Cohort Size: 4 employees`) and an explicit privacy label:  
`🔒 [Privacy Protected: Group Size < 10]`.  
I suppress the high-risk count, high-risk percentage, and average risk score.

### Why:
When a team has only 4 members, reporting that *"1 employee is High Risk"* or showing an elevated average risk score allows team members or managers to deduce who the flagged individual is through simple process of elimination (e.g., who recently missed a promotion, expressed frustration, or had attendance fluctuations).

In enterprise analytics:
- Predictive risk scores are probabilistic advisory signals meant to guide supportive conversations, workload balancing, and career reviews—**never a certainty, performance verdict, or dismissal list**.
- Showing individual predictions or micro-cohort statistics destroys psychological safety and violates privacy regulations (such as GDPR principle of data minimization and protection against automated profiling).
- Enforcing **$k$-anonymity ($k \ge 10$)** ensures analytical utility while strictly safeguarding individual employee privacy.

---

## 5. Completion Checklist

- [x] **Numbers match metric views:** Exits match `metrics.m03_exits` (304 exits), attrition rates match `metrics.m04_attrition_rate_monthly`, and risk cohorts match `metrics.m27_high_risk_share`.
- [x] **Predictions are visibly labelled:** Clear section titled **'🔮 Predicted, not certain: 12-Month Attrition Risk Feed'** with advisory explanation.
- [x] **No individual is identifiable:** All risk data aggregated at department cohort level; no individual names or employee IDs are exposed. Minimum group size threshold ($k \ge 10$) is enforced.
- [x] **3 findings written with verified numbers:** Resignation dominance (87.8%), Support team concentration (34.5%), and 1–3 year tenure milestone (2.73 years).
- [x] **Department filter tested:** Supports interactive switching across departments and company-wide views.

---

## 6. Reference Links (GitHub)

- [Streamlit](https://github.com/streamlit/streamlit) · https://github.com/streamlit/streamlit
- [lifelines (survival analysis)](https://github.com/CamDavidsonPilon/lifelines) · https://github.com/CamDavidsonPilon/lifelines
- [Plotly](https://github.com/plotly/plotly.py) · https://github.com/plotly/plotly.py

---

## 7. How Real Companies Do It

Predictive risk is advice for a conversation, not a decision about a person. High-performing People Analytics teams use risk scores to trigger retention budgets, conduct stay interviews, and address systemic burnout—never to target or label individual employees.

---

## 8. Link to the Next Task

I can now describe who leaves, why they leave, and where future risk lies. **Task 8** shifts focus to how teams deliver work across sprints: velocity, cycle time, and on-time delivery across 16 teams and 38 sprints.

*I built an attrition view that is useful, verified against data, and respects employee privacy.*

