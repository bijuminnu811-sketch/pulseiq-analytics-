# Task 17: Live Streamlit Dashboard Deployment & Production Readiness

**Author:** Minnu Biju  
**Project:** PulseIQ Workforce Analytics  
**Phase:** 4 — Release (Task 17)  
**Live URL:** `https://pulseiq-analytics.streamlit.app`  
**GitHub Repository:** [https://github.com/bijuminnu811-sketch/pulseiq-analytics-.git](https://github.com/bijuminnu811-sketch/pulseiq-analytics-.git)  
**Main Entry Point:** `app.py`  
**Execution Date:** November 2026  

---

## 1. Hosting Architecture Evaluation

To host the PulseIQ analytics suite for enterprise executives and HR leaders, three deployment patterns were evaluated:

| Hosting Option | Architecture | DuckDB Compatibility | Setup Complexity | Monthly Cost | Recommendation Status |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Streamlit Community Cloud** | Serverless Linux containers connected directly to GitHub repository (`main` branch). | **Native & Optimal** (reads local `pulseiq.duckdb` directly with zero network latency). | **Zero-Config** (continuous deployment triggered automatically on `git push`). | **Free Tier** | **FIRST CHOICE (Recommended)** |
| **AWS ECS / Google Cloud Run** | Docker container packaging Python 3.13, Streamlit, and DuckDB behind Application Load Balancer. | High (requires persistent EBS/EFS volume or cloud bucket sync). | High (requires Dockerfile, Terraform/CloudFormation, CI/CD pipelines, IAM roles). | \$25 - \$65 / month | Alternative for Enterprise VPC / Corporate SSO |
| **Hugging Face Spaces** | Git-based Docker/Streamlit spaces. | Moderate (storage quotas and public visibility constraints). | Moderate | Free / \$9 | Backup / Secondary Demo |

### Why Streamlit Community Cloud is the First Choice:
1. **Zero Cold-Start Lag for DuckDB:** Because `pulseiq.duckdb` (32.5 MB) is packaged directly within the repository (well below Streamlit Cloud's 100 MB Git file limit), queries run directly in-process via C++ DuckDB bindings without external database connection latency.
2. **Instant Continuous Deployment:** Any commit or tag pushed to `main` automatically triggers a zero-downtime container rebuild and hot-reloads the production app.
3. **Automated SSL/TLS:** Every deployment receives an official `https://*.streamlit.app` domain with managed HTTPS certificates out of the box.
4. **Responsive Web & Mobile Layout:** Modern Streamlit 1.66+ renders seamlessly across desktop, tablet, and mobile browsers with custom CSS media queries.

---

## 2. Production Database & Storage Strategy

- **Database Engine:** DuckDB 2.0.0
- **Database File:** `pulseiq.duckdb` (32.5 MB)
- **Concurrence & Safety:** All Streamlit pages access DuckDB via `@st.cache_resource` in **`read_only=True`** mode:
  ```python
  @st.cache_resource
  def get_connection():
      return duckdb.connect("pulseiq.duckdb", read_only=True)
  ```
  This prevents database file locking across concurrent user sessions and avoids transient WAL/journal corruption.
- **Data Freshness / Cut-off Date:** September 30, 2026 23:59:59 UTC.
- **Zero Raw Table Access:** All 12 pages and the landing app strictly query certified Gold-level metric views (`metrics.*`) or conformed warehouse dimensions (`warehouse.*`).

---

## 3. Secret Management & Security Isolation

- **Zero Plaintext Secrets:** No credentials, API tokens, passwords, or cloud keys are stored anywhere in the codebase.
- **Secret Architecture:** For external integrations (e.g. enterprise LDAP, email alerts, or webhook callbacks), the application utilizes Streamlit's built-in platform secret manager:
  - **Local Development:** `.streamlit/secrets.toml` (ignored by `.gitignore`).
  - **Streamlit Community Cloud:** Managed encrypted environment variables configured directly in the Streamlit Cloud Dashboard under **App Settings > Secrets**.

---

## 4. User Experience & Mobile Responsiveness

### A. New User Experience & Navigation
When a new executive or auditor lands on `app.py`:
1. **Welcome Banner:** Displays clear branding ("PulseIQ Governed Analytics • Production Live Suite"), official data cut-off date (`September 30, 2026`), and certification status.
2. **Executive Navigation:** Sidebar features an interactive "🧭 Portal Navigation" dropdown guiding users to all 12 analytical pages:
   - Data Quality Gatekeeper (Task 3)
   - Governed Metric Catalog (Task 4)
   - Attendance & Leave Trends (Task 6)
   - Attrition Analytics & Risk (Task 7)
   - Team Productivity (Task 8)
   - Payroll Cost & Reconciliations (Task 9)
   - Budget vs Actual Variance (Task 10)
   - Profit & Loss Analytics (Task 11)
   - Invoices, Receivables & Cash Flow (Task 12)
   - Cross-Department Impact (Task 13)
   - AI Signals Dashboard (Task 14)
   - Executive Health Scorecard (Task 15)
3. **Interactive Governance Filters:** Multi-select department filter and calendar date range with real-time reactive KPI calculation.

### B. Mobile & Phone-Sized Viewport Testing
The dashboard was tested against standard mobile viewports (375x667 px iPhone SE, 390x844 px iPhone 14/15, and 412x915 px Samsung Galaxy):
- Custom CSS media queries (`@media (max-width: 768px)`) ensure KPI cards stack vertically into a single column.
- Header font scales down from 28px to 20px to prevent awkward line wrapping.
- Plotly chart axes automatically switch to compact numeric formatting with touch-friendly tap targets.
- **Evidence Screenshot:** `Phase_4/Task17_Live_Streamlit/Task17_Mobile_Dashboard_View.png` captures the exact mobile layout rendering.

---

## 5. Automated Data Refresh Schedule

In production, company records are refreshed on a structured cadence:

```
+-----------------------------------------------------------------------------------------+
|                               BATCH REFRESH WORKFLOW                                    |
+-----------------------------------------------------------------------------------------+
|  Cron Schedule:  0 2 1 * *  (Monthly on the 1st at 02:00 UTC)                           |
|                                                                                         |
|  1. INGESTION:      python etl.py                                                       |
|                     Validates 29 CSV contracts; routes defects to quarantine.           |
|                                                                                         |
|  2. WAREHOUSE:      python warehouse.py                                                 |
|                     Builds conformed SCD Type 2 dimensions and surrogate key facts.     |
|                                                                                         |
|  3. AUDIT & DQ:     python dq_gatekeeper.py                                             |
|                     Executes 14 automated DQ tests. Halts on critical failures.         |
|                                                                                         |
|  4. METRICS:        python metric_layer.py                                              |
|                     Compiles 28 governed SQL metric views under 'metrics.*'.            |
|                                                                                         |
|  5. REPORT BUILD:   python build_report.py --month <YYYY-MM>                            |
|                     Generates executive monthly PDF & Markdown packs.                   |
|                                                                                         |
|  6. DEPLOYMENT:     git commit & push to GitHub origin/main                             |
|                     Streamlit Community Cloud automatically reloads latest record.      |
+-----------------------------------------------------------------------------------------+
```

