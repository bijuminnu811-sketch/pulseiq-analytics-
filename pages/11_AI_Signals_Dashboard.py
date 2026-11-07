import duckdb
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PULSEIQ - TASK 14: AI SIGNALS DASHBOARD
# ============================================================

st.set_page_config(
    page_title="PulseIQ - AI Signals",
    page_icon="🤖",
    layout="wide",
)

DB_PATH = "pulseiq.duckdb"


# ------------------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------------------

@st.cache_resource
def get_connection():
    return duckdb.connect(DB_PATH, read_only=True)


con = get_connection()


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def run_query(query):
    return con.sql(query).df()


def money_format(value):
    if pd.isna(value):
        return "₹0"
    return f"₹{value:,.0f}"


def show_df(df):
    """Show a table. Works on newer and older Streamlit versions."""
    try:
        st.dataframe(df, width="stretch")
    except TypeError:
        st.dataframe(df, use_container_width=True)


def show_plot(fig):
    """Show a Plotly chart. Works on newer and older Streamlit versions."""
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------------
# TITLE
# ------------------------------------------------------------

st.title("🤖 AI Signals Dashboard")
st.caption(
    "PulseIQ | Predictive signals, anomaly detection and forecast monitoring"
)

st.info(
    "⚠️ AI-generated, for human review — these signals support decision-making "
    "and should not be treated as guarantees."
)


# ============================================================
# LOAD DATA
# ============================================================

anomaly = run_query("""
    SELECT
        result_id,
        source_dataset,
        record_id,
        employee_id,
        period,
        anomaly_score,
        flagged,
        reason_code,
        reason_text,
        money_at_risk,
        model_version,
        scored_at
    FROM warehouse.fact_anomaly
""")

forecast = run_query("""
    SELECT
        forecast_id,
        metric,
        department_id,
        forecast_month,
        forecast_value,
        lower_80,
        upper_80,
        method,
        trained_through,
        model_version
    FROM warehouse.fact_forecast
""")

attrition = run_query("""
    SELECT
        prediction_id,
        employee_id,
        department_id,
        as_of_date,
        risk_score_12m,
        risk_band,
        top_reason_1,
        top_reason_2,
        top_reason_3,
        model_version,
        model_note
    FROM warehouse.fact_attrition_risk
""")

actuals = run_query("""
    SELECT
        month_start_date,
        department_id,
        headcount_end,
        attrition_rate_monthly_pct
    FROM warehouse.fact_headcount_monthly
""")

# ------------------------------------------------------------
# CLEAN DATA TYPES
# ------------------------------------------------------------

# A blank department in the forecast feed means a company-wide forecast.
forecast["department_id"] = forecast["department_id"].fillna("ALL").astype(str)
actuals["department_id"] = actuals["department_id"].astype(str)

for col in ["forecast_value", "lower_80", "upper_80"]:
    forecast[col] = pd.to_numeric(forecast[col], errors="coerce")

actuals["headcount_end"] = pd.to_numeric(
    actuals["headcount_end"], errors="coerce"
)
actuals["attrition_rate_monthly_pct"] = pd.to_numeric(
    actuals["attrition_rate_monthly_pct"], errors="coerce"
)


# ============================================================
# OVERVIEW
# ============================================================

st.header("1. AI Signals Overview")

# "flagged" may be stored as Y/N, True/False or 1/0.
flagged_mask = (
    anomaly["flagged"]
    .astype(str)
    .str.strip()
    .str.upper()
    .isin(["Y", "YES", "TRUE", "1"])
)
flagged_anomalies = anomaly[flagged_mask]

money_at_risk = pd.to_numeric(
    flagged_anomalies["money_at_risk"],
    errors="coerce"
).fillna(0).sum()

high_risk_mask = (
    attrition["risk_band"]
    .astype(str)
    .str.strip()
    .str.upper()
    .isin(["HIGH", "VERY HIGH", "VERY_HIGH", "CRITICAL"])
)
high_risk = attrition[high_risk_mask]

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Flagged anomalies", f"{len(flagged_anomalies):,}")

with c2:
    st.metric("Money at risk", money_format(money_at_risk))

with c3:
    st.metric("High-risk employees", f"{len(high_risk):,}")

with c4:
    st.metric("Forecast records", f"{len(forecast):,}")


# ============================================================
# ANOMALY ANALYSIS
# ============================================================

st.header("2. Anomaly Signals")

st.write(
    "These records identify unusual observations from the existing anomaly "
    "detection output. Money at risk is shown where the source feed provides it."
)

if len(flagged_anomalies) > 0:

    anomaly_money = flagged_anomalies.copy()

    anomaly_money["money_at_risk"] = pd.to_numeric(
        anomaly_money["money_at_risk"],
        errors="coerce"
    ).fillna(0)

    anomaly_money = anomaly_money.sort_values(
        "money_at_risk",
        ascending=False
    )

    st.subheader("Top anomalies by money at risk")

    show_df(
        anomaly_money[
            [
                "period",
                "source_dataset",
                "employee_id",
                "reason_code",
                "reason_text",
                "anomaly_score",
                "money_at_risk",
            ]
        ].head(20)
    )

    st.caption(
        "Ranking is based on the existing money_at_risk value, descending. "
        "Attendance anomalies may have no monetary value in the source feed."
    )

    chart_data = (
        anomaly_money
        .groupby("reason_code", as_index=False)["money_at_risk"]
        .sum()
        .sort_values("money_at_risk", ascending=False)
        .head(10)
    )

    fig = px.bar(
        chart_data,
        x="money_at_risk",
        y="reason_code",
        orientation="h",
        title="Financial impact by anomaly type",
        labels={
            "money_at_risk": "Money at risk",
            "reason_code": "Anomaly type",
        },
    )

    show_plot(fig)

    st.caption(
        "AI-generated, for human review — this chart summarizes the financial "
        "impact already recorded by the anomaly detection feed."
    )

else:
    st.warning("No flagged anomalies were found in the current data.")


# ============================================================
# FORECAST VS ACTUAL
# ============================================================

st.header("3. Forecast vs Actual")

st.write(
    "The forecast feed contains existing forecast values and an 80% interval. "
    "Actual values are taken from the monthly headcount fact table."
)

metric_options = sorted(
    forecast["metric"].dropna().unique().tolist()
)

if not metric_options:
    st.warning("The forecast feed has no metrics to display.")
    st.stop()

selected_metric = st.selectbox(
    "Select forecast metric",
    metric_options,
)

department_options = sorted(
    set(forecast["department_id"].unique().tolist()) | {"ALL"}
)
# Keep "ALL" first in the list.
department_options = ["ALL"] + [d for d in department_options if d != "ALL"]

selected_department = st.selectbox(
    "Select department",
    department_options,
)

forecast_view = forecast[
    (forecast["metric"] == selected_metric)
    &
    (forecast["department_id"] == selected_department)
].copy()

forecast_view["forecast_month"] = pd.to_datetime(
    forecast_view["forecast_month"]
)

# ------------------------------------------------------------
# Match actuals
# ------------------------------------------------------------

actual_view = actuals.copy()

actual_view["month_start_date"] = pd.to_datetime(
    actual_view["month_start_date"]
)

if selected_department == "ALL":
    actual_view = actual_view[actual_view["department_id"] == "ALL"]

    # If the actual table has no ALL department row,
    # calculate the company total from department records.
    if actual_view.empty:
        all_actuals = actuals.copy()
        all_actuals["month_start_date"] = pd.to_datetime(
            all_actuals["month_start_date"]
        )

        # Attrition rate is weighted by headcount so that large
        # departments count more than small ones.
        all_actuals["weighted_rate"] = (
            all_actuals["attrition_rate_monthly_pct"]
            * all_actuals["headcount_end"]
        )

        actual_view = (
            all_actuals
            .groupby("month_start_date", as_index=False)
            .agg(
                headcount_end=("headcount_end", "sum"),
                weighted_rate=("weighted_rate", "sum"),
            )
        )

        actual_view["attrition_rate_monthly_pct"] = np.where(
            actual_view["headcount_end"] > 0,
            actual_view["weighted_rate"] / actual_view["headcount_end"],
            np.nan,
        )
else:
    actual_view = actual_view[
        actual_view["department_id"] == selected_department
    ]


# ------------------------------------------------------------
# Prepare actual metric
# ------------------------------------------------------------

if selected_metric == "headcount_end":

    actual_metric = actual_view[
        ["month_start_date", "headcount_end"]
    ].copy()

    actual_metric = actual_metric.rename(
        columns={
            "month_start_date": "forecast_month",
            "headcount_end": "actual",
        }
    )

elif selected_metric == "attrition_rate_monthly_pct":

    actual_metric = actual_view[
        [
            "month_start_date",
            "attrition_rate_monthly_pct",
        ]
    ].copy()

    actual_metric = actual_metric.rename(
        columns={
            "month_start_date": "forecast_month",
            "attrition_rate_monthly_pct": "actual",
        }
    )

else:
    # No actuals available for this metric. Columns keep proper types
    # so the merge below does not fail.
    actual_metric = pd.DataFrame(
        {
            "forecast_month": pd.to_datetime([]),
            "actual": pd.Series(dtype="float"),
        }
    )

actual_metric["actual"] = pd.to_numeric(
    actual_metric["actual"], errors="coerce"
)

comparison = forecast_view.merge(
    actual_metric,
    on="forecast_month",
    how="left",
)

comparison["error"] = (
    comparison["actual"] - comparison["forecast_value"]
)

comparison["absolute_error"] = comparison["error"].abs()

# If the actual value is zero, a percentage error cannot be calculated,
# so it is left blank instead of becoming infinity.
safe_actual = comparison["actual"].abs().replace(0, np.nan)

comparison["error_pct"] = (
    comparison["absolute_error"] / safe_actual * 100
)

# A missing actual is left blank. It is not treated as zero.
comparison.loc[
    comparison["actual"].isna(),
    ["error", "absolute_error", "error_pct"]
] = np.nan


# ------------------------------------------------------------
# Forecast chart
# ------------------------------------------------------------

if not comparison.empty:

    comparison = comparison.sort_values("forecast_month")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=comparison["forecast_month"],
            y=comparison["upper_80"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=comparison["forecast_month"],
            y=comparison["lower_80"],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            name="80% forecast interval",
            hoverinfo="skip",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=comparison["forecast_month"],
            y=comparison["forecast_value"],
            mode="lines+markers",
            name="Forecast",
        )
    )

    actual_chart = comparison.dropna(subset=["actual"])

    if not actual_chart.empty:

        fig.add_trace(
            go.Scatter(
                x=actual_chart["forecast_month"],
                y=actual_chart["actual"],
                mode="lines+markers",
                name="Actual",
            )
        )

    fig.update_layout(
        title=f"{selected_metric} — Forecast vs Actual",
        xaxis_title="Month",
        yaxis_title=selected_metric,
        hovermode="x unified",
    )

    show_plot(fig)

    st.caption(
        "AI-generated, for human review — the shaded area represents the "
        "existing 80% forecast interval. It is not a guarantee of the actual outcome."
    )

    # --------------------------------------------------------
    # Error explanation
    # --------------------------------------------------------

    st.subheader("How forecast error is calculated")

    st.write("**Error = Actual − Forecast**")

    st.write(
        "**Absolute percentage error = "
        "|Actual − Forecast| ÷ |Actual| × 100**"
    )

    st.write(
        "When an actual value is unavailable, the error is left blank rather "
        "than treating the missing actual as zero. A missing actual is not the "
        "same as an actual value of zero. If the actual value is exactly zero, "
        "the percentage error is also left blank because it cannot be calculated."
    )

    # --------------------------------------------------------
    # Comparison table
    # --------------------------------------------------------

    st.subheader("Forecast comparison table")

    display_table = comparison[
        [
            "forecast_month",
            "department_id",
            "metric",
            "actual",
            "forecast_value",
            "lower_80",
            "upper_80",
            "error",
            "error_pct",
            "method",
        ]
    ].copy()

    display_table = display_table.rename(
        columns={
            "forecast_month": "Month",
            "department_id": "Department",
            "metric": "Metric",
            "actual": "Actual",
            "forecast_value": "Forecast",
            "lower_80": "Lower 80%",
            "upper_80": "Upper 80%",
            "error": "Error",
            "error_pct": "Absolute Error %",
            "method": "Forecast Method",
        }
    )

    show_df(display_table)

else:
    st.warning(
        "No forecast records are available for the selected metric and department."
    )


# ============================================================
# ATTRITION RISK
# ============================================================

st.header("4. Attrition Risk Signals")

st.write(
    "This section uses the existing 12-month attrition-risk output. "
    "Risk scores are signals for human review, not confirmed future events."
)

if not attrition.empty:

    risk_counts = (
        attrition["risk_band"]
        .value_counts()
        .reset_index()
    )

    risk_counts.columns = [
        "risk_band",
        "employee_count",
    ]

    fig_risk = px.bar(
        risk_counts,
        x="risk_band",
        y="employee_count",
        title="Employees by attrition-risk band",
        labels={
            "risk_band": "Risk band",
            "employee_count": "Employees",
        },
    )

    show_plot(fig_risk)

    st.caption(
        "AI-generated, for human review — risk bands summarize the existing "
        "attrition-risk feed and do not mean that an employee will definitely leave."
    )

    risk_table = attrition[
        [
            "employee_id",
            "department_id",
            "as_of_date",
            "risk_score_12m",
            "risk_band",
            "top_reason_1",
            "top_reason_2",
            "top_reason_3",
        ]
    ].copy()

    risk_table = risk_table.sort_values(
        "risk_score_12m",
        ascending=False
    )

    st.subheader("Highest attrition-risk signals")

    show_df(risk_table.head(20))

else:
    st.warning("No attrition-risk records are available.")


# ============================================================
# BUSINESS INTERPRETATION
# ============================================================

st.header("5. Human Review Guidance")

st.info(
    """
**Why a 12% forecast error cannot automatically be called good or bad**

A 12% error does not have a universal interpretation. Its usefulness depends
on the metric being forecast, the normal volatility of that metric, the
forecast horizon, the business decision being supported, and the cost of
being wrong.

For example, a 12% error in a small operational metric may have little
business impact, while the same percentage error in a high-value financial
forecast could be significant.

Therefore, forecast accuracy should be assessed against an appropriate
business baseline, historical performance, and decision threshold rather
than using 12% as a universal pass/fail rule.
"""
)

st.warning(
    "AI-generated, for human review — PulseIQ AI signals are decision-support "
    "outputs and should be validated by appropriate business owners."
)


# ============================================================
# MODEL INFORMATION
# ============================================================

st.header("6. AI Model Information")

model_values = pd.concat(
    [
        anomaly["model_version"],
        forecast["model_version"],
        attrition["model_version"],
    ],
    ignore_index=True,
).dropna().astype(str).unique()

if len(model_values) > 0:
    st.write("**Model versions present in the existing feeds:**")

    for model in sorted(model_values):
        st.write(f"- `{model}`")

forecast_methods = (
    forecast["method"]
    .dropna()
    .astype(str)
    .unique()
)

if len(forecast_methods) > 0:

    st.write("**Forecast methods present:**")

    for method in sorted(forecast_methods):
        st.write(f"- {method}")

st.caption(
    "Task 14 reuses the existing analytical/AI outputs in PulseIQ. "
    "No new model is trained by this dashboard."
)