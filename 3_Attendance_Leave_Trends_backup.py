import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(page_title="Attendance & Leave", layout="wide")

st.title("PulseIQ | Attendance & Leave Trends")
st.caption("Workforce attendance, punctuality, overtime, and leave analysis")

con = duckdb.connect("pulseiq.duckdb", read_only=True)

attendance_query = """
SELECT
    d.department_name,
    strftime(a.period_end_date, '%Y-%m') AS month,
    SUM(a.scheduled_days) AS scheduled_days,
    SUM(a.present_days) AS present_days,
    SUM(a.late_arrivals) AS late_arrivals,
    SUM(a.overtime_hours) AS overtime_hours,
    ROUND(
        100.0 * SUM(a.present_days) /
        NULLIF(SUM(a.scheduled_days), 0), 2
    ) AS attendance_rate
FROM warehouse.fact_attendance_monthly a
JOIN warehouse.dim_department d
    ON a.department_id = d.department_id
WHERE a.period_end_date BETWEEN DATE '2025-04-01'
                            AND DATE '2026-09-30'
GROUP BY d.department_name, month
ORDER BY month
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
WHERE date BETWEEN DATE '2025-04-01' AND DATE '2026-09-30'
ORDER BY date
"""

calendar = con.execute(calendar_query).fetchdf()

calendar["date"] = pd.to_datetime(calendar["date"])

# Identify consecutive days that are holidays or weekends
calendar["is_nonworking"] = (
    (calendar["is_holiday"] == "Y")
    | (calendar["is_weekend"] == "Y")
)

calendar["run_id"] = (
    calendar["is_nonworking"]
    .ne(calendar["is_nonworking"].shift())
    .cumsum()
)

calendar["run_length"] = calendar.groupby("run_id")["date"].transform("size")

calendar["is_long_weekend"] = (
    calendar["is_nonworking"]
    & (calendar["run_length"] >= 3)
)

calendar_summary = (
    calendar.groupby("month", as_index=False)
    .agg(
        holidays=("is_holiday", lambda x: (x == "Y").sum()),
        weekend_days=("is_weekend", lambda x: (x == "Y").sum()),
        working_days=("is_working_day", lambda x: (x == "Y").sum()),
        long_weekend_days=("is_long_weekend", "sum")
    )
)

con.close()

if attendance.empty:
    st.error("No attendance records found for the selected period.")
    st.stop()

departments = sorted(attendance["department_name"].dropna().unique())
selected_departments = st.sidebar.multiselect(
    "Department",
    departments,
    default=departments
)

months = sorted(attendance["month"].dropna().unique())
selected_months = st.sidebar.select_slider(
    "Month range",
    options=months,
    value=(months[0], months[-1])
)

filtered = attendance[
    attendance["department_name"].isin(selected_departments)
    & attendance["month"].between(
        selected_months[0], selected_months[1]
    )
].copy()

filtered_leave = leave[
    leave["department_name"].isin(selected_departments)
    & leave["month"].between(
        selected_months[0], selected_months[1]
    )
].copy()

if filtered.empty:
    st.warning("No attendance records match these filters.")
    st.stop()

scheduled = filtered["scheduled_days"].sum()
present = filtered["present_days"].sum()
overall_rate = 100 * present / scheduled if scheduled else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Attendance Rate", f"{overall_rate:.2f}%")
c2.metric("Scheduled Days", f"{scheduled:,.0f}")
c3.metric("Late Arrivals", f"{filtered['late_arrivals'].sum():,.0f}")
c4.metric("Overtime Hours", f"{filtered['overtime_hours'].sum():,.1f}")

st.header("1. Monthly Attendance Trend")

monthly = (
    filtered.groupby("month", as_index=False)
    .agg(
        scheduled_days=("scheduled_days", "sum"),
        present_days=("present_days", "sum")
    )
)
monthly["attendance_rate"] = (
    100 * monthly["present_days"] / monthly["scheduled_days"]
)
st.line_chart(monthly.set_index("month")["attendance_rate"])

st.line_chart(monthly.set_index("month")["attendance_rate"])
st.subheader("Calendar Context: Holidays, Working Days and Long Weekends")

calendar_filtered = calendar_summary[
    calendar_summary["month"].between(
        selected_months[0], selected_months[1]
    )
].copy()

st.dataframe(
    calendar_filtered,
    use_container_width=True,
    hide_index=True
)

st.header("2. Late Arrivals and Overtime")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Late Arrivals by Month")
    late = filtered.groupby("month")["late_arrivals"].sum()
    st.bar_chart(late)

with col2:
    st.subheader("Overtime Hours by Month")
    overtime = filtered.groupby("month")["overtime_hours"].sum()
    st.bar_chart(overtime)

st.header("3. Leave Trends")

if not filtered_leave.empty:
    approved = filtered_leave[
        filtered_leave["status"].str.lower() == "approved"
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Approved Leave Days by Type")
        leave_type = approved.groupby("leave_type")["leave_days"].sum()
        st.bar_chart(leave_type)

    with col2:
        st.subheader("Approved Leave Days by Department")
        leave_dept = approved.groupby("department_name")["leave_days"].sum()
        st.bar_chart(leave_dept)

    st.subheader("Leave Requests by Status")
    status_summary = (
        filtered_leave.groupby("status", as_index=False)
        .agg(
            requests=("requests", "sum"),
            leave_days=("leave_days", "sum")
        )
    )
    st.dataframe(status_summary, use_container_width=True)
else:
    st.info("No leave records match the selected filters.")

st.header("4. Calendar Context")

calendar_filtered = calendar[
    calendar["month"].between(selected_months[0], selected_months[1])
]

st.caption(
    "Calendar information provides context; it does not prove that "
    "holidays or weekends caused attendance changes."
)
st.dataframe(calendar_filtered, use_container_width=True)

st.header("5. Key Numerical Insights")

st.markdown("""
- **Highest attendance:** July 2025 — 95.35%.
- **Lowest attendance:** May 2026 — 92.64%.
- **Highest late arrivals:** September 2026 — 618.
- **Department trend:** Finance & Accounts attendance declined from
  90.06% in March 2026 to 81.58% in June 2026.
""")

with st.expander("View filtered attendance records"):
    st.dataframe(filtered, use_container_width=True)

with st.expander("View filtered leave records"):
    st.dataframe(filtered_leave, use_container_width=True)