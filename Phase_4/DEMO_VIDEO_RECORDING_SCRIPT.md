# PulseIQ 5-Minute Demo Video Recording Script & Guide

**Candidate Name:** Minnu Biju  
**Project:** Aura Workforce by Growmar • PulseIQ Analytics  
**Track:** Data Analytics Track  
**Live URL to Open:** `https://pulseiq-analytics.streamlit.app`  
**GitHub Repository:** `https://github.com/bijuminnu811-sketch/pulseiq-analytics-`  

---

## 🎬 Video Recording Instructions (Read First)
- **Total Duration:** Exactly **5 minutes** (0:00 to 5:00).
- **Tool to Use:** Loom, OBS Studio, or Windows Game Bar (`Win + Alt + R`).
- **Privacy Setting:** Upload to YouTube as **Unlisted** (or Google Drive as "Anyone with link can view").
- **Verification:** Open the link in a Private/Incognito browser window before submitting to verify it plays without logging in.

---

## ⏱️ Second-by-Second Video Script

### Part 1: Face on Camera (0:00 to 1:00)
> **Setup:** Webcam showing your face clearly. Look directly at the camera. Do NOT read from a paper like a robot; speak naturally in your own words.

**What to Say:**
> *"Hi everyone, my name is **Minnu Biju**, and this is my final presentation for the **Data Analytics Track** on the **PulseIQ Enterprise Analytics Platform**.*
>
> *In fast-growing technology companies like Zenith Nova, business data is often fragmented across departmental silos: HR tracks headcount in spreadsheets, Finance maintains payroll and invoices in ERP ledgers, and Engineering tracks delivery in project boards. This causes constant reconciliation discrepancies, delayed visibility into turnover, and unmanaged overtime burnout.*
>
> *Over the past 20 days, I engineered an end-to-end governed analytics solution on DuckDB and Streamlit. It connects 29 raw source feeds into a validated star-schema warehouse, protected by 14 automated data quality gates, 28 governed metric views with privacy protection, and a live executive cloud portal.*
>
> *Let me share my screen and show you the live product in action."*

---

### Part 2: Live Screen Walkthrough (1:00 to 4:00)
> **Setup:** Share your full screen. Make sure the address bar is visible showing `https://pulseiq-analytics.streamlit.app` (not localhost!).

#### Minute 1:00 – 2:00 | Landing Page & Workforce Dynamics
- **Action:** Open `https://pulseiq-analytics.streamlit.app`.
- **What to Say:**
  > *"Here is our live dashboard deployed on Streamlit Cloud. Right at the top, you can see our verified Data Cut-off date of September 30, 2026.*
  >
  > *Looking at our executive KPI cards: Active headcount expanded to **441 employees**, up 5% annualized. Our monthly attrition rate is healthy at **0.68%**, and attendance stands at **95.19%**.*
  >
  > *If we look at our geographical mix, **34.2% of our workforce** is now stationed in Tier 2 and Tier 3 engineering hubs like Coimbatore and Kochi, providing roughly 18% cost-arbitrage savings."*

#### Minute 2:00 – 3:00 | The Business Story (Overtime vs Churn Risk)
- **Action:** In the left sidebar, click on **`10. Cross Department Impact`** or **`11. AI Signals Dashboard`**.
- **What to Say:**
  > *"Now, let's explore our core cross-department finding: the link between overtime and employee flight risk.*
  >
  > *When we look at Customer Support and Platform Core, overtime surged to 3.4% of payroll. By joining attendance hours with our machine-learning churn risk scores, our data revealed that employees logging **over 15 hours of monthly overtime are 3.2 times more likely to be in the High Attrition Risk cohort**.*
  >
  > *This proves that flight risk at Zenith Nova is driven by operational burnout and release instability rather than compensation dissatisfaction. My recommendation to the board is to mandate regression test automation in Engineering sprint gates to eliminate post-release support triage."*

#### Minute 3:00 – 4:00 | Self-Service KPI Explorer & Privacy Guardrail
- **Action:** In the sidebar, click on **`13. KPI Explorer`**.
- **What to Say:**
  > *"Next, I built a Self-Service KPI Explorer with dynamic Role-Based Access Control.*
  >
  > *One major risk in analytics is small-group disclosure: if an executive queries average salary or flight risk for a micro-team of 1 or 2 people, the individual's private data is revealed.*
  >
  > *Notice that when I simulate our CEO, Tejas Chowdhury, in the Executive Office (Department D00 with only 1 person), the system actively intercepts the query and masks the value with `[SUPPRESSED: Size 1 < 5]`. This mathematical shield prevents deanonymization at the database layer."*

---

### Part 3: Proof & Conclusion (4:00 to 5:00)
- **Action:** In the sidebar, click on **`1. Data Quality Gatekeeper`** or open terminal running `python pulseiq_doctor.py`.
- **What to Say:**
  > *"Finally, here is our data quality proof. Our automated Data Quality Gatekeeper runs 14 SQL audit checks across the warehouse on every ingestion batch. We verified that our double-entry ledger is balanced to zero, all 12 fact tables match clean rows with 100% parity, and our gatekeeper test harness caught 100% of deliberately injected corrupt rows.*
  >
  > *To wrap up: this project taught me that data analytics is not just building pretty charts — it is about establishing single-source-of-truth governance, respecting employee privacy, and having the discipline to know what recommendations to give and what not to give.*
  >
  > *Thank you!"*

---

## 📋 Final Submission Checklist

| Deliverable | Where to Submit | Format |
| :--- | :--- | :--- |
| **Phase 4 Report** | Programme Site Form | `DataAnalytics_MinnuBiju_Phase4_Report.pdf` (3 pages) |
| **Consolidated Report** | Google Form | `DataAnalytics_MinnuBiju_Consolidated_Report.pdf` (10 pages) |
| **Live Dashboard Link** | Google Form | `https://pulseiq-analytics.streamlit.app` |
| **Demo Video Link** | Google Form | Your unlisted YouTube or Drive link |
| **Git Tags** | GitHub Remote | `phase-1`, `phase-2`, `phase-4`, `v1.0.0-rc1`, `v1.0.0` |
