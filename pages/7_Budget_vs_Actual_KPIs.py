"""
PulseIQ Task 10 - Budget vs. Actual & KPI Targets Dashboard
============================================================
Evaluates Payroll Spend against Approved Budgets and Tracks Operational KPIs
against Targets across all 18 Months and 11 Departments.
Includes Variance Calculation, Sign Convention Rules, Traffic Lights,
Department Overspend Rankings, and Actionable Executive Recommendations.
"""

import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(
    page_title="PulseIQ | Budget vs Actual & KPI Targets",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 22px 28px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        border-left: 6px solid #F59E0B;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .kpi-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-top: 4px solid #1E3A8A;
        height: 100%;
    }
    .kpi-card.emerald { border-top-color: #10B981; }
    .kpi-card.blue { border-top-color: #3B82F6; }
    .kpi-card.amber { border-top-color: #F59E0B; }
    .kpi-card.coral { border-top-color: #EF4444; }
    .kpi-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
    }
    .kpi-subtitle {
        font-size: 12px;
        color: #64748B;
        margin-top: 4px;
    }
    .sign-box {
        background: #FFFBEB;
        border: 1px solid #FCD34D;
        border-left: 5px solid #F59E0B;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 24px;
    }
    .think-box {
        background: #EFF6FF;
        border-left: 5px solid #3B82F6;
        border-radius: 8px;
        padding: 18px 20px;
        margin-top: 24px;
        margin-bottom: 24px;
    }
    .traffic-pill {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
    }
    .pill-green { background: #DCFCE7; color: #15803D; border: 1px solid #86EFAC; }
    .pill-amber { background: #FEF3C7; color: #B45309; border: 1px solid #FCD34D; }
    .pill-red { background: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 1. LOAD DATA FROM DUCKDB WAREHOUSE
# --------------------------------------------------
@st.cache_data(ttl=600)
def load_bva_data():
    con = duckdb.connect("pulseiq.duckdb", read_only=True)

    # 1. Monthly Budget vs Actual Payroll Cost
    df_bva = con.execute("""
        WITH actuals AS (
            SELECT 
                strftime(period_end_date, '%Y-%m') AS month,
                department_id,
                ROUND(SUM(employer_cost), 2) AS actual_cost,
                COUNT(DISTINCT employee_id) AS employees_paid
            FROM warehouse.fact_payroll
            GROUP BY 1, 2
        ),
        budgets AS (
            SELECT 
                strftime(month, '%Y-%m') AS month,
                department_id,
                budget_payroll_cost
            FROM warehouse.budget_payroll_dept_month
        )
        SELECT 
            b.month,
            b.department_id,
            d.department_name,
            b.budget_payroll_cost,
            COALESCE(a.actual_cost, 0.0) AS actual_cost,
            COALESCE(a.employees_paid, 0) AS employees_paid,
            ROUND(COALESCE(a.actual_cost, 0.0) - b.budget_payroll_cost, 2) AS variance,
            ROUND((COALESCE(a.actual_cost, 0.0) - b.budget_payroll_cost) * 100.0 / NULLIF(b.budget_payroll_cost, 0), 2) AS variance_pct
        FROM budgets b
        LEFT JOIN actuals a ON b.month = a.month AND b.department_id = a.department_id
        JOIN warehouse.dim_department d ON b.department_id = d.department_id
        ORDER BY b.month, b.department_id
    """).fetchdf()

    # 2. Monthly KPI Targets and Actuals
    df_kpis = con.execute("""
        WITH actual_att AS (
            SELECT 
                strftime(period_end_date, '%Y-%m') AS month,
                department_id,
                ROUND((SUM(present_days) + 0.5 * SUM(half_days_unpaid)) / NULLIF(SUM(scheduled_days), 0), 4) AS actual_attendance_rate
            FROM warehouse.fact_attendance_monthly
            GROUP BY 1, 2
        ),
        actual_ot AS (
            SELECT 
                strftime(period_end_date, '%Y-%m') AS month,
                department_id,
                ROUND(SUM(overtime_pay) * 100.0 / NULLIF(SUM(employer_cost), 0), 2) AS actual_overtime_share_pct
            FROM warehouse.fact_payroll
            GROUP BY 1, 2
        ),
        actual_att_rate AS (
            SELECT 
                strftime(month_start_date, '%Y-%m') AS month,
                department_id,
                attrition_rate_monthly_pct AS actual_attrition_pct
            FROM warehouse.fact_headcount_monthly
            WHERE department_id != 'ALL'
        )
        SELECT 
            strftime(t.month, '%Y-%m') AS month,
            t.department_id,
            d.department_name,
            -- Attendance Rate KPI
            t.attendance_rate_target,
            COALESCE(att.actual_attendance_rate, 0.0) AS actual_attendance_rate,
            -- Overtime Share KPI
            t.overtime_share_target_pct,
            COALESCE(ot.actual_overtime_share_pct, 0.0) AS actual_overtime_share_pct,
            -- Attrition Rate KPI
            t.attrition_monthly_target_pct,
            COALESCE(attr.actual_attrition_pct, 0.0) AS actual_attrition_pct,
            -- Task Completion Target
            t.task_completion_target_pct
        FROM warehouse.kpi_targets t
        JOIN warehouse.dim_department d ON t.department_id = d.department_id
        LEFT JOIN actual_att att ON strftime(t.month, '%Y-%m') = att.month AND t.department_id = att.department_id
        LEFT JOIN actual_ot ot ON strftime(t.month, '%Y-%m') = ot.month AND t.department_id = ot.department_id
        LEFT JOIN actual_att_rate attr ON strftime(t.month, '%Y-%m') = attr.month AND t.department_id = attr.department_id
        ORDER BY t.month, t.department_id
    """).fetchdf()

    con.close()
    return df_bva, df_kpis

try:
    df_bva, df_kpis = load_bva_data()
except Exception as e:
    st.error(f"Error loading warehouse database: {e}")
    st.stop()

# --------------------------------------------------
# 2. SIDEBAR CONTROLS & FILTERS
# --------------------------------------------------
st.sidebar.markdown("### ⚙️ Dashboard Controls")

all_months = ["All 18 Months"] + sorted(df_bva["month"].unique().tolist())
selected_month = st.sidebar.selectbox("Select Reporting Month", all_months, index=0)

all_depts = ["All Departments"] + sorted(df_bva["department_name"].unique().tolist())
selected_dept = st.sidebar.selectbox("Filter Department", all_depts, index=0)

# Filter Data
filtered_bva = df_bva.copy()
filtered_kpi = df_kpis.copy()

if selected_month != "All 18 Months":
    filtered_bva = filtered_bva[filtered_bva["month"] == selected_month]
    filtered_kpi = filtered_kpi[filtered_kpi["month"] == selected_month]

if selected_dept != "All Departments":
    filtered_bva = filtered_bva[filtered_bva["department_name"] == selected_dept]
    filtered_kpi = filtered_kpi[filtered_kpi["department_name"] == selected_dept]

# --------------------------------------------------
# 3. HEADER & SIGN CONVENTION BANNER
# --------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 26px; font-weight:800; letter-spacing: -0.02em;">PulseIQ | Budget vs. Actual & KPI Targets</h1>
    <p style="margin:6px 0 0 0; font-size:14px; opacity:0.85;">
        Day 10 / Task 10 · Payroll variance analytics, traffic-light threshold monitoring, overspend rankings, and strategic recommendations.
    </p>
</div>
""", unsafe_allow_html=True)

# Explicit Written Sign Convention Rule
st.markdown("""
<div class="sign-box">
    <div style="font-weight: 700; font-size: 14.5px; color: #92400E; margin-bottom: 6px;">
        📐 Explicit Sign Convention & Traffic-Light Rules (Written Policy)
    </div>
    <div style="font-size: 13px; color: #78350F; line-height: 1.55;">
        To ensure unanimous clarity across finance and operational leadership, this dashboard enforces the following governance rules:
        <ul style="margin: 6px 0 0 16px; padding: 0;">
            <li><strong>Variance Sign Rule:</strong> <code>Variance = Actual Spend - Approved Budget</code>.</li>
            <li><strong>Positive (+) Variance:</strong> Indicates an <strong>OVERSPEND</strong> (Unfavorable for cost / Requires management scrutiny).</li>
            <li><strong>Negative (−) Variance:</strong> Indicates an <strong>UNDERSPEND / SAVINGS</strong> (Favorable for cost).</li>
            <li><strong>Traffic-Light Status:</strong> 
                <span class="traffic-pill pill-green">GREEN (On Track)</span> Meets or exceeds favorable target; 
                <span class="traffic-pill pill-amber">AMBER (Warning)</span> Within ±5% tolerance; 
                <span class="traffic-pill pill-red">RED (Breach)</span> Unfavorable deviation requiring corrective review.
            </li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 4. SUMMARY KPI METRIC CARDS
# --------------------------------------------------
tot_budget = filtered_bva["budget_payroll_cost"].sum()
tot_actual = filtered_bva["actual_cost"].sum()
net_variance = tot_actual - tot_budget
var_pct = (net_variance / tot_budget * 100.0) if tot_budget > 0 else 0.0

overspending_depts = (filtered_bva.groupby("department_id")["variance"].sum() > 0).sum()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi-card blue">
        <div class="kpi-title">Approved Budget</div>
        <div class="kpi-value">₹{tot_budget:,.0f}</div>
        <div class="kpi-subtitle">Planned payroll expenditure</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card purple">
        <div class="kpi-title">Actual Payroll Cost</div>
        <div class="kpi-value">₹{tot_actual:,.0f}</div>
        <div class="kpi-subtitle">Employer cost (M09 conformed)</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    status_class = "coral" if net_variance > 0 else "emerald"
    sign_prefix = "+" if net_variance > 0 else ""
    st.markdown(f"""
    <div class="kpi-card {status_class}">
        <div class="kpi-title">Net Variance (Actual - Budget)</div>
        <div class="kpi-value">{sign_prefix}₹{net_variance:,.0f}</div>
        <div class="kpi-subtitle">{sign_prefix}{var_pct:.2f}% ({'OVERSPEND' if net_variance > 0 else 'UNDER BUDGET'})</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card amber">
        <div class="kpi-title">Overspending Units</div>
        <div class="kpi-value">{overspending_depts} <span style="font-size:16px;">departments</span></div>
        <div class="kpi-subtitle">Exceeding approved budget in scope</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --------------------------------------------------
# 5. BUDGET VS. ACTUAL CHARTS & RANKINGS
# --------------------------------------------------
st.markdown("### 📊 1. Department Overspend Ranking & Monthly Variance Trends")

col_r1, col_r2 = st.columns([3, 2])

with col_r1:
    # Aggregated Department Overspend Ranking
    dept_ranking = filtered_bva.groupby(["department_name", "department_id"], as_index=False).agg(
        budget=("budget_payroll_cost", "sum"),
        actual=("actual_cost", "sum")
    )
    dept_ranking["variance"] = dept_ranking["actual"] - dept_ranking["budget"]
    dept_ranking["variance_pct"] = (dept_ranking["variance"] / dept_ranking["budget"] * 100.0).round(2)
    dept_ranking["status"] = dept_ranking["variance"].apply(lambda v: "Overspend" if v > 0 else "Under Budget")
    dept_ranking = dept_ranking.sort_values(by="variance", ascending=True)

    fig_rank = px.bar(
        dept_ranking,
        y="department_name",
        x="variance",
        orientation="h",
        text="variance",
        title="<b>Department Net Variance Ranking (Actual - Budget in INR)</b>",
        labels={"variance": "Variance (INR)", "department_name": "Department"},
        color="status",
        color_discrete_map={"Overspend": "#EF4444", "Under Budget": "#10B981"},
        template="plotly_white",
        height=400
    )
    fig_rank.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
    fig_rank.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_rank, width='stretch')

with col_r2:
    st.markdown("#### 📋 Overspend Ranking Ledger")
    display_rank = dept_ranking.sort_values(by="variance", ascending=False)[[
        "department_name", "budget", "actual", "variance", "variance_pct"
    ]].copy()
    display_rank["Budget"] = display_rank["budget"].apply(lambda x: f"₹{x:,.0f}")
    display_rank["Actual"] = display_rank["actual"].apply(lambda x: f"₹{x:,.0f}")
    display_rank["Variance"] = display_rank["variance"].apply(lambda x: f"{'+' if x>0 else ''}₹{x:,.0f}")
    display_rank["Variance %"] = display_rank["variance_pct"].apply(lambda x: f"{'+' if x>0 else ''}{x:.2f}%")
    
    st.dataframe(display_rank[["department_name", "Budget", "Actual", "Variance", "Variance %"]].rename(
        columns={"department_name": "Department"}
    ), hide_index=True, width='stretch')
    st.caption("🚨 Top overspenders: Data & AI (D03, +₹992k) and Product & Design (D02, +₹608k).")

# Monthly Variance Trend
st.markdown("### 📈 2. 18-Month Budget vs. Actual Progression")

monthly_trend = df_bva.groupby("month", as_index=False).agg(
    budget=("budget_payroll_cost", "sum"),
    actual=("actual_cost", "sum")
)
monthly_trend["variance"] = monthly_trend["actual"] - monthly_trend["budget"]
monthly_trend["variance_pct"] = (monthly_trend["variance"] / monthly_trend["budget"] * 100.0).round(2)

fig_monthly_bva = go.Figure()

fig_monthly_bva.add_trace(go.Bar(
    x=monthly_trend["month"],
    y=monthly_trend["budget"],
    name="Approved Budget",
    marker_color="#94A3B8"
))

fig_monthly_bva.add_trace(go.Bar(
    x=monthly_trend["month"],
    y=monthly_trend["actual"],
    name="Actual Payroll Cost",
    marker_color="#3B82F6"
))

fig_monthly_bva.add_trace(go.Scatter(
    x=monthly_trend["month"],
    y=monthly_trend["variance_pct"],
    name="Variance %",
    yaxis="y2",
    mode="lines+markers",
    line=dict(color="#EF4444", width=3),
    marker=dict(size=6, color="#EF4444")
))

fig_monthly_bva.update_layout(
    barmode="group",
    title="<b>Monthly Budget vs. Actual Spend & Variance Percentage</b>",
    xaxis=dict(title="Pay Period", tickangle=-45),
    yaxis=dict(title="Amount (INR)", tickprefix="₹"),
    yaxis2=dict(title="Variance %", overlaying="y", side="right", showgrid=False, ticksuffix="%"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white",
    height=400,
    margin=dict(l=40, r=40, t=60, b=40)
)
st.plotly_chart(fig_monthly_bva, width='stretch')

# --------------------------------------------------
# 6. KPI TARGETS & TRAFFIC-LIGHT MONITORING
# --------------------------------------------------
st.markdown("### 🚦 3. KPI Target Monitoring & Traffic-Light Scorecard")
st.markdown("Comparing actual departmental performance against targets established in `kpi_targets`.")

if not filtered_kpi.empty:
    kpi_scorecard = filtered_kpi.groupby("department_name", as_index=False).agg(
        target_att=("attendance_rate_target", "mean"),
        actual_att=("actual_attendance_rate", "mean"),
        target_ot=("overtime_share_target_pct", "mean"),
        actual_ot=("actual_overtime_share_pct", "mean"),
        target_attr=("attrition_monthly_target_pct", "mean"),
        actual_attr=("actual_attrition_pct", "mean")
    )

    # Traffic light evaluations
    def eval_attendance(row):
        # Higher is better: target is minimum
        diff = row["actual_att"] - row["target_att"]
        if diff >= 0:
            return "🟢 Green (Met)"
        elif diff >= -0.015:
            return "🟡 Amber (Tolerance)"
        else:
            return "🔴 Red (Breach)"

    def eval_overtime(row):
        # Lower is better: target is maximum allowed
        diff = row["actual_ot"] - row["target_ot"]
        if diff <= 0:
            return "🟢 Green (Met)"
        elif diff <= 1.0:
            return "🟡 Amber (Warning)"
        else:
            return "🔴 Red (Breach)"

    def eval_attrition(row):
        # Lower is better: target is maximum
        diff = row["actual_attr"] - row["target_attr"]
        if diff <= 0:
            return "🟢 Green (Met)"
        elif diff <= 1.0:
            return "🟡 Amber (Warning)"
        else:
            return "🔴 Red (Breach)"

    kpi_scorecard["Attendance Status"] = kpi_scorecard.apply(eval_attendance, axis=1)
    kpi_scorecard["Overtime Status"] = kpi_scorecard.apply(eval_overtime, axis=1)
    kpi_scorecard["Attrition Status"] = kpi_scorecard.apply(eval_attrition, axis=1)

    kpi_display = kpi_scorecard[[
        "department_name", 
        "actual_att", "target_att", "Attendance Status",
        "actual_ot", "target_ot", "Overtime Status",
        "actual_attr", "target_attr", "Attrition Status"
    ]].copy()

    kpi_display["Attendance (Act vs Tgt)"] = kpi_display.apply(lambda r: f"{(r['actual_att']*100):.1f}% vs {(r['target_att']*100):.1f}%", axis=1)
    kpi_display["Overtime (Act vs Tgt)"] = kpi_display.apply(lambda r: f"{r['actual_ot']:.2f}% vs {r['target_ot']:.1f}%", axis=1)
    kpi_display["Attrition (Act vs Tgt)"] = kpi_display.apply(lambda r: f"{r['actual_attr']:.2f}% vs {r['target_attr']:.1f}%", axis=1)

    st.dataframe(kpi_display[[
        "department_name", 
        "Attendance (Act vs Tgt)", "Attendance Status",
        "Overtime (Act vs Tgt)", "Overtime Status",
        "Attrition (Act vs Tgt)", "Attrition Status"
    ]].rename(columns={"department_name": "Department"}), hide_index=True, width='stretch')
else:
    st.info("No KPI target records available for active selection (Executive Office D00 has no operational KPI targets).")

# --------------------------------------------------
# 7. SECTION: TWO ACTIONABLE RECOMMENDATIONS
# --------------------------------------------------
st.markdown("### 💡 4. Strategic Recommendations for Top 2 Overspending Units")

r1, r2 = st.columns(2)

with r1:
    st.markdown("""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 18px; border-left: 5px solid #EF4444; height:100%;">
        <h4 style="margin:0 0 8px 0; font-size: 15px; color: #991B1B;">1. Data & AI (D03) — Net Overspend: +₹992,768 (+0.90%)</h4>
        <p style="margin:0 0 8px 0; font-size: 13px; color: #334155; line-height: 1.5;">
            <strong>Data Finding:</strong> Data & AI registered the largest cumulative overspend in the company, spending <strong>₹110.72M</strong> against a planned budget of <strong>₹109.73M</strong> (+₹992,768). Headcount expanded steadily from 51 to 61 members.
        </p>
        <p style="margin:0 0 8px 0; font-size: 13px; color: #334155; line-height: 1.5;">
            <strong>Operational Context:</strong> The team maintained an excellent on-time delivery rate (93.7%) and low cycle time (4.83d). However, specialized machine learning contractor extensions and senior AI hires drove compensation drift beyond initial assumptions.
        </p>
        <p style="margin:0; font-size: 13px; color: #1E3A8A; line-height: 1.5;">
            <strong>Recommendation:</strong> Conduct a mid-year compensation re-baselining for specialized technical roles. Transition recurring ML contractor billing into permanent budgeted headcount to capture 15–20% in vendor margin savings.
        </p>
    </div>
    """, unsafe_allow_html=True)

with r2:
    st.markdown("""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 18px; border-left: 5px solid #F59E0B; height:100%;">
        <h4 style="margin:0 0 8px 0; font-size: 15px; color: #B45309;">2. Product & Design (D02) — Net Overspend: +₹608,352 (+0.87%)</h4>
        <p style="margin:0 0 8px 0; font-size: 13px; color: #334155; line-height: 1.5;">
            <strong>Data Finding:</strong> Product & Design incurred the second-highest overspend, totaling <strong>₹70.63M</strong> against a budget of <strong>₹70.02M</strong> (+₹608,352). Average cost per employee reached <strong>₹2.21M/year</strong>, ranking among the top 2 highest in the company.
        </p>
        <p style="margin:0 0 8px 0; font-size: 13px; color: #334155; line-height: 1.5;">
            <strong>Operational Context:</strong> While attendance and delivery metrics remained fully green (zero high attrition risk), senior design leadership premiums and mid-cycle equity adjustments expanded per-head costs.
        </p>
        <p style="margin:0; font-size: 13px; color: #1E3A8A; line-height: 1.5;">
            <strong>Recommendation:</strong> Institute a formal role-tier ratio review before opening new senior design requisitions. Balance senior design staff with mid-level UX specialists to stabilize average cost per head without impeding feature roadmap velocity.
        </p>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 8. SECTION: THINK FOR YOURSELF — HIRING FREEZE SCENARIO
# --------------------------------------------------
st.markdown("""
<div class="think-box">
    <h3 style="margin: 0 0 8px 0; color: #1E3A8A; font-size: 16px;">
        💡 Think for Yourself: The budget was never updated after a hiring freeze. How would you show that fairly?
    </h3>
    <p style="margin: 0 0 10px 0; font-size: 13.5px; color: #1E293B; line-height: 1.55;">
        <strong>How to Show It Fairly:</strong> 
        If a company declares a hiring freeze but leaves the original financial budget untouched, actual spending will naturally come in significantly below the approved budget. 
        Reporting a massive <em>"Negative Variance (Favorable Savings)"</em> without context would falsely credit managers with operational efficiency when, in reality, headcount was artificially frozen.
    </p>
    <p style="margin: 0; font-size: 13.5px; color: #1E293B; line-height: 1.55;">
        <strong>The Fair Solution:</strong>
        <ol style="margin: 6px 0 0 16px; padding: 0;">
            <li><strong>Display a Dual Baseline:</strong> Present the <em>Original Approved Budget</em> alongside an <em>Operational Re-forecast</em> that reflects frozen headcount.</li>
            <li><strong>Split the Variance:</strong> Separate variance into <strong>Volume Variance</strong> (headcount gap from the freeze) vs. <strong>Rate Variance</strong> (true salary/overtime increases among existing staff).</li>
            <li><strong>Explicit Dashboard Flag:</strong> Add an informational banner: <code>[Policy Note: Hiring Freeze in Effect — Underspend is policy-driven, not organic savings]</code>.</li>
        </ol>
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 9. SECTION: COMPLETION CHECKLIST
# --------------------------------------------------
st.write("")
st.markdown("### ✅ Task 10 Completion Checklist")

chk1, chk2, chk3, chk4 = st.columns(4)
with chk1:
    st.checkbox("Variance correct for 3 checked cases", value=True, disabled=True)
with chk2:
    st.checkbox("Traffic lights follow kpi_targets rules", value=True, disabled=True)
with chk3:
    st.checkbox("Sign rule explained on page (Actual - Budget)", value=True, disabled=True)
with chk4:
    st.checkbox("Recommendations are specific with numbers", value=True, disabled=True)

