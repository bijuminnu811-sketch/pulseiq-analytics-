import streamlit as st
import duckdb
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="PulseIQ | Attendance & Leave",
    layout="wide"
)

st.title("PulseIQ | Attendance & Leave Trends")
st.caption(
    "Workforce attendance, punctuality, overtime, and leave analysis"
)

START_DATE = "2025-04-01"
END_DATE = "2026-09-30"

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

try:
    con = duckdb.connect("pulseiq.duckdb", read_only=True)

    attendance_query = """
    SELECT
        d.department_name,
        strftime(a.period_end_date, '%Y-%m') AS month,
        SUM(a.scheduled_days) AS scheduled_days,
        SUM(a.present_days) AS present_days,
        SUM(a.late_arrivals) AS late_arrivals,
        SUM(a.overtime_hours) AS overtime_hours
    FROM warehouse.fact_attendance_monthly a
    JOIN warehouse.dim_department d
        ON a.department_id = d.department_id
    WHERE a.period_end_date BETWEEN DATE '2025-04-01'
                                AND DATE '2026-09-30'
    GROUP BY d.department_name, month
    ORDER BY month, d.department_name
    """
    attendance = con.execute(attendance_query).fetchdf()

    leave_query = """
    SELECT
        COALESCE(lt.leave_type_name, 'Unknown') AS leave_type,
        COALESCE(d.department_name, 'Unknown') AS department_name,
        l.status,
        SUM(l.days) AS leave_days,
        COUNT(*) AS requests,
        strftime(l.start_date, '%Y-%m') AS month
    FROM warehouse.fact_leave l
    LEFT JOIN warehouse.dim_leave_type lt
        ON l.leave_type_code = lt.leave_type_code
    LEFT JOIN warehouse.dim_employee e
        ON l.employee_key = e.employee_key
    LEFT JOIN warehouse.dim_department d
        ON e.department_id = d.department_id
    WHERE l.start_date BETWEEN DATE '2025-04-01'
                           AND DATE '2026-09-30'
    GROUP BY leave_type, department_name, l.status, month
    ORDER BY month
    """
    leave = con.execute(leave_query).fetchdf()

    calendar_query = """
    SELECT
        date,
        strftime(date, '%Y-%m') AS month,
        is_holiday,
        is_weekend,
        is_working_day
    FROM warehouse.dim_date
    WHERE date BETWEEN DATE '2025-03-28'
                   AND DATE '2026-10-03'
    ORDER BY date
    """
    calendar = con.execute(calendar_query).fetchdf()
    con.close()

except Exception as e:
    st.error(f"Unable to load dashboard data: {e}")
    st.stop()

if attendance.empty:
    st.error("No attendance records found for the selected period.")
    st.stop()

# FIX 1: DuckDB SUM() gives Decimal numbers. Charts need normal floats.
for col in ["scheduled_days", "present_days", "late_arrivals", "overtime_hours"]:
    attendance[col] = attendance[col].astype(float)

for col in ["leave_days", "requests"]:
    leave[col] = leave[col].astype(float)

# --------------------------------------------------
# 2. CALENDAR AND LONG-WEEKEND CALCULATION
# --------------------------------------------------

calendar["date"] = pd.to_datetime(calendar["date"])

calendar["is_nonworking"] = (
    calendar["is_holiday"].eq("Y")
    | calendar["is_weekend"].eq("Y")
)

# A new run starts when non-working status changes
# OR the dates are not consecutive.
date_gap = calendar["date"].diff().dt.days.ne(1)

calendar["run_id"] = (
    calendar["is_nonworking"].ne(calendar["is_nonworking"].shift())
    | date_gap
).cumsum()

calendar["run_length"] = (
    calendar.groupby("run_id")["date"].transform("size")
)

calendar["is_long_weekend"] = (
    calendar["is_nonworking"] & (calendar["run_length"] >= 3)
)

calendar_display = calendar[
    calendar["date"].between(
        pd.Timestamp(START_DATE), pd.Timestamp(END_DATE)
    )
].copy()

calendar_summary = (
    calendar_display.groupby("month", as_index=False)
    .agg(
        holidays=("is_holiday", lambda x: int(x.eq("Y").sum())),
        weekend_days=("is_weekend", lambda x: int(x.eq("Y").sum())),
        working_days=("is_working_day", lambda x: int(x.eq("Y").sum())),
        long_weekend_days=("is_long_weekend", lambda x: int(x.sum()))
    )
)

# --------------------------------------------------
# 3. FILTERS
# --------------------------------------------------

departments = sorted(attendance["department_name"].dropna().unique())
months = sorted(attendance["month"].dropna().unique())

st.sidebar.header("Dashboard Filters")

selected_departments = st.sidebar.multiselect(
    "Department",
    departments,
    default=departments
)

selected_months = st.sidebar.select_slider(
    "Month range",
    options=months,
    value=(months[0], months[-1])
)

filtered = attendance[
    attendance["department_name"].isin(selected_departments)
    & attendance["month"].between(selected_months[0], selected_months[1])
].copy()

filtered_leave = leave[
    leave["department_name"].isin(selected_departments)
    & leave["month"].between(selected_months[0], selected_months[1])
].copy()

calendar_filtered = calendar_summary[
    calendar_summary["month"].between(selected_months[0], selected_months[1])
].copy()

if filtered.empty:
    st.warning("No attendance records match the selected filters.")
    st.stop()

# --------------------------------------------------
# 4. KPI CARDS
# --------------------------------------------------

scheduled = filtered["scheduled_days"].sum()
present = filtered["present_days"].sum()
overall_rate = 100 * present / scheduled if scheduled > 0 else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Attendance Rate", f"{overall_rate:.2f}%")
c2.metric("Scheduled Days", f"{scheduled:,.0f}")
c3.metric("Late Arrivals", f"{filtered['late_arrivals'].sum():,.0f}")
c4.metric("Overtime Hours", f"{filtered['overtime_hours'].sum():,.1f}")

# --------------------------------------------------
# 5. MONTHLY TABLE (RATES, NOT ONLY COUNTS)
# --------------------------------------------------

monthly = (
    filtered.groupby("month", as_index=False)
    .agg(
        scheduled_days=("scheduled_days", "sum"),
        present_days=("present_days", "sum"),
        late_arrivals=("late_arrivals", "sum"),
        overtime_hours=("overtime_hours", "sum")
    )
)

nan = float("nan")

# Attendance rate = present days / scheduled days
monthly["attendance_rate"] = (
    100 * monthly["present_days"] / monthly["scheduled_days"].replace(0, nan)
)
# Late rate = late arrivals per 100 present days (fair comparison)
monthly["late_rate"] = (
    100 * monthly["late_arrivals"] / monthly["present_days"].replace(0, nan)
)
# Overtime per scheduled day (fair comparison)
monthly["ot_per_day"] = (
    monthly["overtime_hours"] / monthly["scheduled_days"].replace(0, nan)
)

# Add calendar info so holidays and long weekends can be marked
monthly = monthly.merge(calendar_filtered, on="month", how="left")
monthly[["holidays", "long_weekend_days"]] = (
    monthly[["holidays", "long_weekend_days"]].fillna(0)
)
monthly["marked"] = (
    (monthly["holidays"] > 0) | (monthly["long_weekend_days"] > 0)
)

# --------------------------------------------------
# 6. MONTHLY ATTENDANCE TREND (WITH HOLIDAY MARKERS)
# --------------------------------------------------

st.header("1. Monthly Attendance Trend")

base = alt.Chart(monthly).encode(
    x=alt.X("month:O", title="Month")
)

line = base.mark_line(point=True).encode(
    y=alt.Y(
        "attendance_rate:Q",
        # FIX 2: zoom the axis so small dips are visible
        scale=alt.Scale(zero=False),
        title="Attendance Rate (%)"
    ),
    tooltip=[
        "month",
        alt.Tooltip("attendance_rate:Q", format=".2f"),
        "holidays",
        "long_weekend_days"
    ]
)

# FIX 3: red diamonds on months with holidays or long weekends
marks = (
    base.transform_filter("datum.marked")
    .mark_point(color="red", shape="diamond", size=160)
    .encode(y=alt.Y("attendance_rate:Q", scale=alt.Scale(zero=False)))
)

st.altair_chart(line + marks, width='stretch')

st.caption(
    "Attendance rate = total present days / total scheduled days. "
    "Red diamonds = months with a holiday or a long weekend. "
    "Check these first before reporting a dip."
)

# --------------------------------------------------
# 7. HEATMAP: MONTH x DEPARTMENT
# --------------------------------------------------

st.subheader("Attendance Rate Heatmap (Month x Department)")

heat = filtered.copy()
heat["attendance_rate"] = (
    100 * heat["present_days"] / heat["scheduled_days"].replace(0, nan)
)

heatmap = alt.Chart(heat).mark_rect().encode(
    x=alt.X("month:O", title="Month"),
    y=alt.Y("department_name:N", title="Department"),
    color=alt.Color(
        "attendance_rate:Q",
        scale=alt.Scale(scheme="redyellowgreen", zero=False),
        title="Attendance %"
    ),
    tooltip=[
        "department_name",
        "month",
        alt.Tooltip("attendance_rate:Q", format=".2f")
    ]
)

st.altair_chart(heatmap, width='stretch')
st.caption("Red = lower attendance, green = higher attendance.")

# --------------------------------------------------
# 8. CALENDAR CONTEXT + DENOMINATOR CHECK
# --------------------------------------------------

st.subheader("Calendar Context")

st.dataframe(
    calendar_filtered,
    width='stretch',
    hide_index=True
)

st.caption(
    "Long-weekend days are non-working days belonging to a run "
    "of three or more consecutive non-working dates. "
    "Calendar information provides context and does not prove causation."
)

with st.expander("Check: is the denominator based on working days?"):
    check = monthly[["month", "scheduled_days", "working_days"]].copy()
    check["scheduled_per_working_day"] = (
        check["scheduled_days"] / check["working_days"].replace(0, nan)
    )
    st.dataframe(check, width='stretch', hide_index=True)
    st.caption(
        "scheduled_per_working_day is about the number of employees. "
        "It should stay similar every month. If it jumps in months with "
        "holidays, scheduled_days may include non-working days."
    )

# --------------------------------------------------
# 9. LATE ARRIVALS AND OVERTIME
# --------------------------------------------------

st.header("2. Late Arrivals and Overtime")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Late Arrivals per 100 Present Days")
    late_chart = alt.Chart(monthly).mark_bar().encode(
        x=alt.X("month:O", title="Month"),
        y=alt.Y("late_rate:Q", title="Late arrivals per 100 present days"),
        tooltip=[
            "month",
            "late_arrivals",
            alt.Tooltip("late_rate:Q", format=".2f")
        ]
    )
    st.altair_chart(late_chart, width='stretch')

with col2:
    st.subheader("Overtime Hours by Month")
    ot_chart = alt.Chart(monthly).mark_bar().encode(
        x=alt.X("month:O", title="Month"),
        y=alt.Y("overtime_hours:Q", title="Overtime hours"),
        tooltip=[
            "month",
            alt.Tooltip("overtime_hours:Q", format=".1f"),
            alt.Tooltip("ot_per_day:Q", format=".3f")
        ]
    )
    st.altair_chart(ot_chart, width='stretch')

st.caption(
    "Late arrivals are shown as a rate (per 100 present days), "
    "not a raw count, so months are compared fairly."
)

# --------------------------------------------------
# 10. LEAVE TRENDS
# --------------------------------------------------

st.header("3. Leave Trends")

if not filtered_leave.empty:

    approved = filtered_leave[
        filtered_leave["status"].astype(str).str.lower().eq("approved")
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Approved Leave Days by Type")
        if not approved.empty:
            by_type = (
                approved.groupby("leave_type", as_index=False)["leave_days"].sum()
            )
            st.altair_chart(
                alt.Chart(by_type).mark_bar().encode(
                    x=alt.X("leave_days:Q", title="Leave days"),
                    y=alt.Y("leave_type:N", sort="-x", title="Leave type"),
                    tooltip=["leave_type", "leave_days"]
                ),
                width='stretch'
            )
        else:
            st.info("No approved leave records for this selection.")

    with col2:
        st.subheader("Approved Leave Days by Department")
        if not approved.empty:
            by_dept = (
                approved.groupby("department_name", as_index=False)["leave_days"].sum()
            )
            st.altair_chart(
                alt.Chart(by_dept).mark_bar().encode(
                    x=alt.X("leave_days:Q", title="Leave days"),
                    y=alt.Y("department_name:N", sort="-x", title="Department"),
                    tooltip=["department_name", "leave_days"]
                ),
                width='stretch'
            )
        else:
            st.info("No approved leave records for this selection.")

    st.subheader("Leave Requests by Status")

    status_summary = (
        filtered_leave.groupby("status", as_index=False)
        .agg(
            requests=("requests", "sum"),
            leave_days=("leave_days", "sum")
        )
    )
    st.dataframe(status_summary, width='stretch', hide_index=True)

else:
    st.info("No leave records match the selected filters.")

# --------------------------------------------------
# 11. UNUSUAL MONTHS (FOUND AUTOMATICALLY)
# --------------------------------------------------

st.header("4. Unusual Months")

if len(monthly) >= 4:
    z = pd.DataFrame({"month": monthly["month"]})
    for metric in ["attendance_rate", "late_rate", "ot_per_day"]:
        std = monthly[metric].std()
        z[metric] = (
            (monthly[metric] - monthly[metric].mean()) / std
            if std and std > 0 else 0.0
        )

    # Largest distance from normal, in any of the 3 metrics
    z["score"] = z[["attendance_rate", "late_rate", "ot_per_day"]].abs().max(axis=1)
    top3 = z.sort_values("score", ascending=False).head(3)["month"].tolist()

    def what_stood_out(month):
        row = z[z["month"] == month].iloc[0]
        metric = row[["attendance_rate", "late_rate", "ot_per_day"]].abs().idxmax()
        direction = "high" if row[metric] > 0 else "low"
        names = {
            "attendance_rate": "attendance rate",
            "late_rate": "late-arrival rate",
            "ot_per_day": "overtime per day"
        }
        return f"{names[metric]} is unusually {direction}"

    unusual = monthly[monthly["month"].isin(top3)][[
        "month", "attendance_rate", "late_rate", "ot_per_day",
        "holidays", "long_weekend_days"
    ]].copy()
    unusual["what_stood_out"] = unusual["month"].apply(what_stood_out)

    st.dataframe(unusual, width='stretch', hide_index=True)
    st.caption(
        "These months are far from the average (measured in standard "
        "deviations). Look at holidays and long weekends in the same row "
        "first. Then write your own possible cause for each month. "
        "The data shows context, not proof."
    )
else:
    st.info("Select at least 4 months to detect unusual months.")

# --------------------------------------------------
# 12. KEY NUMERICAL INSIGHTS
# --------------------------------------------------

st.header("5. Key Numerical Insights")

highest_row = monthly.loc[monthly["attendance_rate"].idxmax()]
lowest_row = monthly.loc[monthly["attendance_rate"].idxmin()]
late_row = monthly.loc[monthly["late_rate"].idxmax()]
overtime_row = monthly.loc[monthly["overtime_hours"].idxmax()]
typical_ot = monthly["overtime_hours"].median()

st.markdown(
    f"- **Highest attendance:** {highest_row['month']} - "
    f"{highest_row['attendance_rate']:.2f}%."
)
st.markdown(
    f"- **Lowest attendance:** {lowest_row['month']} - "
    f"{lowest_row['attendance_rate']:.2f}% "
    f"(gap from highest: "
    f"{highest_row['attendance_rate'] - lowest_row['attendance_rate']:.2f} points)."
)
st.markdown(
    f"- **Highest late-arrival rate:** {late_row['month']} - "
    f"{late_row['late_rate']:.2f} per 100 present days "
    f"({late_row['late_arrivals']:,.0f} late arrivals)."
)
st.markdown(
    f"- **Highest overtime:** {overtime_row['month']} - "
    f"{overtime_row['overtime_hours']:,.1f} hours, "
    f"{100 * (overtime_row['overtime_hours'] / typical_ot - 1):.0f}% "
    f"above the typical month ({typical_ot:,.1f} hours)."
)

# --------------------------------------------------
# 13. DEPARTMENT VIEW
# --------------------------------------------------

st.subheader("Attendance by Department")

dept_totals = (
    filtered.groupby("department_name", as_index=False)
    .agg(
        scheduled_days=("scheduled_days", "sum"),
        present_days=("present_days", "sum")
    )
)
dept_totals["attendance_rate"] = (
    100 * dept_totals["present_days"]
    / dept_totals["scheduled_days"].replace(0, nan)
)

st.dataframe(
    dept_totals.sort_values("attendance_rate"),
    width='stretch',
    hide_index=True
)

# Which department changed most in the lowest month?
# (compared with its OWN normal, not with other departments)
st.subheader(f"Who changed most in the lowest month ({lowest_row['month']})?")

dept_month = filtered.copy()
dept_month["rate"] = (
    100 * dept_month["present_days"] / dept_month["scheduled_days"].replace(0, nan)
)
own_normal = dept_month.groupby("department_name")["rate"].mean().rename("own_average")
low_month = (
    dept_month[dept_month["month"] == lowest_row["month"]]
    .set_index("department_name")["rate"]
    .rename("rate_in_low_month")
)
change = pd.concat([own_normal, low_month], axis=1).dropna().reset_index()
change["change_points"] = change["rate_in_low_month"] - change["own_average"]

st.dataframe(
    change.sort_values("change_points"),
    width='stretch',
    hide_index=True
)
st.caption(
    "A big department moves the company average most. A small department "
    "can have the biggest drop. Compare each department with its own "
    "average to see who really changed."
)

# --------------------------------------------------
# 14. DATA TABLES
# --------------------------------------------------

with st.expander("View filtered attendance records"):
    st.dataframe(filtered, width='stretch', hide_index=True)

with st.expander("View filtered leave records"):
    st.dataframe(filtered_leave, width='stretch', hide_index=True)