import duckdb
import streamlit as st
import pandas as pd

# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="Executive Company Health Scorecard",
    page_icon="📊",
    layout="wide",
)

st.title("Executive Company Health Scorecard")
st.caption("Company health at a glance • Source: approved metrics layer")

DB_PATH = "pulseiq.duckdb"


# =========================================================
# DATABASE CONNECTION
# =========================================================

@st.cache_resource
def get_connection():
    return duckdb.connect(DB_PATH, read_only=True)


c = get_connection()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def run_query(query, params=None):
    """
    Run a DuckDB query.
    If parameters are supplied, pass them.
    Otherwise run without parameters.
    """
    if params is None:
        return c.execute(query).df()

    return c.execute(query, params).df()


def get_target(month, target_column):
    """
    Get KPI target from warehouse.kpi_targets.
    Uses the selected month.
    """
    query = f"""
        SELECT {target_column}
        FROM warehouse.kpi_targets
        WHERE month = CAST(? || '-01' AS DATE)
        LIMIT 1
    """

    result = c.execute(query, [month]).fetchone()

    if result is None:
        return None

    return result[0]


def higher_is_better_status(value, target):
    if value is None or target is None:
        return "⚪ No target"

    if value >= target:
        return "🟢 On target"

    if value >= target * 0.90:
        return "🟡 Watch"

    return "🔴 Below target"


def lower_is_better_status(value, target):
    if value is None or target is None:
        return "⚪ No target"

    if value <= target:
        return "🟢 On target"

    if value <= target * 1.10:
        return "🟡 Watch"

    return "🔴 Above target"


def trend(current, previous, higher_is_better=True):
    if current is None or previous is None:
        return "→ No previous data"

    if current > previous:
        return "↑ Improving" if higher_is_better else "↑ Worsening"

    if current < previous:
        return "↓ Improving" if not higher_is_better else "↓ Worsening"

    return "→ Stable"


def money(value):
    if value is None:
        return "—"

    return f"₹{value:,.0f}"


def percent(value):
    if value is None:
        return "—"

    return f"{value:.2f}%"


# =========================================================
# AVAILABLE MONTHS
# =========================================================

months_df = run_query("""
    SELECT DISTINCT month_period
    FROM metrics.m16_revenue
    ORDER BY month_period DESC
""")

if months_df.empty:
    st.error("No monthly data found in the approved metric views.")
    st.stop()

months = months_df["month_period"].tolist()

selected_month = st.selectbox(
    "Select month",
    months,
    index=0,
)


# =========================================================
# PREVIOUS MONTH
# =========================================================

previous_month_df = run_query(
    """
    SELECT MAX(month_period)
    FROM metrics.m16_revenue
    WHERE month_period < ?
    """,
    [selected_month],
)

previous_month = previous_month_df.iloc[0, 0]


# =========================================================
# TARGETS
# =========================================================

attendance_target = get_target(
    selected_month,
    "attendance_rate_target",
)

overtime_target = get_target(
    selected_month,
    "overtime_share_target_pct",
)

attrition_target = get_target(
    selected_month,
    "attrition_monthly_target_pct",
)

task_target = get_target(
    selected_month,
    "task_completion_target_pct",
)

# Attendance target is stored as a ratio, e.g. 0.94 = 94%.
if attendance_target is not None and attendance_target <= 1:
    attendance_target = attendance_target * 100


# =========================================================
# KPI 1 — ATTRITION
# =========================================================

attrition_df = run_query(
    """
    SELECT
        AVG(attrition_pct_compliant) AS value
    FROM metrics.m04_attrition_rate_monthly
    WHERE month_start_date = CAST(? || '-01' AS DATE)
      AND is_privacy_masked = FALSE
    """,
    [selected_month],
)

attrition = attrition_df.iloc[0]["value"]


previous_attrition_df = run_query(
    """
    SELECT
        AVG(attrition_pct_compliant) AS value
    FROM metrics.m04_attrition_rate_monthly
    WHERE month_start_date = CAST(? || '-01' AS DATE)
      AND is_privacy_masked = FALSE
    """,
    [previous_month],
)

previous_attrition = previous_attrition_df.iloc[0]["value"]


# =========================================================
# KPI 2 — OVERTIME
# =========================================================

overtime_df = run_query(
    """
    SELECT
        AVG(overtime_share_pct_compliant) AS value
    FROM metrics.m11_overtime_share
    WHERE month_period = ?
      AND is_privacy_masked = FALSE
    """,
    [selected_month],
)

overtime = overtime_df.iloc[0]["value"]


previous_overtime_df = run_query(
    """
    SELECT
        AVG(overtime_share_pct_compliant) AS value
    FROM metrics.m11_overtime_share
    WHERE month_period = ?
      AND is_privacy_masked = FALSE
    """,
    [previous_month],
)

previous_overtime = previous_overtime_df.iloc[0]["value"]


# =========================================================
# KPI 3 — ATTENDANCE
# =========================================================

attendance_df = run_query(
    """
    SELECT
        AVG(attendance_rate_compliant) AS value
    FROM metrics.m13_attendance_rate
    WHERE month_period = ?
      AND is_privacy_masked = FALSE
    """,
    [selected_month],
)

attendance = attendance_df.iloc[0]["value"]

previous_attendance_df = run_query(
    """
    SELECT
        AVG(attendance_rate_compliant) AS value
    FROM metrics.m13_attendance_rate
    WHERE month_period = ?
      AND is_privacy_masked = FALSE
    """,
    [previous_month],
)

previous_attendance = previous_attendance_df.iloc[0]["value"]


# Attendance may be stored as 0.94 instead of 94.
if attendance is not None and attendance <= 1:
    attendance = attendance * 100

if previous_attendance is not None and previous_attendance <= 1:
    previous_attendance = previous_attendance * 100


# =========================================================
# KPI 4 — REVENUE
# =========================================================

revenue_df = run_query(
    """
    SELECT
        SUM(revenue) AS value
    FROM metrics.m16_revenue
    WHERE month_period = ?
    """,
    [selected_month],
)

revenue = revenue_df.iloc[0]["value"]


previous_revenue_df = run_query(
    """
    SELECT
        SUM(revenue) AS value
    FROM metrics.m16_revenue
    WHERE month_period = ?
    """,
    [previous_month],
)

previous_revenue = previous_revenue_df.iloc[0]["value"]


# =========================================================
# KPI 5 — NET PROFIT
# =========================================================

profit_df = run_query(
    """
    SELECT
        net_profit AS value
    FROM metrics.m17_net_profit
    WHERE month_period = ?
    LIMIT 1
    """,
    [selected_month],
)

net_profit = (
    profit_df.iloc[0]["value"]
    if not profit_df.empty
    else None
)


previous_profit_df = run_query(
    """
    SELECT
        net_profit AS value
    FROM metrics.m17_net_profit
    WHERE month_period = ?
    LIMIT 1
    """,
    [previous_month],
)

previous_net_profit = (
    previous_profit_df.iloc[0]["value"]
    if not previous_profit_df.empty
    else None
)


# =========================================================
# KPI 6 — OPERATING MARGIN
# =========================================================

margin_df = run_query(
    """
    SELECT
        operating_margin_pct AS value
    FROM metrics.m18_operating_margin
    WHERE month_period = ?
    LIMIT 1
    """,
    [selected_month],
)

operating_margin = (
    margin_df.iloc[0]["value"]
    if not margin_df.empty
    else None
)


previous_margin_df = run_query(
    """
    SELECT
        operating_margin_pct AS value
    FROM metrics.m18_operating_margin
    WHERE month_period = ?
    LIMIT 1
    """,
    [previous_month],
)

previous_operating_margin = (
    previous_margin_df.iloc[0]["value"]
    if not previous_margin_df.empty
    else None
)


# =========================================================
# KPI 7 — PAYROLL % OF REVENUE
# =========================================================

payroll_df = run_query(
    """
    SELECT
        payroll_pct_of_revenue AS value
    FROM metrics.m19_payroll_pct_revenue
    WHERE month_period = ?
    LIMIT 1
    """,
    [selected_month],
)

payroll_pct = (
    payroll_df.iloc[0]["value"]
    if not payroll_df.empty
    else None
)


previous_payroll_df = run_query(
    """
    SELECT
        payroll_pct_of_revenue AS value
    FROM metrics.m19_payroll_pct_revenue
    WHERE month_period = ?
    LIMIT 1
    """,
    [previous_month],
)

previous_payroll_pct = (
    previous_payroll_df.iloc[0]["value"]
    if not previous_payroll_df.empty
    else None
)


# =========================================================
# KPI 8 — TASK COMPLETION
# =========================================================

task_df = run_query("""
    SELECT
        AVG(completion_rate_compliant) AS value
    FROM metrics.m22_task_completion_rate
    WHERE is_privacy_masked = FALSE
""")

task_completion = task_df.iloc[0]["value"]


# =========================================================
# SCORECARD TITLE
# =========================================================

st.divider()

st.subheader(f"Company Health — {selected_month}")

st.caption(
    "Executive scorecard using approved metric views. "
    "Targets are sourced from warehouse.kpi_targets where available."
)


# =========================================================
# ROW 1 — PEOPLE & OPERATIONS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Attrition Rate",
        percent(attrition),
        trend(
            attrition,
            previous_attrition,
            higher_is_better=False,
        ),
    )

    st.caption(
        f"Target ≤ {attrition_target:.1f}%  •  "
        f"{lower_is_better_status(attrition, attrition_target)}"
        if attrition_target is not None
        else "Target not available"
    )


with col2:
    st.metric(
        "Overtime Share",
        percent(overtime),
        trend(
            overtime,
            previous_overtime,
            higher_is_better=False,
        ),
    )

    st.caption(
        f"Target ≤ {overtime_target:.1f}%  •  "
        f"{lower_is_better_status(overtime, overtime_target)}"
        if overtime_target is not None
        else "Target not available"
    )


with col3:
    st.metric(
        "Attendance Rate",
        percent(attendance),
        trend(
            attendance,
            previous_attendance,
            higher_is_better=True,
        ),
    )

    st.caption(
        f"Target ≥ {attendance_target:.1f}%  •  "
        f"{higher_is_better_status(attendance, attendance_target)}"
        if attendance_target is not None
        else "Target not available"
    )


with col4:
    st.metric(
        "Task Completion",
        percent(task_completion),
        "Latest sprint data",
    )

    st.caption(
        f"Target ≥ {task_target:.1f}%  •  "
        f"{higher_is_better_status(task_completion, task_target)}"
        if task_target is not None
        else "Target not available"
    )


# =========================================================
# ROW 2 — FINANCIAL HEALTH
# =========================================================

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Revenue",
        money(revenue),
        trend(
            revenue,
            previous_revenue,
            higher_is_better=True,
        ),
    )

    st.caption("Source: M16 Revenue")


with col2:
    st.metric(
        "Net Profit",
        money(net_profit),
        trend(
            net_profit,
            previous_net_profit,
            higher_is_better=True,
        ),
    )

    st.caption("Source: M17 Net Profit")


with col3:
    st.metric(
        "Operating Margin",
        percent(operating_margin),
        trend(
            operating_margin,
            previous_operating_margin,
            higher_is_better=True,
        ),
    )

    st.caption("Source: M18 Operating Margin")


with col4:
    st.metric(
        "Payroll / Revenue",
        percent(payroll_pct),
        trend(
            payroll_pct,
            previous_payroll_pct,
            higher_is_better=False,
        ),
    )

    st.caption("Source: M19 Payroll % Revenue")


# =========================================================
# KPI DEFENCE
# =========================================================

st.divider()

st.subheader("Why these 8 KPIs?")

kpi_reasons = [
    (
        "Attrition Rate",
        "Shows whether employees are leaving at a concerning rate.",
    ),
    (
        "Overtime Share",
        "Shows whether overtime is increasing payroll pressure.",
    ),
    (
        "Attendance Rate",
        "Shows workforce availability and attendance health.",
    ),
    (
        "Task Completion",
        "Shows whether teams are completing planned work.",
    ),
    (
        "Revenue",
        "Shows the company's monthly income.",
    ),
    (
        "Net Profit",
        "Shows whether the company is generating profit after expenses.",
    ),
    (
        "Operating Margin",
        "Shows profitability relative to revenue.",
    ),
    (
        "Payroll / Revenue",
        "Shows how much revenue is being consumed by payroll.",
    ),
]

for name, reason in kpi_reasons:
    st.write(f"**{name}** — {reason}")


# =========================================================
# DETAILED PAGE LINKS
# =========================================================

st.divider()

st.subheader("Detailed analysis")

st.markdown("""
- [Attendance & Leave Trends](./3_Attendance_Leave_Trends)
- [Payroll Cost Analysis](./5_Payroll_Cost_Analysis)
- [Profit & Loss Analytics](./8_Profit_Loss_Analytics)
- [Invoices, Receivables & Cash Flow](./9_Invoices_Receivables_Cash_Flow)
- [Cross Department Impact](./10_Cross_Department_Impact)
""")

st.caption(
    "Task 15 • Executive Company Health Scorecard • "
    "All headline KPI values are sourced from approved metric views."
)