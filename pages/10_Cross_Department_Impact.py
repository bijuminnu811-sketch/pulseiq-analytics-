import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Task 13 - Cross Department Impact",
    page_icon="📊",
    layout="wide"
)

st.title("Cross-Department Impact View")
st.caption("Task 13 | Department × Month analysis")


# =========================================================
# FILE PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXCEL_FILE = PROJECT_ROOT / "03_Data" / "PulseIQ_Dataset.xlsx"


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    headcount = pd.read_excel(
        EXCEL_FILE,
        sheet_name="fact_headcount_monthly"
    )

    payroll = pd.read_excel(
        EXCEL_FILE,
        sheet_name="fact_payroll"
    )

    attendance = pd.read_excel(
        EXCEL_FILE,
        sheet_name="fact_attendance_monthly"
    )

    leave = pd.read_excel(
        EXCEL_FILE,
        sheet_name="fact_leave"
    )

    employee = pd.read_excel(
        EXCEL_FILE,
        sheet_name="dim_employee"
    )

    department = pd.read_excel(
        EXCEL_FILE,
        sheet_name="dim_department"
    )

    return (
        headcount,
        payroll,
        attendance,
        leave,
        employee,
        department
    )


try:
    (
        headcount,
        payroll,
        attendance,
        leave,
        employee,
        department
    ) = load_data()

except Exception as e:

    st.error(f"Could not load Task 13 data: {e}")
    st.stop()


# =========================================================
# CLEAN DATES
# =========================================================

headcount["month"] = pd.to_datetime(
    headcount["month_start_date"],
    errors="coerce"
).dt.to_period("M").astype(str)

payroll["month"] = pd.to_datetime(
    payroll["period_end_date"],
    errors="coerce"
).dt.to_period("M").astype(str)

attendance["month"] = pd.to_datetime(
    attendance["period_end_date"],
    errors="coerce"
).dt.to_period("M").astype(str)

leave["month"] = pd.to_datetime(
    leave["start_date"],
    errors="coerce"
).dt.to_period("M").astype(str)


# =========================================================
# 1. HEADCOUNT AGGREGATION
# Grain: Department × Month
# =========================================================

hc = (
    headcount
    .groupby(["department_id", "month"], as_index=False)
    .agg(
        headcount_start=("headcount_start", "max"),
        hires=("hires", "sum"),
        exits=("exits", "sum"),
        voluntary_exits=("voluntary_exits", "sum"),
        transfers_in=("transfers_in", "sum"),
        transfers_out=("transfers_out", "sum"),
        headcount_end=("headcount_end", "max"),
        attrition_rate_pct=("attrition_rate_monthly_pct", "max")
    )
)


# =========================================================
# 2. PAYROLL AGGREGATION
# Grain: Department × Month
# =========================================================

pay = (
    payroll
    .groupby(["department_id", "month"], as_index=False)
    .agg(
        payroll_gross=("gross_pay", "sum"),
        employer_cost=("employer_cost", "sum"),
        overtime_hours_paid=("overtime_hours_paid", "sum"),
        overtime_pay=("overtime_pay", "sum"),
        payroll_headcount=("headcount_flag", "sum")
    )
)


# =========================================================
# 3. ATTENDANCE AGGREGATION
# Grain: Department × Month
# =========================================================

att = (
    attendance
    .groupby(["department_id", "month"], as_index=False)
    .agg(
        scheduled_days=("scheduled_days", "sum"),
        present_days=("present_days", "sum"),
        paid_leave_days_attendance=("paid_leave_days", "sum"),
        unpaid_absence_days=("unpaid_absence_days", "sum"),
        attendance_overtime_hours=("overtime_hours", "sum")
    )
)

att["attendance_rate_pct"] = np.where(
    att["scheduled_days"] > 0,
    att["present_days"] / att["scheduled_days"] * 100,
    np.nan
)


# =========================================================
# 4. LEAVE AGGREGATION
#
# Leave has employee-level data, so first attach
# employee -> department.
#
# Only APPROVED leave is counted.
# =========================================================

employee_dept = (
    employee[
        ["employee_id", "department_id"]
    ]
    .drop_duplicates("employee_id")
)

leave = leave.merge(
    employee_dept,
    on="employee_id",
    how="left"
)

leave_approved = leave[
    leave["status"].astype(str).str.upper().eq("APPROVED")
].copy()

lv = (
    leave_approved
    .groupby(["department_id", "month"], as_index=False)
    .agg(
        approved_leave_days=("days", "sum"),
        approved_leave_requests=("leave_request_id", "nunique")
    )
)


# =========================================================
# 5. COMBINE ONLY AFTER EACH SOURCE IS AGGREGATED
# =========================================================

final = hc.merge(
    pay,
    on=["department_id", "month"],
    how="outer"
)

final = final.merge(
    att,
    on=["department_id", "month"],
    how="outer"
)

final = final.merge(
    lv,
    on=["department_id", "month"],
    how="outer"
)


# =========================================================
# DEPARTMENT NAME
# =========================================================

dept_lookup = department[
    ["department_id", "department_name"]
].drop_duplicates("department_id")

final = final.merge(
    dept_lookup,
    on="department_id",
    how="left"
)


# =========================================================
# CALCULATED METRICS
# =========================================================

final["avg_headcount"] = (
    final["headcount_start"].fillna(0)
    + final["headcount_end"].fillna(0)
) / 2


final["overtime_cost_pct"] = np.where(
    final["payroll_gross"].fillna(0) > 0,
    final["overtime_pay"].fillna(0)
    / final["payroll_gross"].fillna(0)
    * 100,
    0
)


final["overtime_hours_per_employee"] = np.where(
    final["avg_headcount"] > 0,
    final["overtime_hours_paid"].fillna(0)
    / final["avg_headcount"],
    0
)


final["leave_days_per_employee"] = np.where(
    final["avg_headcount"] > 0,
    final["approved_leave_days"].fillna(0)
    / final["avg_headcount"],
    0
)


final["employer_cost_per_employee"] = np.where(
    final["avg_headcount"] > 0,
    final["employer_cost"].fillna(0)
    / final["avg_headcount"],
    0
)


# =========================================================
# CLEAN NUMERIC COLUMNS
# =========================================================

numeric_columns = [
    "headcount_start",
    "hires",
    "exits",
    "voluntary_exits",
    "transfers_in",
    "transfers_out",
    "headcount_end",
    "attrition_rate_pct",
    "payroll_gross",
    "employer_cost",
    "overtime_hours_paid",
    "overtime_pay",
    "payroll_headcount",
    "scheduled_days",
    "present_days",
    "paid_leave_days_attendance",
    "unpaid_absence_days",
    "attendance_overtime_hours",
    "attendance_rate_pct",
    "approved_leave_days",
    "approved_leave_requests",
    "avg_headcount",
    "overtime_cost_pct",
    "overtime_hours_per_employee",
    "leave_days_per_employee",
    "employer_cost_per_employee"
]

for col in numeric_columns:
    if col in final.columns:
        final[col] = pd.to_numeric(
            final[col],
            errors="coerce"
        ).fillna(0)


# =========================================================
# SORT
# =========================================================

final = final.sort_values(
    ["month", "department_name"]
).reset_index(drop=True)


# =========================================================
# VALIDATION
# =========================================================

duplicate_count = (
    final.groupby(["department_id", "month"])
    .size()
    .gt(1)
    .sum()
)

st.subheader("Data Quality Validation")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Department-Month Rows",
    f"{len(final):,}"
)

c2.metric(
    "Duplicate Dept-Month Groups",
    f"{duplicate_count:,}"
)

c3.metric(
    "Departments",
    f"{final['department_id'].nunique():,}"
)

if duplicate_count == 0:
    st.success(
        "✓ No duplicate department-month groups after aggregation."
    )
else:
    st.error(
        "Duplicate department-month groups detected."
    )


# =========================================================
# FILTERS
# =========================================================

st.subheader("Department Comparison")

col1, col2 = st.columns(2)

with col1:
    departments = sorted(
        final["department_name"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_departments = st.multiselect(
        "Department",
        departments,
        default=departments
    )

with col2:
    months = sorted(
        final["month"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_months = st.multiselect(
        "Month",
        months,
        default=months[-12:] if len(months) > 12 else months
    )


filtered = final[
    final["department_name"].isin(selected_departments)
    & final["month"].isin(selected_months)
].copy()


# =========================================================
# KPI CARDS
# =========================================================

st.subheader("Key Workforce & Cost Metrics")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    "Employer Cost",
    f"₹{filtered['employer_cost'].sum():,.0f}"
)

k2.metric(
    "Overtime Pay",
    f"₹{filtered['overtime_pay'].sum():,.0f}"
)

k3.metric(
    "Overtime Hours",
    f"{filtered['overtime_hours_paid'].sum():,.0f}"
)

k4.metric(
    "Approved Leave Days",
    f"{filtered['approved_leave_days'].sum():,.0f}"
)

k5.metric(
    "Exits",
    f"{filtered['exits'].sum():,.0f}"
)


# =========================================================
# TABLE
# =========================================================

st.subheader("Department × Month Analytical Table")

display_columns = [
    "month",
    "department_name",
    "headcount_start",
    "hires",
    "exits",
    "voluntary_exits",
    "headcount_end",
    "attrition_rate_pct",
    "employer_cost",
    "overtime_hours_paid",
    "overtime_pay",
    "overtime_cost_pct",
    "attendance_rate_pct",
    "approved_leave_days",
    "leave_days_per_employee",
    "overtime_hours_per_employee"
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DEPARTMENT SUMMARY
# =========================================================

st.subheader("Department-Level Summary")

dept_summary = (
    filtered
    .groupby("department_name", as_index=False)
    .agg(
        employer_cost=("employer_cost", "sum"),
        overtime_pay=("overtime_pay", "sum"),
        overtime_hours=("overtime_hours_paid", "sum"),
        exits=("exits", "sum"),
        voluntary_exits=("voluntary_exits", "sum"),
        leave_days=("approved_leave_days", "sum"),
        avg_headcount=("avg_headcount", "mean")
    )
)

dept_summary["overtime_cost_pct"] = np.where(
    dept_summary["employer_cost"] > 0,
    dept_summary["overtime_pay"]
    / dept_summary["employer_cost"] * 100,
    0
)

dept_summary["overtime_hours_per_employee"] = np.where(
    dept_summary["avg_headcount"] > 0,
    dept_summary["overtime_hours"]
    / dept_summary["avg_headcount"],
    0
)

st.dataframe(
    dept_summary.sort_values(
        "overtime_pay",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)


# =========================================================
# CHARTS
# =========================================================

st.subheader("Overtime Cost by Department")

overtime_chart = (
    dept_summary
    .sort_values("overtime_pay", ascending=False)
    .set_index("department_name")[
        ["overtime_pay"]
    ]
)

st.bar_chart(overtime_chart)


st.subheader("Employer Cost by Department")

cost_chart = (
    dept_summary
    .sort_values("employer_cost", ascending=False)
    .set_index("department_name")[
        ["employer_cost"]
    ]
)

st.bar_chart(cost_chart)


st.subheader("Attrition vs Overtime")

relationship = (
    filtered
    .groupby("department_name", as_index=False)
    .agg(
        attrition_rate_pct=("attrition_rate_pct", "mean"),
        overtime_hours_per_employee=(
            "overtime_hours_per_employee",
            "mean"
        ),
        overtime_pay=("overtime_pay", "sum")
    )
)

st.dataframe(
    relationship.sort_values(
        "attrition_rate_pct",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)


# =========================================================
# BUSINESS INTERPRETATION
# =========================================================

st.subheader("Business Findings")

if len(dept_summary) > 0:

    highest_ot = dept_summary.loc[
        dept_summary["overtime_pay"].idxmax()
    ]

    highest_cost = dept_summary.loc[
        dept_summary["employer_cost"].idxmax()
    ]

    st.write(
        f"**Highest overtime cost:** "
        f"{highest_ot['department_name']} "
        f"with ₹{highest_ot['overtime_pay']:,.0f}."
    )

    st.write(
        f"**Highest employer cost:** "
        f"{highest_cost['department_name']} "
        f"with ₹{highest_cost['employer_cost']:,.0f}."
    )

st.info(
    "High overtime and high attrition occurring in the same department "
    "does not prove that overtime causes attrition. Both may be associated "
    "with a third factor such as workload, staffing shortages, seasonal demand, "
    "project deadlines, or management practices. The dashboard therefore "
    "shows association and comparison rather than causal impact."
)


# =========================================================
# REFERENCE VALIDATION
# =========================================================

st.subheader("Reference Reconciliation")

st.warning(
    "Task 13 reference_summary_dept_month and unlock_PQ-13 "
    "were not found in the current project files. "
    "Reference reconciliation cannot be claimed until those "
    "validation materials are provided."
)


# =========================================================
# DOWNLOAD
# =========================================================

csv_data = final.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Task 13 Department-Month Table",
    data=csv_data,
    file_name="Task13_Cross_Department_Impact.csv",
    mime="text/csv"
)