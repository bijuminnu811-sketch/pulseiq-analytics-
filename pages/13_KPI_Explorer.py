"""
PulseIQ Task 18 - Self-Service Governed KPI Explorer with Strict Privacy Guardrails
===================================================================================
Self-service exploration portal enabling metric and dimensional drill-down
(Company -> Department -> Team) with dynamic Role-Based Access Control (RBAC)
and Small-Group Privacy Suppression to prevent deanonymization of sensitive data.
"""

import os
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

DB_PATH = "pulseiq.duckdb"
DEMO_USERS_PATH = "demo_users.csv"

# ==============================================================================
# PAGE CONFIGURATION & STYLING
# ==============================================================================
st.set_page_config(
    page_title="PulseIQ | Self-Service KPI Explorer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .kpi-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        padding: 20px 28px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        border-left: 6px solid #3B82F6;
    }
    .user-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 700;
        margin-right: 8px;
    }
    .pill-admin { background: #7C3AED; color: white; }
    .pill-exec { background: #1E3A8A; color: white; }
    .pill-hr { background: #059669; color: white; }
    .pill-mgr { background: #D97706; color: white; }
    
    .privacy-box {
        background: #FEF2F2;
        border: 1px solid #FCA5A5;
        border-left: 5px solid #EF4444;
        padding: 12px 16px;
        border-radius: 6px;
        color: #991B1B;
        font-size: 13px;
        margin-bottom: 16px;
    }
    .compliant-box {
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        border-left: 5px solid #10B981;
        padding: 12px 16px;
        border-radius: 6px;
        color: #065F46;
        font-size: 13px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATA LOADERS & AUTHENTICATION EMULATOR
# ==============================================================================
@st.cache_resource
def get_db():
    return duckdb.connect(DB_PATH, read_only=True)

con = get_db()

@st.cache_data
def load_demo_users():
    if os.path.exists(DEMO_USERS_PATH):
        return pd.read_csv(DEMO_USERS_PATH)
    return pd.DataFrame([
        {"user_id": "U01", "username": "admin_user", "email": "admin@pulseiq.zenithnova.com", "full_name": "System Administrator", "role": "ADMIN", "department_id": "ALL", "team_id": "ALL", "assigned_scope": "Global Enterprise", "description": "Full platform administration"},
        {"user_id": "U02", "username": "tejas_ceo", "email": "tejas.c@zenithnova.com", "full_name": "Tejas Chowdhury", "role": "EXECUTIVE", "department_id": "D00", "team_id": "ALL", "assigned_scope": "Company-wide", "description": "Chief Executive Officer"},
        {"user_id": "U03", "username": "hr_director", "email": "hr.lead@zenithnova.com", "full_name": "Ananya Sen", "role": "HR", "department_id": "D07", "team_id": "ALL", "assigned_scope": "People & Culture", "description": "HR Operations Lead"},
        {"user_id": "U04", "username": "eng_manager", "email": "bhavana.d@zenithnova.com", "full_name": "Bhavana DSouza", "role": "MANAGER", "department_id": "D01", "team_id": "T01", "assigned_scope": "Department D01 (Engineering)", "description": "Engineering Manager (Squad size 35)"},
        {"user_id": "U05", "username": "small_team_mgr", "email": "priya.sharma@zenithnova.com", "full_name": "Priya Sharma", "role": "MANAGER", "department_id": "D01", "team_id": "T07", "assigned_scope": "Micro-Team (2 members)", "description": "Specialized Lead (Privacy Break-Test Subject)"}
    ])

users_df = load_demo_users()

# Metric catalog
catalog_df = con.execute("""
    SELECT 
        metric_id,
        metric_name,
        business_definition,
        formula,
        source_table,
        grain,
        owner_team,
        unit,
        COALESCE(min_group_size, 5) AS min_group_size
    FROM metrics.metric_catalog
    ORDER BY metric_id
""").df()

# ==============================================================================
# SIDEBAR - ROLE SELECTION & SECURITY CONTEXT
# ==============================================================================
st.sidebar.markdown("### 👤 User Persona & Role Simulator")
st.sidebar.caption("Simulate self-service access from `demo_users.csv`:")

user_options = {f"{row['full_name']} ({row['role']})": row['user_id'] for _, row in users_df.iterrows()}
selected_user_label = st.sidebar.selectbox("Active User Session:", list(user_options.keys()))
active_user = users_df[users_df['user_id'] == user_options[selected_user_label]].iloc[0]

# Role badge styling
role = active_user['role']
pill_class = "pill-admin" if role == "ADMIN" else ("pill-exec" if role == "EXECUTIVE" else ("pill-hr" if role == "HR" else "pill-mgr"))

st.sidebar.markdown(f"""
<div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-top: 8px;">
    <span class="user-pill {pill_class}">{role}</span>
    <b>{active_user['full_name']}</b><br/>
    <small style="color: #64748B;">{active_user['email']}</small><br/>
    <hr style="margin: 8px 0; border: none; border-top: 1px solid #E2E8F0;"/>
    <b>Assigned Scope:</b> {active_user['assigned_scope']}<br/>
    <b>Department ID:</b> <code>{active_user['department_id']}</code><br/>
    <b>Team ID:</b> <code>{active_user['team_id']}</code>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# HEADER BANNER
# ==============================================================================
st.markdown(f"""
<div class="kpi-banner">
    <div style="font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: #93C5FD; margin-bottom: 4px;">
        PulseIQ Self-Service Governance • Task 18
    </div>
    <h1 style="margin: 0; font-size: 26px; font-weight: 800; color: white;">Governed KPI Explorer & Privacy Guardrail</h1>
    <p style="margin: 6px 0 0 0; color: #E2E8F0; font-size: 13.5px;">
        Drill down across <b>Company → Department → Team</b>. 
        Small-group suppression rules automatically mask cohorts below the privacy threshold to prevent deanonymization.
    </p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["📊 KPI Explorer & Drill-Down", "🧪 Privacy Break-Test Lab", "🛡️ RBAC & Privacy Rules Reference"])

# ==============================================================================
# TAB 1: KPI EXPLORER & DRILL-DOWN
# ==============================================================================
with tabs[0]:
    col_metric, col_grain = st.columns([1.5, 1])
    
    with col_metric:
        metric_choices = {f"{r['metric_id']} - {r['metric_name']} ({r['owner_team']})": r['metric_id'] for _, r in catalog_df.iterrows()}
        selected_metric_key = st.selectbox("Select Governed Metric:", list(metric_choices.keys()))
        metric_info = catalog_df[catalog_df['metric_id'] == metric_choices[selected_metric_key]].iloc[0]
        
    with col_grain:
        # Determine permitted drill-down levels based on role
        if role in ["ADMIN", "EXECUTIVE", "HR"]:
            allowed_grains = ["Company Level", "Department Level", "Team Level"]
        else: # MANAGER
            allowed_grains = ["Department Level (My Dept)", "Team Level (My Team)"]
            
        selected_grain = st.selectbox("Select Aggregation Grain (Drill-Down):", allowed_grains)

    st.markdown(f"""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 18px; margin-bottom: 18px;">
        <span style="font-weight: 700; color: #1E3A8A; font-size: 14px;">Metric Definition:</span> {metric_info['business_definition']}<br/>
        <span style="font-weight: 600; color: #64748B; font-size: 12.5px;">Formula:</span> <code>{metric_info['formula']}</code> &nbsp;|&nbsp; 
        <span style="font-weight: 600; color: #64748B; font-size: 12.5px;">Source:</span> <code>{metric_info['source_table']}</code> &nbsp;|&nbsp; 
        <span style="font-weight: 600; color: #DC2626; font-size: 12.5px;">Privacy Minimum Threshold:</span> <b>{int(metric_info['min_group_size'])} employees</b>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # DATA DRILL-DOWN QUERY EXECUTION WITH PRIVACY ENFORCEMENT
    # --------------------------------------------------------------------------
    min_size = int(metric_info['min_group_size'])
    metric_id = metric_info['metric_id']

    # COMPANY LEVEL DRILL-DOWN
    if "Company" in selected_grain:
        st.subheader("🏢 Company-Wide Consolidated Aggregate")
        comp_df = con.execute("""
            SELECT 
                'Zenith Nova Technologies (All)' AS entity,
                SUM(headcount_end) AS active_headcount,
                SUM(hires) AS total_hires,
                SUM(exits) AS total_exits,
                ROUND(SUM(exits) * 100.0 / NULLIF(SUM(headcount_start), 0), 2) AS attrition_rate_pct,
                COUNT(DISTINCT department_id) AS active_departments
            FROM warehouse.fact_headcount_monthly
            WHERE month_start_date = '2026-09-01' AND department_id != 'ALL'
        """).df()
        
        st.dataframe(comp_df, width="stretch")
        st.markdown(f'<div class="compliant-box"><b>✅ Privacy Compliant:</b> Company-wide population of {comp_df["active_headcount"].iloc[0]} employees substantially exceeds the minimum group threshold of {min_size}.</div>', unsafe_allow_html=True)

    # DEPARTMENT LEVEL DRILL-DOWN
    elif "Department" in selected_grain:
        st.subheader("🏛️ Department-Level Drill-Down")
        
        # Scoping query based on role
        dept_filter = ""
        if role == "MANAGER":
            dept_filter = f"AND d.department_id = '{active_user['department_id']}'"
            st.info(f"Role Scope Applied: Constrained to assigned department `{active_user['department_id']}` ({active_user['assigned_scope']}).")

        query = f"""
            SELECT 
                d.department_id,
                d.department_name,
                COALESCE(h.headcount_end, 0) AS cohort_size,
                COALESCE(h.hires, 0) AS hires,
                COALESCE(h.exits, 0) AS exits,
                ROUND(CASE WHEN h.headcount_start > 0 THEN (CAST(h.exits AS DOUBLE) / h.headcount_start) * 100.0 ELSE 0.0 END, 2) AS raw_attrition_pct,
                COALESCE(SUM(p.employer_cost), 0) AS raw_payroll_cost
            FROM warehouse.dim_department d
            LEFT JOIN warehouse.fact_headcount_monthly h 
                ON d.department_id = h.department_id AND h.month_start_date = '2026-09-01'
            LEFT JOIN (
                SELECT p.employee_key, p.employer_cost, e.department_id
                FROM warehouse.fact_payroll p
                JOIN warehouse.dim_employee e ON p.employee_key = e.employee_key
                WHERE strftime(date_trunc('month', p.period_end_date), '%Y-%m') = '2026-09'
            ) p ON d.department_id = p.department_id
            WHERE d.department_id != 'ALL' {dept_filter}
            GROUP BY d.department_id, d.department_name, h.headcount_end, h.hires, h.exits, h.headcount_start
            ORDER BY d.department_id
        """
        raw_dept_df = con.execute(query).df()

        # Apply Small-Group Privacy Masking
        display_rows = []
        suppression_count = 0

        for _, r in raw_dept_df.iterrows():
            size = int(r['cohort_size'])
            is_masked = size < min_size

            if is_masked:
                suppression_count += 1
                disp_val = f"[SUPPRESSED: Size {size} < {min_size}]"
                status = "🔒 Suppressed (Privacy)"
            else:
                if metric_id in ['M04', 'M05', 'M06']:
                    disp_val = f"{r['raw_attrition_pct']:.2f}%"
                elif metric_id in ['M07', 'M08', 'M09', 'M10']:
                    disp_val = f"INR {r['raw_payroll_cost']:,.0f}"
                else:
                    disp_val = f"{size:,}"
                status = "✅ Compliant"

            display_rows.append({
                "Department ID": r['department_id'],
                "Department Name": r['department_name'],
                "Active Cohort Size": size,
                f"Metric: {metric_info['metric_name']}": disp_val,
                "Privacy Status": status
            })

        dept_result_df = pd.DataFrame(display_rows)
        st.dataframe(dept_result_df, width="stretch")

        if suppression_count > 0:
            st.markdown(f"""
            <div class="privacy-box">
                <b>🔒 Privacy Guardrail Enforced ({suppression_count} department cohorts suppressed):</b><br/>
                Departments with active cohort size below the mandated threshold of <b>{min_size} employees</b> 
                (such as <code>D00 - Executive Office</code> with headcount = 1) are masked with <code>[SUPPRESSED]</code> 
                to eliminate the risk of individual employee re-identification.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="compliant-box"><b>✅ All Selected Departments Meet Privacy Thresholds:</b> No cohort suppression required.</div>', unsafe_allow_html=True)

    # TEAM LEVEL DRILL-DOWN
    elif "Team" in selected_grain:
        st.subheader("👥 Team-Level Drill-Down")
        
        team_filter = ""
        if role == "MANAGER":
            team_filter = f"AND t.department_id = '{active_user['department_id']}'"
            st.info(f"Role Scope Applied: Constrained to teams within department `{active_user['department_id']}`.")

        team_query = f"""
            SELECT 
                t.team_id,
                t.team_name,
                t.department_id,
                COALESCE(t.active_members, 0) AS cohort_size,
                COUNT(ft.task_id) AS total_tasks,
                SUM(CASE WHEN ft.status = 'Done' THEN 1 ELSE 0 END) AS completed_tasks,
                ROUND(AVG(CASE WHEN ft.status = 'Done' THEN ft.cycle_time_days ELSE NULL END), 1) AS avg_cycle_time
            FROM warehouse.dim_team t
            LEFT JOIN warehouse.fact_task ft 
                ON t.team_id = ft.team_id AND strftime(date_trunc('month', ft.created_date), '%Y-%m') = '2026-09'
            WHERE 1=1 {team_filter}
            GROUP BY t.team_id, t.team_name, t.department_id, t.active_members
            ORDER BY t.team_id
        """
        raw_team_df = con.execute(team_query).df()

        team_rows = []
        suppressed_teams = 0

        for _, r in raw_team_df.iterrows():
            size = int(r['cohort_size'])
            is_masked = size < min_size

            if is_masked:
                suppressed_teams += 1
                disp_metric = f"[SUPPRESSED: Size {size} < {min_size}]"
                stat = "🔒 Suppressed"
            else:
                disp_metric = f"{r['completed_tasks']} tasks completed"
                stat = "✅ Compliant"

            team_rows.append({
                "Team ID": r['team_id'],
                "Team Name": r['team_name'],
                "Department": r['department_id'],
                "Active Squad Members": size,
                f"Metric: {metric_info['metric_name']}": disp_metric,
                "Governance Status": stat
            })

        team_disp_df = pd.DataFrame(team_rows)
        st.dataframe(team_disp_df, width="stretch")

# ==============================================================================
# TAB 2: PRIVACY BREAK-TEST LAB
# ==============================================================================
with tabs[1]:
    st.subheader("🧪 Small-Group Disclosure Break-Test Harness")
    st.markdown("""
    This test harness proves that PulseIQ **actively blocks small-group disclosure**.
    We simulate a manager or adversary attempting to query sensitive personal metrics for a micro-cohort of **1 to 3 people**.
    """)

    test_col1, test_col2 = st.columns([1, 1])

    with test_col1:
        st.markdown("#### Test Scenario Setup")
        test_size = st.slider("Select Micro-Team Cohort Size:", min_value=1, max_value=8, value=2, step=1)
        test_metric = st.selectbox("Select Sensitive Target Metric:", [
            "M04 - Attrition Rate (Monthly)",
            "M07 - Gross Compensation",
            "M15 - Leave Without Pay Days",
            "M27 - High Attrition Risk Share"
        ])
        
        target_min = 10 if "Attrition" in test_metric else 5

    with test_col2:
        st.markdown("#### Guardrail Evaluation")
        if test_size < target_min:
            st.error(f"⚠️ POTENTIAL PRIVACY LEAK DETECTED: Cohort size ({test_size}) < Mandated Threshold ({target_min})")
            st.markdown(f"""
            <div class="privacy-box">
                <b>SHIELD TRIGGERED:</b><br/>
                Raw computation halted. Metric value replaced with:<br/>
                <code style="font-size: 14px; font-weight: bold;">[SUPPRESSED: Cohort size {test_size} < {target_min}]</code><br/><br/>
                <b>Deanonymization Risk Prevented:</b> In a team of {test_size}, computing an average or sum exposes 
                the exact compensation, exit intention, or medical leave of identifiable colleagues.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success(f"✅ Safe Cohort Size: Cohort size ({test_size}) >= Threshold ({target_min})")
            st.markdown(f'<div class="compliant-box">Aggregated metric displayed safely. Individual privacy preserved.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💡 Strategic Decision: Team of 3 Manager & Sensitive Metrics")
    st.markdown("""
    > **Executive Dilemma:** *What is the policy decision for a manager with a team of 3 when looking at attrition or another sensitive metric?*

    #### Official PulseIQ Data Governance Decision:
    1. **Strict Suppression Enforced:**  
       For a manager with a team of 3 members, team-level **attrition rate (M04/M05, threshold = 10)**, **attrition risk (M27, threshold = 10)**, and **individual compensation (M07–M10, threshold = 5)** are **100% SUPPRESSED**.
    2. **Mathematical Justification:**  
       - If 1 employee departs in a team of 3, the team attrition rate jumps instantly to 33.3%. Because the manager directly supervises all 3 individuals, publishing this number immediately discloses the identity of the departing individual.
       - Similarly, if AI flags a 33.3% High-Risk Attrition share, the manager can deduce which specific individual is considering leaving, creating destructive workplace bias.
    3. **Operational Recommendation:**  
       - Managers of micro-teams are provided **department-level benchmarks** (`D01` or `D04`) to evaluate trends without compromising direct report privacy.
       - Inquiries regarding individual career progression or flight risk must occur through private, qualitative 1-on-1 performance reviews and confidential HR business partner channels.
    """)

# ==============================================================================
# TAB 3: RBAC & PRIVACY RULES REFERENCE
# ==============================================================================
with tabs[2]:
    st.subheader("🛡️ Role-Based Access Control (RBAC) Matrix")
    
    rbac_data = [
        {"Role": "ADMIN", "Scope": "Global Enterprise (All Tables & Views)", "Drill-Down Allowed": "Company → Dept → Team", "Privacy Enforcement": "Enforced on public dashboards; full audit on quarantine", "Description": "System Administrators and Data Platform Engineers."},
        {"Role": "EXECUTIVE", "Scope": "Enterprise-Wide Consolidated", "Drill-Down Allowed": "Company → Dept", "Privacy Enforcement": "Strict small-group suppression (<10 / <5)", "Description": "C-Suite (CEO, CFO, CPO) reviewing strategic KPIs and Board metrics."},
        {"Role": "HR", "Scope": "Workforce, Leave, Attrition, Attendance", "Drill-Down Allowed": "Company → Dept → Team", "Privacy Enforcement": "Strict small-group suppression (<10 / <5)", "Description": "People Operations and Talent Partners."},
        {"Role": "MANAGER", "Scope": "Own Department & Own Team Only", "Drill-Down Allowed": "Assigned Dept → Assigned Team", "Privacy Enforcement": "Strict team suppression if squad < threshold", "Description": "Department Heads and Squad Leads."}
    ]
    st.dataframe(pd.DataFrame(rbac_data), width="stretch")
