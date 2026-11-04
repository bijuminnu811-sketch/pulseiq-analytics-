"""
Task 11: Profit & Loss and Expense Analytics Dashboard
=======================================================
Page: 8_Profit_Loss_Analytics.py
Database: pulseiq.duckdb
Schema: warehouse
Sources: fact_ledger, dim_account, fact_expense, dim_vendor

Sign Convention:
  Revenue  = SUM(credit - debit) for INCOME accounts  (credit-normal)
  Expense  = SUM(debit - credit)  for EXPENSE accounts (debit-normal)
  Profit   = Revenue - Expense
  Margin % = Profit / Revenue * 100   (NULL if Revenue = 0)

Double-counting prevention:
  All fact_ledger joins filter dim_account WHERE is_group = 'N' (detail accounts only).
"""

import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ─── Config ───────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "pulseiq.duckdb")

st.set_page_config(
    page_title="Profit & Loss Analytics | PulseIQ",
    page_icon="💹",
    layout="wide",
)

# ─── Helpers ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_monthly_pnl() -> pd.DataFrame:
    """Monthly Revenue, Expense, Profit and Margin from fact_ledger."""
    sql = """
    WITH revenue AS (
        SELECT
            fl.posting_period,
            ROUND(SUM(fl.credit - fl.debit), 2) AS revenue
        FROM warehouse.fact_ledger fl
        JOIN warehouse.dim_account a ON fl.account_code = a.account_code
        WHERE a.is_group = 'N' AND a.account_type = 'INCOME'
        GROUP BY fl.posting_period
    ),
    expense AS (
        SELECT
            fl.posting_period,
            ROUND(SUM(fl.debit - fl.credit), 2) AS expense
        FROM warehouse.fact_ledger fl
        JOIN warehouse.dim_account a ON fl.account_code = a.account_code
        WHERE a.is_group = 'N' AND a.account_type = 'EXPENSE'
        GROUP BY fl.posting_period
    )
    SELECT
        COALESCE(r.posting_period, e.posting_period) AS month_period,
        COALESCE(r.revenue, 0)   AS revenue,
        COALESCE(e.expense, 0)   AS expense,
        ROUND(COALESCE(r.revenue, 0) - COALESCE(e.expense, 0), 2) AS profit,
        CASE
            WHEN COALESCE(r.revenue, 0) = 0 THEN NULL
            ELSE ROUND((COALESCE(r.revenue, 0) - COALESCE(e.expense, 0))
                       / COALESCE(r.revenue, 0) * 100, 2)
        END AS margin_pct
    FROM revenue r
    FULL OUTER JOIN expense e ON r.posting_period = e.posting_period
    ORDER BY month_period
    """
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute(sql).df()
    con.close()
    return df


@st.cache_data(ttl=300)
def get_expense_by_category() -> pd.DataFrame:
    """Expense totals grouped by account_name from fact_expense."""
    sql = """
    SELECT
        COALESCE(a.account_name, 'Unknown') AS category,
        ROUND(SUM(e.total_amount), 2) AS total_expense
    FROM warehouse.fact_expense e
    LEFT JOIN warehouse.dim_account a ON e.category_account = a.account_code
    WHERE a.is_group = 'N' OR a.is_group IS NULL
    GROUP BY category
    ORDER BY total_expense DESC
    """
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute(sql).df()
    con.close()
    return df


@st.cache_data(ttl=300)
def get_top_vendors(n: int = 10) -> pd.DataFrame:
    """Top N vendors by total_amount from fact_expense."""
    sql = f"""
    SELECT
        COALESCE(v.vendor_name, 'Unknown') AS vendor_name,
        ROUND(SUM(e.total_amount), 2) AS total_spent
    FROM warehouse.fact_expense e
    LEFT JOIN warehouse.dim_vendor v ON e.vendor_id = v.vendor_id
    GROUP BY vendor_name
    ORDER BY total_spent DESC
    LIMIT {n}
    """
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute(sql).df()
    con.close()
    return df


@st.cache_data(ttl=300)
def get_monthly_expense_category() -> pd.DataFrame:
    """Monthly expense by category for stacked chart."""
    sql = """
    SELECT
        strftime(e.expense_date, '%Y-%m') AS month_period,
        COALESCE(a.account_name, 'Unknown') AS category,
        ROUND(SUM(e.total_amount), 2) AS total_expense
    FROM warehouse.fact_expense e
    LEFT JOIN warehouse.dim_account a ON e.category_account = a.account_code
    WHERE a.is_group = 'N' OR a.is_group IS NULL
    GROUP BY month_period, category
    ORDER BY month_period, category
    """
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute(sql).df()
    con.close()
    return df


def fmt_cr(val: float) -> str:
    """Format as ₹X.XX Cr (Crores)."""
    return f"₹{val/1e7:,.2f} Cr"


def fmt_lakh(val: float) -> str:
    return f"₹{val/1e5:,.2f} L"


# ─── Page Header ──────────────────────────────────────────────────────────────
st.title("💹 Profit & Loss and Expense Analytics")
st.caption("Task 11 · Phase 3 · PulseIQ Analytics | Aura Workforce by GrowMar")

with st.expander("📐 Sign Convention & Methodology", expanded=False):
    st.markdown("""
| Item | Formula | Sign |
|------|---------|------|
| **Revenue** | SUM(credit − debit) for INCOME accounts | Positive = income earned |
| **Expense** | SUM(debit − credit) for EXPENSE accounts | Positive = cost incurred |
| **Profit** | Revenue − Expense | Positive = profitable period |
| **Profit Margin %** | Profit ÷ Revenue × 100 | Higher is better |

**Double-counting prevention:** All `fact_ledger` joins filter `dim_account` on `is_group = 'N'`  
(detail / leaf accounts only). Group/parent accounts are excluded from aggregation.

**Period:** April 2025 – September 2026 (18 months)
""")

# ─── Load Data ────────────────────────────────────────────────────────────────
df_pnl = get_monthly_pnl()
df_cat = get_expense_by_category()
df_vendors = get_top_vendors(10)
df_monthly_cat = get_monthly_expense_category()

# ─── Month Selector ───────────────────────────────────────────────────────────
all_months = sorted(df_pnl["month_period"].unique().tolist())
col_sel1, col_sel2 = st.columns([2, 1])
with col_sel1:
    selected_months = st.multiselect(
        "🗓️ Filter months (leave blank to show all)",
        options=all_months,
        default=[],
    )
with col_sel2:
    view_mode = st.radio("💰 Value scale", ["Crores (Cr)", "Lakhs (L)"], horizontal=True)

use_cr = view_mode.startswith("Crores")
scale = 1e7 if use_cr else 1e5
unit_lbl = "₹ Cr" if use_cr else "₹ L"

if selected_months:
    df_view = df_pnl[df_pnl["month_period"].isin(selected_months)].copy()
else:
    df_view = df_pnl.copy()

# ─── KPI Cards ───────────────────────────────────────────────────────────────
st.subheader("📊 Summary KPIs")
total_rev  = df_view["revenue"].sum()
total_exp  = df_view["expense"].sum()
total_prof = df_view["profit"].sum()
avg_margin = (total_prof / total_rev * 100) if total_rev > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue",  fmt_cr(total_rev)  if use_cr else fmt_lakh(total_rev))
k2.metric("Total Expense",  fmt_cr(total_exp)  if use_cr else fmt_lakh(total_exp))
k3.metric("Net Profit",     fmt_cr(total_prof) if use_cr else fmt_lakh(total_prof),
          delta=f"{avg_margin:.1f}% margin")
k4.metric("Avg Profit Margin", f"{avg_margin:.2f}%",
          delta="vs 0% breakeven")

st.divider()

# ─── Revenue vs Expense Bar Chart ─────────────────────────────────────────────
st.subheader("📈 Monthly Revenue vs Expense")

df_bar = df_view[["month_period", "revenue", "expense"]].copy()
df_bar["revenue_scaled"] = df_bar["revenue"] / scale
df_bar["expense_scaled"] = df_bar["expense"] / scale

fig_bar = go.Figure()
fig_bar.add_bar(x=df_bar["month_period"], y=df_bar["revenue_scaled"],
                name="Revenue", marker_color="#2ecc71")
fig_bar.add_bar(x=df_bar["month_period"], y=df_bar["expense_scaled"],
                name="Expense", marker_color="#e74c3c")
fig_bar.update_layout(
    barmode="group",
    xaxis_title="Month",
    yaxis_title=unit_lbl,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=380,
    margin=dict(l=40, r=20, t=20, b=40),
)
st.plotly_chart(fig_bar, use_container_width=True)

# ─── Profit & Margin Trend ────────────────────────────────────────────────────
st.subheader("📉 Profit & Margin Trend")

fig_trend = go.Figure()
fig_trend.add_bar(
    x=df_view["month_period"],
    y=(df_view["profit"] / scale).round(2),
    name="Profit",
    marker_color=["#2ecc71" if v >= 0 else "#e74c3c" for v in df_view["profit"]],
)
fig_trend.add_scatter(
    x=df_view["month_period"],
    y=df_view["margin_pct"],
    name="Margin %",
    mode="lines+markers",
    yaxis="y2",
    line=dict(color="#3498db", width=2),
    marker=dict(size=6),
)
fig_trend.update_layout(
    yaxis=dict(title=unit_lbl),
    yaxis2=dict(title="Margin %", overlaying="y", side="right", showgrid=False),
    xaxis_title="Month",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    height=380,
    margin=dict(l=40, r=60, t=20, b=40),
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ─── Expense by Category ──────────────────────────────────────────────────────
col_cat1, col_cat2 = st.columns([1, 1])

with col_cat1:
    st.subheader("🧾 Expense by Category")
    df_cat_disp = df_cat.copy()
    df_cat_disp["total_expense_scaled"] = df_cat_disp["total_expense"] / scale
    fig_cat = px.bar(
        df_cat_disp,
        x="total_expense_scaled",
        y="category",
        orientation="h",
        color="total_expense_scaled",
        color_continuous_scale="Reds",
        labels={"total_expense_scaled": unit_lbl, "category": "Category"},
        height=420,
    )
    fig_cat.update_coloraxes(showscale=False)
    fig_cat.update_layout(margin=dict(l=10, r=20, t=20, b=30), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_cat, use_container_width=True)

with col_cat2:
    st.subheader("🏷️ Category Share (Pie)")
    fig_pie = px.pie(
        df_cat_disp,
        names="category",
        values="total_expense",
        hole=0.4,
        height=420,
    )
    fig_pie.update_traces(textposition="outside", textinfo="label+percent")
    fig_pie.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=30))
    st.plotly_chart(fig_pie, use_container_width=True)

# ─── Stacked Monthly Expense by Category ──────────────────────────────────────
st.subheader("📦 Monthly Expense Breakdown by Category")
if selected_months:
    df_mc = df_monthly_cat[df_monthly_cat["month_period"].isin(selected_months)].copy()
else:
    df_mc = df_monthly_cat.copy()

df_mc["total_expense_scaled"] = df_mc["total_expense"] / scale
fig_stack = px.bar(
    df_mc,
    x="month_period",
    y="total_expense_scaled",
    color="category",
    barmode="stack",
    labels={"total_expense_scaled": unit_lbl, "month_period": "Month"},
    height=400,
)
fig_stack.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    margin=dict(l=40, r=20, t=40, b=40),
)
st.plotly_chart(fig_stack, use_container_width=True)

st.divider()

# ─── Top 10 Vendors ───────────────────────────────────────────────────────────
st.subheader("🏢 Top 10 Vendors by Spending")
df_v = df_vendors.copy()
df_v["total_spent_scaled"] = df_v["total_spent"] / scale

fig_vendor = px.bar(
    df_v,
    x="total_spent_scaled",
    y="vendor_name",
    orientation="h",
    color="total_spent_scaled",
    color_continuous_scale="Blues",
    labels={"total_spent_scaled": unit_lbl, "vendor_name": "Vendor"},
    height=380,
)
fig_vendor.update_coloraxes(showscale=False)
fig_vendor.update_layout(
    margin=dict(l=10, r=20, t=20, b=30),
    yaxis=dict(autorange="reversed"),
)
st.plotly_chart(fig_vendor, use_container_width=True)

# Vendor table
st.dataframe(
    df_v[["vendor_name", "total_spent"]].rename(
        columns={"vendor_name": "Vendor", "total_spent": "Total Spent (₹)"}
    ).style.format({"Total Spent (₹)": "₹{:,.2f}"}),
    use_container_width=True,
    height=320,
)

st.divider()

# ─── Reconciliation Table ─────────────────────────────────────────────────────
st.subheader("🔍 Reconciliation Table")

total_rev_full  = df_pnl["revenue"].sum()
total_exp_full  = df_pnl["expense"].sum()
total_prof_full = df_pnl["profit"].sum()
avg_margin_full = total_prof_full / total_rev_full * 100 if total_rev_full > 0 else 0

# fact_expense total (operational non-payroll expenses)
exp_ops_total = df_cat["total_expense"].sum()

recon_data = {
    "Metric": [
        "Total Revenue (18 months)",
        "Total Expense (18 months)",
        "Net Profit (18 months)",
        "Avg Profit Margin %",
        "Operational Expense (fact_expense)",
        "Number of Expense Categories",
        "Top Vendor Spending",
    ],
    "Calculated Value": [
        fmt_cr(total_rev_full),
        fmt_cr(total_exp_full),
        fmt_cr(total_prof_full),
        f"{avg_margin_full:.2f}%",
        fmt_cr(exp_ops_total),
        str(len(df_cat)),
        df_vendors.iloc[0]["vendor_name"] + " " + fmt_lakh(df_vendors.iloc[0]["total_spent"]),
    ],
    "Source": [
        "fact_ledger + dim_account (INCOME, is_group=N)",
        "fact_ledger + dim_account (EXPENSE, is_group=N)",
        "Revenue − Expense",
        "Profit ÷ Revenue × 100",
        "fact_expense + dim_account (is_group=N)",
        "Distinct account_name in fact_expense",
        "fact_expense + dim_vendor (top 1)",
    ],
    "Note": [
        "Detail accounts only; group accounts excluded",
        "Detail accounts only; group accounts excluded",
        "Positive = profitable",
        "Full 18-month period",
        "Non-payroll operational expenses",
        "",
        "Largest single vendor by cumulative spend",
    ],
}

df_recon = pd.DataFrame(recon_data)
st.dataframe(df_recon, use_container_width=True, hide_index=True)

st.divider()

# ─── Monthly P&L Table ────────────────────────────────────────────────────────
with st.expander("📋 Monthly P&L Detail Table", expanded=False):
    df_display = df_view.copy()
    df_display = df_display.rename(columns={
        "month_period": "Month",
        "revenue": "Revenue (₹)",
        "expense": "Expense (₹)",
        "profit": "Profit (₹)",
        "margin_pct": "Margin %",
    })
    st.dataframe(
        df_display.style.format({
            "Revenue (₹)": "₹{:,.0f}",
            "Expense (₹)": "₹{:,.0f}",
            "Profit (₹)":  "₹{:,.0f}",
            "Margin %":    "{:.2f}%",
        }).background_gradient(subset=["Profit (₹)"], cmap="RdYlGn"),
        use_container_width=True,
        height=400,
    )

st.divider()

# ─── Business Findings ────────────────────────────────────────────────────────
st.subheader("💡 Three Business Findings")

with st.container(border=True):
    st.markdown("""
**Finding 1 — Margin Compression Despite Revenue Growth (Apr 2026 onwards)**

Revenue grew from ~₹6.1 Cr/month (2025 average) to ~₹7.8 Cr/month (Apr–Sep 2026),
a ~28 % increase. However, the profit margin dipped below 10 % in Apr 2026, the lowest
since the period began. Total expense for Apr 2026 reached ₹7.2 Cr — growing faster than
revenue. This signals that cost scaling is outpacing revenue, compressing margins even as
top-line grows.

> **Action:** Conduct a cost-driver review for April 2026; identify whether this is a
> seasonal spike or structural cost escalation.
""")

with st.container(border=True):
    st.markdown("""
**Finding 2 — Vendor Concentration Risk: Top 2 Vendors Account for >19% of All Operational Spend**

Skyline Realty Holdings (₹1.99 Cr) and StratoHost Infrastructure (₹1.68 Cr) together represent
over 19 % of total operational expenses. Cloud Hosting and Office Rent are the top two categories.
Dependence on a small number of high-spend vendors creates negotiation leverage risk and potential
single-point-of-failure exposure.

> **Action:** Renegotiate long-term contracts with top 2 vendors; evaluate alternative cloud/office
> providers to introduce price competition.
""")

with st.container(border=True):
    st.markdown("""
**Finding 3 — Expense Seasonality: Q1 FY (April) Consistently Shows Peak Costs**

Both April 2025 (₹6.48 Cr expense) and April 2026 (₹7.20 Cr expense) show the highest monthly
expense in their respective financial years. This is likely driven by annual contract renewals,
insurance premiums, and recruitment costs at the start of the financial year. Revenue does not
spike proportionally, causing margin dips each April.

> **Action:** Smooth large annual costs across quarters (e.g., monthly accruals) to avoid sharp
> margin distortion in the first month of each financial year.
""")

st.divider()

# ─── Revenue Grows, Margins Fall — Explanation ────────────────────────────────
st.subheader("🔎 Why Can Revenue Grow While Margins Fall? — Three Explanations")

tab1, tab2, tab3 = st.tabs(["1. Rising Fixed Costs", "2. Pricing Pressure", "3. Mix Shift"])

with tab1:
    st.markdown("""
**Reason: Fixed costs (rent, infrastructure, headcount) expand to support growth, but revenue has not yet caught up.**

As a business scales, it hires more staff, leases larger office space, and expands cloud infrastructure
*before* the full revenue from those investments materialises. In 2026, Aura Workforce expanded headcount
(as seen in prior dashboard metrics), but payroll and infrastructure costs grew faster than revenue.

**Data needed to verify:**
- Monthly headcount vs monthly payroll cost trend (from `fact_headcount_monthly` + `fact_payroll`)
- Payroll as % of revenue over time
- Rent/cloud cost as % of revenue
""")

with tab2:
    st.markdown("""
**Reason: Competitive pressure forces discounting, lowering revenue per unit even as volumes rise.**

Revenue can grow in total if more clients are acquired, but if each new client is won at a lower
contract rate (due to pricing pressure or discounts), the revenue per unit of effort falls. Meanwhile
the cost to service each client may remain constant or rise.

**Data needed to verify:**
- Average revenue per client/contract (from `fact_invoice` + `dim_client`)
- Number of clients over time (distinct `client_id` count per month)
- Average invoice value trend
""")

with tab3:
    st.markdown("""
**Reason: The business shifts toward lower-margin product lines or service categories as it grows.**

If Aura Workforce starts winning more contracts in lower-margin segments (e.g., bulk staffing vs
high-value analytics consulting), total revenue can grow from volume, but the blended margin falls
because the new revenue mix carries lower profitability.

**Data needed to verify:**
- Revenue segmented by service type / product category (requires a `service_category` column in
  `fact_invoice` or `dim_client`)
- Gross margin per service line
- Share of revenue by segment over time
""")

st.caption("PulseIQ Analytics · Task 11 · Phase 3 · Aura Workforce by GrowMar")
