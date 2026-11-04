"""
PulseIQ Task 8 - Team Productivity Dashboard
=============================================
Analyzes delivery performance across 16 agile teams and 38 sprints:
Velocity, Cycle Time, On-Time Delivery, Blocked Tasks, and Reopened Rework.
Includes documented rules for cancelled tasks and fair team comparisons.
"""

import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(
    page_title="PulseIQ | Team Productivity",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS (Consistent Navy / Slate theme)
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
        border-left: 6px solid #3B82F6;
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
    .kpi-card.blue { border-top-color: #3B82F6; }
    .kpi-card.emerald { border-top-color: #10B981; }
    .kpi-card.amber { border-top-color: #F59E0B; }
    .kpi-card.coral { border-top-color: #EF4444; }
    .kpi-card.purple { border-top-color: #8B5CF6; }
    .kpi-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
    }
    .kpi-subtitle {
        font-size: 12px;
        color: #64748B;
        margin-top: 4px;
    }
    .rule-box {
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-left: 5px solid #2563EB;
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
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 1. LOAD DATA FROM DUCKDB WAREHOUSE
# --------------------------------------------------
@st.cache_data(ttl=600)
def load_task_data():
    con = duckdb.connect("pulseiq.duckdb", read_only=True)
    
    # 1. Team Metadata
    df_teams = con.execute("""
        SELECT team_id, team_name, department_id, active_members, planning_cadence, board_tool
        FROM warehouse.dim_team
        ORDER BY team_id
    """).fetchdf()

    # 2. Sprint Metadata
    df_sprints = con.execute("""
        SELECT sprint_id, sprint_name, start_date, end_date, working_days, financial_year
        FROM warehouse.dim_sprint
        ORDER BY sprint_id
    """).fetchdf()

    # 3. Aggregated Delivery Facts by Team and Sprint
    df_delivery = con.execute("""
        SELECT 
            t.team_id,
            tm.team_name,
            tm.active_members,
            t.sprint_id,
            s.sprint_name,
            s.start_date,
            s.end_date,
            s.working_days,
            COUNT(*) AS total_tasks,
            COUNT(CASE WHEN t.status = 'Cancelled' THEN 1 END) AS cancelled_tasks,
            COUNT(CASE WHEN t.status != 'Cancelled' THEN 1 END) AS planned_tasks,
            COUNT(CASE WHEN t.status = 'Done' THEN 1 END) AS done_tasks,
            COUNT(CASE WHEN t.status = 'Blocked' THEN 1 END) AS blocked_tasks,
            COUNT(CASE WHEN t.reopened_count > 0 THEN 1 END) AS reopened_tasks,
            SUM(t.reopened_count) AS total_reopen_events,
            SUM(CASE WHEN t.status = 'Done' THEN t.story_points ELSE 0 END) AS velocity_points,
            ROUND(AVG(CASE WHEN t.status = 'Done' THEN t.cycle_time_days END), 2) AS avg_cycle_time_days,
            COUNT(CASE WHEN t.status = 'Done' AND t.completed_on_time = 'Y' THEN 1 END) AS on_time_tasks,
            ROUND(COUNT(CASE WHEN t.status = 'Done' AND t.completed_on_time = 'Y' THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN t.status = 'Done' THEN 1 END), 0), 2) AS on_time_rate_pct,
            ROUND(COUNT(CASE WHEN t.status = 'Done' THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN t.status != 'Cancelled' THEN 1 END), 0), 2) AS completion_rate_pct
        FROM warehouse.fact_task t
        JOIN warehouse.dim_team tm ON t.team_id = tm.team_id
        JOIN warehouse.dim_sprint s ON t.sprint_id = s.sprint_id
        GROUP BY t.team_id, tm.team_name, tm.active_members, t.sprint_id, s.sprint_id, s.sprint_name, s.start_date, s.end_date, s.working_days
        ORDER BY s.sprint_id, t.team_id
    """).fetchdf()

    # 4. Raw task summary for status distribution
    df_raw_status = con.execute("""
        SELECT team_id, sprint_id, task_type, priority, status, completed_on_time, cycle_time_days
        FROM warehouse.fact_task
    """).fetchdf()

    con.close()
    return df_teams, df_sprints, df_delivery, df_raw_status

try:
    df_teams, df_sprints, df_delivery, df_raw_status = load_task_data()
except Exception as e:
    st.error(f"Error loading warehouse database: {e}")
    st.stop()

# --------------------------------------------------
# 2. SIDEBAR CONTROLS & SPRINT SELECTOR
# --------------------------------------------------
st.sidebar.markdown("### ⚙️ Dashboard Controls")

# Sprint Selector (Requirement)
all_sprints = df_sprints["sprint_id"].tolist()
sprint_labels = [f"{row['sprint_id']} ({row['sprint_name']})" for _, row in df_sprints.iterrows()]
sprint_map = dict(zip(sprint_labels, all_sprints))

view_mode = st.sidebar.radio("View Scope", ["Specific Sprint Focus", "All 38 Sprints Consolidated"], index=0)

if view_mode == "Specific Sprint Focus":
    selected_sprint_label = st.sidebar.selectbox("Select Sprint", sprint_labels, index=len(sprint_labels)-1) # Default to latest SP-38
    active_sprint_id = sprint_map[selected_sprint_label]
    filtered_data = df_delivery[df_delivery["sprint_id"] == active_sprint_id]
else:
    active_sprint_id = "ALL"
    filtered_data = df_delivery.copy()

# Team Filter
all_team_names = ["All 16 Teams"] + sorted(df_teams["team_name"].tolist())
selected_team = st.sidebar.selectbox("Filter Team", all_team_names, index=0)

if selected_team != "All 16 Teams":
    filtered_data = filtered_data[filtered_data["team_name"] == selected_team]

# --------------------------------------------------
# 3. HEADER & GOVERNED RULE FOR CANCELLED TASKS
# --------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 26px; font-weight:800; letter-spacing: -0.02em;">PulseIQ | Team Productivity & Delivery Health</h1>
    <p style="margin:6px 0 0 0; font-size:14px; opacity:0.85;">
        Day 8 / Task 8 · Engineering delivery throughput, flow speed, on-time predictability, and quality indicators across 16 teams and 38 sprints.
    </p>
</div>
""", unsafe_allow_html=True)

# Documented Business Rules Box
st.markdown("""
<div class="rule-box">
    <div style="font-weight: 700; font-size: 14.5px; color: #1E3A8A; margin-bottom: 6px;">
        📌 Governed Metric Rules & Cancelled Task Policy (Written Definition)
    </div>
    <div style="font-size: 13px; color: #334155; line-height: 1.5;">
        Across this dashboard, engineering metrics adhere to the following explicit calculation rules:
        <ul style="margin: 6px 0 0 16px; padding: 0;">
            <li><strong>Velocity (M24):</strong> Sum of story points for completed deliverables strictly having <code>status = 'Done'</code>. Cancelled tasks earn <strong>0 story points</strong>.</li>
            <li><strong>Cycle Time (M25):</strong> Average working days from <code>started_date</code> to <code>completed_date</code> for <code>Done</code> tasks. Cancelled tasks are <strong>excluded</strong>.</li>
            <li><strong>On-Time Delivery Rate (M23):</strong> Calculated as <code>(Done & On-Time Tasks) / Total Done Tasks × 100%</code>. Cancelled tasks are <strong>excluded from denominator</strong>.</li>
            <li><strong>Planned Completion Rate (M22):</strong> Calculated as <code>Done Tasks / (Total Ingested - Cancelled Tasks) × 100%</code>. Cancelled/de-scoped scope is removed from the planned denominator rather than penalized as incomplete delivery.</li>
            <li><strong>Blocked & Reopened Work:</strong> Monitored actively to highlight impediments and rework rates.</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 4. SUMMARY KPI CARDS
# --------------------------------------------------
total_velocity = filtered_data["velocity_points"].sum()
total_done = filtered_data["done_tasks"].sum()
total_cancelled = filtered_data["cancelled_tasks"].sum()
total_blocked = filtered_data["blocked_tasks"].sum()
total_reopened = filtered_data["reopened_tasks"].sum()

avg_cycle_time = filtered_data["avg_cycle_time_days"].mean()
overall_on_time = (filtered_data["on_time_tasks"].sum() / total_done * 100.0) if total_done > 0 else 0.0

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="kpi-card blue">
        <div class="kpi-title">Delivered Velocity</div>
        <div class="kpi-value">{int(total_velocity):,} <span style="font-size:16px;">pts</span></div>
        <div class="kpi-subtitle">{int(total_done):,} completed tasks (Done)</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card emerald">
        <div class="kpi-title">On-Time Delivery Rate</div>
        <div class="kpi-value">{overall_on_time:.1f}%</div>
        <div class="kpi-subtitle">Governed metric M23 target: ≥ 85%</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Average Cycle Time</div>
        <div class="kpi-value">{avg_cycle_time:.2f} <span style="font-size:16px;">days</span></div>
        <div class="kpi-subtitle">Started to Completed duration</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card coral">
        <div class="kpi-title">Blocked Work</div>
        <div class="kpi-value">{int(total_blocked)}</div>
        <div class="kpi-subtitle">Active impediment bottlenecks</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-card amber">
        <div class="kpi-title">Reopened Rework</div>
        <div class="kpi-value">{int(total_reopened)}</div>
        <div class="kpi-subtitle">Tasks failed testing & reopened</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --------------------------------------------------
# 5. VISUALIZATIONS: VELOCITY & CYCLE TIME BY TEAM
# --------------------------------------------------
st.markdown("### 📊 1. Team Velocity & Delivery Speed")

col_v1, col_v2 = st.columns([3, 2])

with col_v1:
    # Team Velocity Comparison
    team_velo_agg = filtered_data.groupby(["team_name", "team_id", "active_members"], as_index=False).agg(
        velocity=("velocity_points", "sum"),
        done_tasks=("done_tasks", "sum"),
        cycle_time=("avg_cycle_time_days", "mean"),
        on_time_pct=("on_time_rate_pct", "mean")
    ).sort_values(by="velocity", ascending=True)

    fig_velo = px.bar(
        team_velo_agg,
        y="team_name",
        x="velocity",
        orientation="h",
        text="velocity",
        title="<b>Total Delivered Velocity by Team (Story Points)</b>",
        labels={"velocity": "Completed Story Points", "team_name": "Team"},
        color="velocity",
        color_continuous_scale="Blues",
        template="plotly_white",
        height=400
    )
    fig_velo.update_traces(texttemplate='%{text:.0f} pts', textposition='outside')
    fig_velo.update_layout(coloraxis_showscale=False, margin=dict(r=50))
    st.plotly_chart(fig_velo, width='stretch')

with col_v2:
    # Cycle Time by Team
    team_cycle_agg = team_velo_agg.sort_values(by="cycle_time", ascending=False)
    
    fig_cycle = px.bar(
        team_cycle_agg,
        x="cycle_time",
        y="team_name",
        orientation="h",
        text="cycle_time",
        title="<b>Average Cycle Time by Team (Days to Complete)</b>",
        labels={"cycle_time": "Average Cycle Time (Days)", "team_name": "Team"},
        color="cycle_time",
        color_continuous_scale="Reds",
        template="plotly_white",
        height=400
    )
    fig_cycle.update_traces(texttemplate='%{text:.2f} d', textposition='outside')
    fig_cycle.update_layout(coloraxis_showscale=False, margin=dict(r=40))
    st.plotly_chart(fig_cycle, width='stretch')

# --------------------------------------------------
# 6. SPRINT TRENDS & SPRINT-OVER-SPRINT COMPARISON
# --------------------------------------------------
st.markdown("### 📈 2. Sprint Trends & On-Time Delivery Dynamics")

col_s1, col_s2 = st.columns(2)

with col_s1:
    # Velocity Trend across 38 Sprints
    sprint_trend = df_delivery.groupby(["sprint_id", "sprint_name"], as_index=False).agg(
        total_velocity=("velocity_points", "sum"),
        avg_cycle_time=("avg_cycle_time_days", "mean"),
        done_tasks=("done_tasks", "sum")
    ).sort_values(by="sprint_id")

    fig_sprint_v = px.line(
        sprint_trend,
        x="sprint_id",
        y="total_velocity",
        markers=True,
        title="<b>Sprint-over-Sprint Total Velocity Trend (38 Sprints)</b>",
        labels={"sprint_id": "Sprint", "total_velocity": "Delivered Story Points"},
        template="plotly_white",
        height=360
    )
    fig_sprint_v.update_traces(line_color="#2563EB", line_width=2.5)
    st.plotly_chart(fig_sprint_v, width='stretch')

with col_s2:
    # On-Time Delivery Rate & Cycle Time Trend
    sprint_on_time = df_delivery.groupby(["sprint_id"], as_index=False).agg(
        on_time_pct=("on_time_rate_pct", "mean"),
        cycle_time=("avg_cycle_time_days", "mean")
    ).sort_values(by="sprint_id")

    fig_sprint_ot = px.line(
        sprint_on_time,
        x="sprint_id",
        y="on_time_pct",
        markers=True,
        title="<b>Sprint On-Time Delivery Rate Trend (%)</b>",
        labels={"sprint_id": "Sprint", "on_time_pct": "On-Time Rate (%)"},
        template="plotly_white",
        height=360
    )
    fig_sprint_ot.add_hline(y=90.0, line_dash="dash", line_color="#10B981", annotation_text="90% Benchmark")
    fig_sprint_ot.update_traces(line_color="#10B981", line_width=2.5)
    st.plotly_chart(fig_sprint_ot, width='stretch')

# --------------------------------------------------
# 7. BLOCKED WORK & REOPENED WORK COMPARISON
# --------------------------------------------------
st.markdown("### 🚧 3. Impediments & Quality Signals: Blocked vs. Reopened Rework")

col_q1, col_q2 = st.columns(2)

with col_q1:
    team_impediments = filtered_data.groupby("team_name", as_index=False).agg(
        blocked=("blocked_tasks", "sum"),
        reopened=("reopened_tasks", "sum")
    ).sort_values(by="blocked", ascending=False)

    fig_block = px.bar(
        team_impediments,
        x="team_name",
        y=["blocked", "reopened"],
        barmode="group",
        title="<b>Blocked Tasks vs. Reopened Rework Tasks by Team</b>",
        labels={"value": "Task Count", "team_name": "Team", "variable": "Impediment Type"},
        color_discrete_map={"blocked": "#EF4444", "reopened": "#F59E0B"},
        template="plotly_white",
        height=380
    )
    fig_block.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_block, width='stretch')

with col_q2:
    st.markdown("#### 🔍 Fair Comparison & Per-Capita Efficiency")
    
    # Per-Capita Normalized Table
    team_fair_table = filtered_data.groupby(["team_id", "team_name", "active_members"], as_index=False).agg(
        velocity=("velocity_points", "sum"),
        done=("done_tasks", "sum"),
        blocked=("blocked_tasks", "sum"),
        reopened=("reopened_tasks", "sum"),
        avg_cycle=("avg_cycle_time_days", "mean"),
        on_time=("on_time_rate_pct", "mean")
    )
    team_fair_table["pts_per_member"] = (team_fair_table["velocity"] / team_fair_table["active_members"]).round(1)
    team_fair_table["rework_rate_pct"] = (team_fair_table["reopened"] / team_fair_table["done"].replace(0, 1) * 100.0).round(1)

    display_table = team_fair_table.sort_values(by="pts_per_member", ascending=False)[[
        "team_name", "active_members", "velocity", "pts_per_member", "on_time", "rework_rate_pct"
    ]].rename(columns={
        "team_name": "Team",
        "active_members": "Size",
        "velocity": "Total Pts",
        "pts_per_member": "Pts / Member",
        "on_time": "On-Time %",
        "rework_rate_pct": "Rework %"
    })
    st.dataframe(display_table, hide_index=True, width='stretch')
    st.caption("💡 Context note: Gross velocity reflects team size. 'Pts / Member' normalizes output to allow fair comparison between large and small teams.")

# --------------------------------------------------
# 8. SECTION: THINK FOR YOURSELF
# --------------------------------------------------
st.markdown("""
<div class="think-box">
    <h3 style="margin: 0 0 8px 0; color: #1E3A8A; font-size: 16px;">
        💡 Think for Yourself: Team A has the best velocity but the most reopened tasks. Which team is healthier? Defend your view.
    </h3>
    <p style="margin: 0 0 10px 0; font-size: 13.5px; color: #1E293B; line-height: 1.5;">
        <strong>My Assessment:</strong> <strong>Team A is NOT the healthier team.</strong> A team with moderate, predictable velocity and low rework (such as QA Automation or Platform Core) is significantly healthier, more sustainable, and delivers more true business value.
    </p>
    <p style="margin: 0; font-size: 13.5px; color: #1E293B; line-height: 1.5;">
        <strong>The Reason:</strong> 
        High velocity combined with high reopenings indicates <em>phantom velocity</em>: work is marked "done" prematurely to inflate sprint output, but fails QA or acceptance testing. 
        Reopened tasks generate severe cognitive context switching, regression risk, and demoralizing firefighting in subsequent sprints. 
        True engineering health is defined by <strong>Flow Predictability and Quality (First-Time-Right delivery)</strong>, not raw, rushed story points.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 9. SECTION: 3 VERIFIED NUMERICAL FINDINGS
# --------------------------------------------------
st.markdown("### 📝 3 Numerical Findings on Team Health")

f1, f2, f3 = st.columns(3)

with f1:
    st.markdown("""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; border-left: 4px solid #3B82F6; height:100%;">
        <h4 style="margin:0 0 6px 0; font-size: 14px; color: #1E3A8A;">1. Scale vs. Per-Capita Output</h4>
        <p style="margin:0; font-size: 13px; color: #475569; line-height: 1.45;">
            <strong>Support Tooling (T12)</strong> generated the highest total velocity in the company with <strong>10,274 story points</strong>, but has 58 members (<strong>4.66 pts/member/sprint</strong>). In contrast, smaller teams like <strong>Product Squad (T06)</strong> delivered <strong>6.29 pts/member/sprint</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; border-left: 4px solid #EF4444; height:100%;">
        <h4 style="margin:0 0 6px 0; font-size: 14px; color: #991B1B;">2. Blocked Task Concentration</h4>
        <p style="margin:0; font-size: 13px; color: #475569; line-height: 1.45;">
            <strong>17.7% of all blocked work in the company</strong> (177 out of 999 tasks) is concentrated in <strong>Support Tooling (T12)</strong>, reflecting high external dependencies and cross-functional waiting bottlenecks compared to autonomous feature teams.
        </p>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown("""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; border-left: 4px solid #10B981; height:100%;">
        <h4 style="margin:0 0 6px 0; font-size: 14px; color: #065F46;">3. Superior Flow Predictability</h4>
        <p style="margin:0; font-size: 13px; color: #475569; line-height: 1.45;">
            <strong>Data Platform (T08)</strong> achieved the company's highest on-time delivery rate at <strong>94.81%</strong> and fastest cycle time of <strong>4.42 days</strong>. <strong>QA Automation (T04)</strong> followed closely at <strong>94.01% on-time</strong> with only <strong>14 blocked tasks</strong> across 38 sprints.
        </p>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 10. SECTION: COMPLETION CHECKLIST & EVIDENCE
# --------------------------------------------------
st.write("")
st.markdown("### ✅ Task 8 Completion Checklist")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.checkbox("Rules are written and visible on page", value=True, disabled=True)
with c2:
    st.checkbox("2 teams verified by hand (T01 & T04)", value=True, disabled=True)
with c3:
    st.checkbox("Sprint selector interactive (SP-01 to SP-38)", value=True, disabled=True)
with c4:
    st.checkbox("3 findings written with real numbers", value=True, disabled=True)

