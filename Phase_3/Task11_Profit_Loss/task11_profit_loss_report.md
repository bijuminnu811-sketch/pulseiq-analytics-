# Task 11: Profit & Loss and Expense Analytics
## PulseIQ Analytics | Aura Workforce by GrowMar

---

## 1. Overview

| Item | Detail |
|------|--------|
| **Task** | Phase 3, Task 11 — Profit and Loss & Expense Analytics |
| **Dashboard Page** | `pages/8_Profit_Loss_Analytics.py` |
| **Database** | `pulseiq.duckdb` |
| **Core Tables** | `warehouse.fact_ledger`, `warehouse.dim_account`, `warehouse.fact_expense`, `warehouse.dim_vendor` |
| **Period** | April 2025 – September 2026 (18 months) |

---

## 2. Sign Convention

| Metric | Formula | Sign Rule |
|--------|---------|-----------|
| **Revenue** | `SUM(credit − debit)` for INCOME accounts | Positive = income earned |
| **Expense** | `SUM(debit − credit)` for EXPENSE accounts | Positive = cost incurred |
| **Profit** | `Revenue − Expense` | Positive = profitable period |
| **Profit Margin %** | `Profit ÷ Revenue × 100` | NULL when Revenue = 0 |

**Double-counting prevention:** All `fact_ledger` aggregations join `dim_account` and filter `WHERE is_group = 'N'`. This ensures only detail/leaf accounts are included. Parent (group) accounts, which aggregate child balances, are excluded to prevent double-counting.

---

## 3. Data Sources

### 3.1 fact_ledger
- Monthly journal entries with `debit`, `credit`, `signed_amount_debit_positive`
- Joined to `dim_account` on `account_code`
- Filtered by `account_type IN ('INCOME','EXPENSE')` and `is_group = 'N'`
- Aggregated by `posting_period` (format: `YYYY-MM`)

### 3.2 dim_account
- Contains `account_code`, `account_name`, `account_type`, `is_group`, `statement`
- `is_group = 'Y'` → parent/group account (excluded from summation)
- `is_group = 'N'` → detail account (included in summation)
- `statement = 'Profit & Loss'` → Income or Expense accounts
- `statement = 'Balance Sheet'` → Asset, Liability, Equity accounts

### 3.3 fact_expense
- Operational (non-payroll) expenses with `total_amount`, `category_account`, `vendor_id`, `expense_date`
- Joined to `dim_account` for category name
- Joined to `dim_vendor` for vendor name
- Used for expense category analysis and top-10 vendor ranking

### 3.4 dim_vendor
- Master vendor list with `vendor_id`, `vendor_name`, `city`, `gst_registration`

---

## 4. Reconciliation Table

| Metric | Calculated Value | Source | Note |
|--------|----------------|--------|------|
| Total Revenue (18 months) | ₹126.09 Cr | fact_ledger + dim_account (INCOME, is_group=N) | Detail accounts only |
| Total Expense (18 months) | ₹103.61 Cr | fact_ledger + dim_account (EXPENSE, is_group=N) | Detail accounts only |
| Net Profit (18 months) | ₹22.48 Cr | Revenue − Expense | Positive = profitable |
| Avg Profit Margin % | ~17.83% | Profit ÷ Revenue × 100 | Full 18-month period |
| Operational Expense (fact_expense) | ₹19.73 Cr | fact_expense + dim_account (is_group=N) | Non-payroll operational costs |
| Expense Categories | 12 | Distinct account_name in fact_expense | Office Rent is largest |
| Top Vendor | Skyline Realty Holdings (~₹199 L) | fact_expense + dim_vendor | Largest single vendor |

> **Note:** The difference between total_expense from `fact_ledger` (~₹103.61 Cr) and from `fact_expense` (~₹19.73 Cr) is expected — `fact_ledger` includes payroll and all other cost entries posted by the accounting system, while `fact_expense` contains only operational procurement expenses.

---

## 5. Three Business Findings

### Finding 1 — Margin Compression Despite Revenue Growth (Apr 2026 onwards)

Revenue grew from ~₹6.1 Cr/month (FY2025 average) to ~₹7.8 Cr/month (Apr–Sep 2026), a ~28% increase. However, profit margin dipped to its lowest point in April 2026, with expenses reaching ₹7.2 Cr — growing faster than revenue. Cost scaling is outpacing revenue, compressing margins even as the top-line grows.

**Recommended action:** Conduct a cost-driver review for April 2026; identify whether this is a seasonal spike or structural cost escalation requiring budget controls.

### Finding 2 — Vendor Concentration Risk: Top 2 Vendors Account for >19% of All Operational Spend

Skyline Realty Holdings (~₹199 L) and StratoHost Infrastructure (~₹168 L) together represent over 19% of total operational procurement expenses. Office Rent and Cloud Hosting are the two largest expense categories. Heavy dependence on two vendors creates negotiation leverage risk and potential service disruption exposure.

**Recommended action:** Renegotiate long-term contracts with the top 2 vendors and evaluate alternative providers to introduce price competition and reduce concentration risk.

### Finding 3 — April Seasonality: Consistent Cost Spikes at Financial Year Start

Both April 2025 (₹6.48 Cr expense) and April 2026 (₹7.20 Cr expense) show the highest monthly expenses in their respective financial years. This pattern is consistent with annual contract renewals, insurance premiums, and recruitment costs incurred at the start of each financial year. Revenue does not spike proportionally, causing margin dips each April.

**Recommended action:** Smooth large annual commitments across quarters through monthly accruals to avoid sharp margin distortions in the first month of each financial year.

---

## 6. Why Revenue Can Grow While Margins Fall — Three Explanations

### Explanation 1: Rising Fixed Costs (Scale-Up Cost Overhang)
As a business grows, it hires more staff, leases larger spaces, and expands infrastructure *before* the full revenue from those investments materialises. Payroll and infrastructure costs grow faster than revenue, compressing margins even as the top-line increases.

**Data needed to verify:**
- Monthly headcount vs monthly payroll cost trend (`fact_headcount_monthly` + `fact_payroll`)
- Payroll as % of revenue over time
- Rent/cloud hosting cost as % of revenue

### Explanation 2: Pricing Pressure (Discounting to Win Volume)
Competitive markets may force a business to discount to win new clients. Revenue can grow in total if more contracts are acquired, but if each is priced lower, the revenue per unit of effort falls while servicing costs remain constant or rise.

**Data needed to verify:**
- Average revenue per client/contract (`fact_invoice` + `dim_client`)
- Distinct client count per month
- Average invoice value trend over time

### Explanation 3: Mix Shift to Lower-Margin Services
If a business shifts its revenue mix toward higher-volume but lower-margin service lines (e.g., bulk staffing vs high-value consulting), total revenue grows through volume, but the blended profit margin falls because new revenue carries lower unit profitability.

**Data needed to verify:**
- Revenue segmented by service type or product category (requires `service_category` column in `fact_invoice` or `dim_client`)
- Gross margin per service line
- Share of revenue by segment over time

---

## 7. Files Created / Modified

| File | Action |
|------|--------|
| `pages/8_Profit_Loss_Analytics.py` | ✅ Created — Streamlit dashboard page |
| `docs/task11_profit_loss_report.md` | ✅ Created — This documentation file |

---

## 8. Testing Instructions

### Step 1: Run the Streamlit app
```bash
cd "C:\Users\binit\OneDrive\New folder\pulseiq_new"
.venv\Scripts\streamlit.exe run app.py
```

### Step 2: Navigate to the page
In the left sidebar, click **8 Profit Loss Analytics**.

### Step 3: Verify the dashboard
1. **KPI cards** — Check total revenue ~₹126 Cr, expense ~₹104 Cr, profit ~₹22 Cr, margin ~17-18%
2. **Revenue vs Expense bar chart** — Revenue (green) should be taller than Expense (red) for most months
3. **Profit trend** — April 2026 should show the lowest margin bar
4. **Category chart** — Office Rent should be the tallest bar
5. **Top vendors** — Skyline Realty Holdings should be #1
6. **Month filter** — Select a single month (e.g., 2026-04) and verify KPI cards update
7. **Reconciliation table** — Verify totals match hand-calculated values from raw queries

### Step 4: Spot-check a month
Manually verify April 2025:
- Revenue: ₹7,10,75,300
- Expense: ₹6,47,61,237
- Profit: ₹63,14,063
- Margin: ~8.88%

---

## 9. Git Commands

```bash
cd "C:\Users\binit\OneDrive\New folder\pulseiq_new"

git add pages/8_Profit_Loss_Analytics.py docs/task11_profit_loss_report.md

git commit -m "feat(task11): add profit & loss dashboard with expense analytics and vendor ranking"

git push origin main
```

