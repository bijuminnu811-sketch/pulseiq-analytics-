# PulseIQ Executive Board Presentation (Board Pack)

**Organization:** Zenith Nova Technologies  
**Audience:** Board of Directors  
**Author:** Minnu Biju (Data Analytics Track)  
**Release Tag:** `v1.0.0`  
**Data Cut-off Date:** September 30, 2026  

---

## Slide 1: Workforce Expansion & Retention Stability
- **Empirical Finding:** Active headcount grew +5.0% YoY reaching 441 employees. Monthly attrition settled at a healthy 0.68% (annualized 8.16%), below the board's 12.0% ceiling.
- **Supporting Evidence:** 441 active staff (M01), 23 hires, 3 exits, 95.19% attendance rate (M13). Distributed Tier 2/3 hubs account for 34.2% of workforce.
- **Business Interpretation:** The business has matured beyond early-stage turnover volatility into predictable headcount scaling (+2.3 net additions/month).
- **Recommendation:** Maintain current hiring pace; preserve Tier 2/3 expansion to hedge metropolitan salary inflation.

---

## Slide 2: Payroll Capital Allocation & Overtime Exposure
- **Empirical Finding:** Monthly employer payroll cost totaled INR 55.52M (INR 125.9K per head). Engineering (D01) represents 42.1% of company payroll (INR 23.36M).
- **Operational Risk:** Customer Support experienced a 3.4% overtime cost surge (INR 286K), driven by post-release shift triage.
- **Business Interpretation:** R&D capital allocation reflects strategic market focus. Support overtime indicates release instability.
- **Recommendation:** Mandate automated regression testing in Engineering sprint exit gates to eliminate post-release Support shift overtime.

---

## Slide 3: Liquidity, Invoicing & Receivables Aging Drag
- **Empirical Finding:** Recognized revenue reached INR 98.97M with net operating profit of INR 18.06M (18.25% operating margin).
- **Working Capital Concern:** Days Sales Outstanding (DSO) averaged 58.4 days. Overdue balances past Net 30 total INR 14.2M (22.0% of receivables), concentrated in 3 enterprise accounts.
- **Business Interpretation:** Topline profitability is robust, but commercial liquidity is hindered by enterprise milestone sign-off delays.
- **Recommendation:** Enforce a 1.5% late payment interest policy; transition accounts past 45 days to bi-weekly advance retainers.

---

## Slide 4: Sprint Throughput & Engineering Delivery Discipline
- **Empirical Finding:** Engineering squads achieved an 89.3% sprint on-time delivery rate (M23) with an average cycle time of 3.8 days (M25).
- **Throughput Evidence:** QA Automation (T04) peaked at 227 completed story points in SP-38 during multi-platform integration testing.
- **Business Interpretation:** Development cadence is reliable. The team exhibits low rework rates (3.1%) and strong sprint predictability.
- **Recommendation:** Protect sprint focus by capping mid-sprint unplanned requirements to under 10% of committed capacity.

---

## Slide 5: Cross-Domain Impact — Overtime Burnout Drives Churn Risk
- **Empirical Finding:** Staff logging >15 hours of monthly overtime are 3.2x more likely to be classified in the High Attrition Risk cohort (M27).
- **Supporting Evidence:** Cross-department correlation between attendance hours and AI flight risk flags across 430 scored employees.
- **Business Interpretation:** Flight risk is driven by operational burnout rather than base salary dissatisfaction.
- **Recommendation:** Institute automated HR burnout alerts when overtime exceeds 10h for two consecutive pay cycles; mandate compensatory rest.

---

## Slide 6: Analytical Integrity — Data Quality Gatekeeper Proof
- **Empirical Proof:** 14 automated SQL audit gates, 100% row count reconciliation across 12 fact tables, zero unexpected orphan keys.
- **Test Harness:** Proved with 7 deliberately injected corrupt rows (unbalanced journals, duplicate wages, orphan entities) all intercepted.
- **Privacy Shield:** Strict dynamic masking for small cohorts (<10 / <5) automatically suppresses deanonymization vectors.

---

## Slide 7: Strategic Data Discipline — What NOT to Recommend!
- **Core Governance Question:** Which recommendation should NOT be given because the available data is too weak to support it?
- **POLICY DECISION:** Do NOT recommend cutting sales/marketing headcount or attributing churn to specific managers.
- **Analytical Justification:**
  1. The dataset does NOT contain customer acquisition cost (CAC), lead conversion funnels, or marketing attribution.
  2. The dataset does NOT contain exit interview transcripts or manager 360-degree performance reviews.
- **Alternative:** Commission a formal Employee Sentiment Survey and integrate CRM pipeline feeds before adjusting commercial headcount.

---

## Slide 8: Strategic Roadmap & Capital Allocation Recommendations
1. **Overtime Burnout Capping:** Target < 2.0% overtime in Support; saves INR 2.4M annually.
2. **Receivables Clawback:** Target DSO < 50 days; unlocks INR 8.5M in immediate cash flow.
3. **Tier 2/3 Regional Hubs:** Expand regional share to 40% for 18% structural cost arbitrage.
4. **FastAPI ERP Integration:** Real-time automated payroll sync eliminates manual spreadsheet handoffs.

---

## Slide 9: Project Handover & Production Release Verification
- **Release Version:** `v1.0.0` (Git Tagged & Pushed)
- **Author:** Minnu Biju (Data Analytics Track)
- **GitHub Repository:** [bijuminnu811-sketch/pulseiq-analytics-](https://github.com/bijuminnu811-sketch/pulseiq-analytics-)
- **Live Application:** [https://pulseiq-analytics.streamlit.app](https://pulseiq-analytics.streamlit.app)