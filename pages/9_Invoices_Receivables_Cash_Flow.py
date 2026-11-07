import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Invoices, Receivables & Cash Flow",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Invoices, Receivables & Cash Flow")
st.caption(
    "Task 12 — Invoice ageing, client payment behaviour, cash inflow and cash outflow"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

DB_PATH = Path("pulseiq.duckdb")

if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.stop()

con = duckdb.connect(str(DB_PATH), read_only=True)


# ============================================================
# LOAD INVOICE DATA
# ============================================================

invoice_query = """
SELECT
    i.invoice_id,
    i.invoice_number,
    i.client_id,
    c.client_name,
    c.industry,
    c.city,
    c.state_or_region,
    c.country,
    c.payment_terms_days,
    i.invoice_date,
    i.due_date,
    i.total_amount,
    i.amount_paid,
    i.balance_due,
    i.status,
    i.last_payment_date,
    i.days_to_pay
FROM warehouse.fact_invoice i
LEFT JOIN warehouse.dim_client c
    ON i.client_id = c.client_id
"""

invoices = con.execute(invoice_query).fetchdf()


# ============================================================
# LOAD PAYMENT DATA
# ============================================================

payment_query = """
SELECT
    payment_id,
    invoice_id,
    payment_date,
    amount,
    payment_mode,
    reference_no,
    received_by
FROM warehouse.fact_invoice_payment
"""

payments = con.execute(payment_query).fetchdf()


# ============================================================
# LOAD EXPENSE DATA
# ============================================================

expense_query = """
SELECT
    bill_reference,
    description,
    department_id,
    total_amount,
    due_date,
    paid_date,
    status,
    payment_mode,
    ledger_entry_id,
    payment_ledger_entry_id
FROM warehouse.fact_expense
"""

expenses = con.execute(expense_query).fetchdf()

con.close()


# ============================================================
# DATA TYPES
# ============================================================

date_columns = [
    "invoice_date",
    "due_date",
    "last_payment_date"
]

for col in date_columns:
    invoices[col] = pd.to_datetime(invoices[col], errors="coerce")

payments["payment_date"] = pd.to_datetime(
    payments["payment_date"],
    errors="coerce"
)

expenses["paid_date"] = pd.to_datetime(
    expenses["paid_date"],
    errors="coerce"
)

expenses["due_date"] = pd.to_datetime(
    expenses["due_date"],
    errors="coerce"
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Dashboard Filters")

min_invoice_date = invoices["invoice_date"].min()
max_invoice_date = invoices["invoice_date"].max()

date_range = st.sidebar.date_input(
    "Invoice Date Range",
    value=(
        min_invoice_date.date(),
        max_invoice_date.date()
    ),
    min_value=min_invoice_date.date(),
    max_value=max_invoice_date.date()
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])
else:
    start_date = min_invoice_date
    end_date = max_invoice_date


client_options = sorted(
    invoices["client_name"].dropna().unique().tolist()
)

selected_clients = st.sidebar.multiselect(
    "Client",
    options=client_options,
    default=[]
)


# ============================================================
# APPLY INVOICE FILTER
# ============================================================

filtered_invoices = invoices[
    (invoices["invoice_date"] >= start_date) &
    (invoices["invoice_date"] <= end_date)
].copy()

if selected_clients:
    filtered_invoices = filtered_invoices[
        filtered_invoices["client_name"].isin(selected_clients)
    ].copy()


# ============================================================
# OPEN RECEIVABLES
# ============================================================

OPEN_STATUSES = [
    "SENT",
    "OVERDUE",
    "PARTIALLY_PAID"
]

open_invoices = filtered_invoices[
    filtered_invoices["status"].isin(OPEN_STATUSES)
].copy()


# ============================================================
# AGEING
# ============================================================

# Ageing cutoff = selected end date.
#
# days_overdue:
#   Future due date -> 0 days
#   Due date to 30 days -> 0-30
#   31-60 days -> 31-60
#   61-90 days -> 61-90
#   >90 days -> 90+
#
# This keeps every open receivable in exactly one ageing bucket.

as_of_date = end_date

open_invoices["days_overdue"] = (
    as_of_date - open_invoices["due_date"]
).dt.days

open_invoices["days_overdue"] = (
    open_invoices["days_overdue"]
    .fillna(0)
    .clip(lower=0)
)


def ageing_bucket(days):
    if days <= 30:
        return "0–30 days"
    elif days <= 60:
        return "31–60 days"
    elif days <= 90:
        return "61–90 days"
    else:
        return "90+ days"


open_invoices["ageing_bucket"] = (
    open_invoices["days_overdue"]
    .apply(ageing_bucket)
)


AGEING_ORDER = [
    "0–30 days",
    "31–60 days",
    "61–90 days",
    "90+ days"
]


# ============================================================
# KPI VALUES
# ============================================================

total_open_receivables = open_invoices["balance_due"].sum()

overdue_receivables = open_invoices.loc[
    open_invoices["status"] == "OVERDUE",
    "balance_due"
].sum()

partially_paid_receivables = open_invoices.loc[
    open_invoices["status"] == "PARTIALLY_PAID",
    "balance_due"
].sum()

sent_receivables = open_invoices.loc[
    open_invoices["status"] == "SENT",
    "balance_due"
].sum()

open_invoice_count = len(open_invoices)


# ============================================================
# KPI ROW
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Open Receivables",
        f"₹{total_open_receivables / 1e7:.2f} Cr"
    )

with col2:
    st.metric(
        "Overdue",
        f"₹{overdue_receivables / 1e7:.2f} Cr"
    )

with col3:
    st.metric(
        "Partially Paid",
        f"₹{partially_paid_receivables / 1e7:.2f} Cr"
    )

with col4:
    st.metric(
        "Open Invoices",
        f"{open_invoice_count:,}"
    )


# ============================================================
# STATUS BREAKDOWN
# ============================================================

st.subheader("Open Receivables by Status")

status_df = (
    open_invoices
    .groupby("status", as_index=False)["balance_due"]
    .sum()
)

status_order = [
    "SENT",
    "OVERDUE",
    "PARTIALLY_PAID"
]

status_df["status"] = pd.Categorical(
    status_df["status"],
    categories=status_order,
    ordered=True
)

status_df = status_df.sort_values("status")

fig_status = px.bar(
    status_df,
    x="status",
    y="balance_due",
    text_auto=".2s",
    title="Open Receivables by Invoice Status",
    labels={
        "status": "Status",
        "balance_due": "Balance Due"
    }
)

fig_status.update_yaxes(
    tickprefix="₹",
    tickformat=",.0f"
)

st.plotly_chart(
    fig_status,
    use_container_width=True
)


# ============================================================
# AGEING ANALYSIS
# ============================================================

st.subheader("Receivables Ageing")

ageing_df = (
    open_invoices
    .groupby("ageing_bucket", as_index=False)["balance_due"]
    .sum()
)

ageing_df["ageing_bucket"] = pd.Categorical(
    ageing_df["ageing_bucket"],
    categories=AGEING_ORDER,
    ordered=True
)

ageing_df = ageing_df.sort_values("ageing_bucket")

fig_ageing = px.bar(
    ageing_df,
    x="ageing_bucket",
    y="balance_due",
    text_auto=".2s",
    title=f"Open Receivables Ageing as of {as_of_date.date()}",
    labels={
        "ageing_bucket": "Ageing Bucket",
        "balance_due": "Balance Due"
    }
)

fig_ageing.update_yaxes(
    tickprefix="₹",
    tickformat=",.0f"
)

st.plotly_chart(
    fig_ageing,
    use_container_width=True
)


# ============================================================
# AGEING RECONCILIATION
# ============================================================

ageing_total = ageing_df["balance_due"].sum()

reconciliation_difference = (
    ageing_total - total_open_receivables
)

st.subheader("Ageing Reconciliation")

rec_col1, rec_col2, rec_col3 = st.columns(3)

with rec_col1:
    st.metric(
        "Total Open Receivables",
        f"₹{total_open_receivables:,.0f}"
    )

with rec_col2:
    st.metric(
        "Ageing Bucket Total",
        f"₹{ageing_total:,.0f}"
    )

with rec_col3:
    st.metric(
        "Difference",
        f"₹{reconciliation_difference:,.0f}"
    )

if abs(reconciliation_difference) < 1:
    st.success("✅ Ageing buckets reconcile to total open receivables.")
else:
    st.error(
        "❌ Ageing reconciliation failed. "
        "Investigate missing or duplicated ageing records."
    )


# ============================================================
# CLIENT PAYMENT BEHAVIOUR
# ============================================================

st.subheader("Client Payment Behaviour")

# Use fully paid invoices with actual final payment date.
# This avoids treating an outstanding partial payment as a completed payment.

paid_invoices = filtered_invoices[
    (filtered_invoices["status"] == "PAID") &
    (filtered_invoices["invoice_date"].notna()) &
    (filtered_invoices["last_payment_date"].notna())
].copy()

paid_invoices["actual_days_to_pay"] = (
    paid_invoices["last_payment_date"]
    - paid_invoices["invoice_date"]
).dt.days

paid_invoices["actual_days_to_pay"] = (
    paid_invoices["actual_days_to_pay"].clip(lower=0)
)

client_payment_df = (
    paid_invoices
    .groupby(
        ["client_id", "client_name"],
        as_index=False
    )
    .agg(
        avg_days_to_pay=("actual_days_to_pay", "mean"),
        paid_invoice_count=("invoice_id", "nunique")
    )
)

client_payment_df = client_payment_df.sort_values(
    "avg_days_to_pay",
    ascending=False
)

if not client_payment_df.empty:

    fig_client = px.bar(
        client_payment_df.head(20),
        x="avg_days_to_pay",
        y="client_name",
        orientation="h",
        text="avg_days_to_pay",
        title="Average Days to Pay by Client — Top 20",
        labels={
            "avg_days_to_pay": "Average Days to Pay",
            "client_name": "Client"
        }
    )

    fig_client.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_client.add_vline(
        x=75,
        line_dash="dash",
        annotation_text="75-day risk threshold"
    )

    st.plotly_chart(
        fig_client,
        use_container_width=True
    )

    st.dataframe(
        client_payment_df,
        use_container_width=True
    )

else:
    st.info("No fully paid invoices with valid payment dates were found.")


# ============================================================
# HIGHEST OVERDUE CLIENTS
# ============================================================

st.subheader("Highest Overdue Clients")

overdue_client_df = (
    open_invoices[
        open_invoices["status"] == "OVERDUE"
    ]
    .groupby(
        ["client_id", "client_name"],
        as_index=False
    )["balance_due"]
    .sum()
    .sort_values("balance_due", ascending=False)
)

if not overdue_client_df.empty:

    fig_overdue = px.bar(
        overdue_client_df.head(15),
        x="balance_due",
        y="client_name",
        orientation="h",
        text_auto=".2s",
        title="Top Overdue Clients",
        labels={
            "balance_due": "Overdue Balance",
            "client_name": "Client"
        }
    )

    fig_overdue.update_xaxes(
        tickprefix="₹",
        tickformat=",.0f"
    )

    st.plotly_chart(
        fig_overdue,
        use_container_width=True
    )

else:
    st.info("No overdue clients found for the selected period.")


# ============================================================
# CASH FLOW
# ============================================================

st.subheader("Monthly Cash Inflow vs Cash Outflow")

# Cash inflow comes from actual invoice payment records.
cash_inflow = payments[
    (payments["payment_date"] >= start_date) &
    (payments["payment_date"] <= end_date)
].copy()

if selected_clients:
    selected_invoice_ids = set(
        filtered_invoices["invoice_id"].dropna()
    )

    cash_inflow = cash_inflow[
        cash_inflow["invoice_id"].isin(selected_invoice_ids)
    ]


cash_inflow["month"] = (
    cash_inflow["payment_date"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

inflow_monthly = (
    cash_inflow
    .groupby("month", as_index=False)["amount"]
    .sum()
    .rename(columns={"amount": "cash_inflow"})
)


# Cash outflow comes from actual paid expense records.
cash_outflow = expenses[
    (expenses["paid_date"] >= start_date) &
    (expenses["paid_date"] <= end_date)
].copy()

cash_outflow["month"] = (
    cash_outflow["paid_date"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

outflow_monthly = (
    cash_outflow
    .groupby("month", as_index=False)["total_amount"]
    .sum()
    .rename(columns={"total_amount": "cash_outflow"})
)


cash_flow = pd.merge(
    inflow_monthly,
    outflow_monthly,
    on="month",
    how="outer"
).fillna(0)

cash_flow = cash_flow.sort_values("month")

cash_flow["net_cash_flow"] = (
    cash_flow["cash_inflow"]
    - cash_flow["cash_outflow"]
)


if not cash_flow.empty:

    cash_flow_long = cash_flow.melt(
        id_vars="month",
        value_vars=[
            "cash_inflow",
            "cash_outflow"
        ],
        var_name="cash_flow_type",
        value_name="amount"
    )

    cash_flow_long["cash_flow_type"] = (
        cash_flow_long["cash_flow_type"]
        .map({
            "cash_inflow": "Cash Inflow",
            "cash_outflow": "Cash Outflow"
        })
    )

    fig_cash = px.bar(
        cash_flow_long,
        x="month",
        y="amount",
        color="cash_flow_type",
        barmode="group",
        title="Monthly Cash Inflow vs Cash Outflow",
        labels={
            "month": "Month",
            "amount": "Amount",
            "cash_flow_type": "Type"
        }
    )

    fig_cash.update_yaxes(
        tickprefix="₹",
        tickformat=",.0f"
    )

    st.plotly_chart(
        fig_cash,
        use_container_width=True
    )


# ============================================================
# CASH FLOW KPIs
# ============================================================

total_inflow = cash_flow["cash_inflow"].sum()
total_outflow = cash_flow["cash_outflow"].sum()
net_cash_flow = total_inflow - total_outflow

cash_col1, cash_col2, cash_col3 = st.columns(3)

with cash_col1:
    st.metric(
        "Cash Inflow",
        f"₹{total_inflow / 1e7:.2f} Cr"
    )

with cash_col2:
    st.metric(
        "Cash Outflow",
        f"₹{total_outflow / 1e7:.2f} Cr"
    )

with cash_col3:
    st.metric(
        "Net Cash Flow",
        f"₹{net_cash_flow / 1e7:.2f} Cr"
    )


# ============================================================
# VALIDATION CHECKS
# ============================================================

st.subheader("Data Validation Checks")

validation = []


# Missing invoice dates
missing_invoice_dates = (
    filtered_invoices["invoice_date"].isna().sum()
)

validation.append({
    "Check": "Missing invoice dates",
    "Result": int(missing_invoice_dates),
    "Status": "PASS" if missing_invoice_dates == 0 else "CHECK"
})


# Missing due dates
missing_due_dates = (
    open_invoices["due_date"].isna().sum()
)

validation.append({
    "Check": "Missing due dates in open invoices",
    "Result": int(missing_due_dates),
    "Status": "PASS" if missing_due_dates == 0 else "CHECK"
})


# Missing payment dates
missing_payment_dates = (
    payments["payment_date"].isna().sum()
)

validation.append({
    "Check": "Missing payment dates",
    "Result": int(missing_payment_dates),
    "Status": "PASS" if missing_payment_dates == 0 else "CHECK"
})


# Duplicate payment IDs
duplicate_payment_ids = (
    payments["payment_id"]
    .duplicated()
    .sum()
)

validation.append({
    "Check": "Duplicate payment IDs",
    "Result": int(duplicate_payment_ids),
    "Status": "PASS" if duplicate_payment_ids == 0 else "CHECK"
})


# Invoice amount reconciliation
invoice_reconciliation = (
    filtered_invoices["total_amount"]
    - filtered_invoices["amount_paid"]
    - filtered_invoices["balance_due"]
)

invoice_reconciliation_error = (
    invoice_reconciliation.abs() > 1
).sum()

validation.append({
    "Check": "Invoice total = paid + balance",
    "Result": int(invoice_reconciliation_error),
    "Status": "PASS" if invoice_reconciliation_error == 0 else "CHECK"
})


# Partial payment validation
partial_check = filtered_invoices[
    filtered_invoices["status"] == "PARTIALLY_PAID"
]

partial_invalid = (
    (
        partial_check["amount_paid"] <= 0
    ) |
    (
        partial_check["balance_due"] <= 0
    ) |
    (
        partial_check["amount_paid"] >= partial_check["total_amount"]
    )
).sum()

validation.append({
    "Check": "Partial payment amounts valid",
    "Result": int(partial_invalid),
    "Status": "PASS" if partial_invalid == 0 else "CHECK"
})


# Open status validation
invalid_open_statuses = (
    set(open_invoices["status"].dropna().unique())
    - set(OPEN_STATUSES)
)

validation.append({
    "Check": "Open statuses restricted to SENT / OVERDUE / PARTIALLY_PAID",
    "Result": (
        "PASS"
        if len(invalid_open_statuses) == 0
        else str(invalid_open_statuses)
    ),
    "Status": (
        "PASS"
        if len(invalid_open_statuses) == 0
        else "CHECK"
    )
})


# Ageing reconciliation
validation.append({
    "Check": "Ageing total = open receivables",
    "Result": f"₹{reconciliation_difference:,.0f}",
    "Status": (
        "PASS"
        if abs(reconciliation_difference) < 1
        else "CHECK"
    )
})


validation_df = pd.DataFrame(validation)

st.dataframe(
    validation_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FINANCE RISK INTERPRETATION
# ============================================================

st.subheader("Finance Risk: Clients Paying After 75 Days")

if not client_payment_df.empty:

    slow_clients = client_payment_df[
        client_payment_df["avg_days_to_pay"] > 75
    ].copy()

    if not slow_clients.empty:

        st.warning(
            f"⚠️ {len(slow_clients)} client(s) have an average payment "
            "time above 75 days."
        )

        st.markdown(
            """
            **Why this can be a financial risk**

            Consistently receiving payment after 75 days can slow cash
            conversion and increase working-capital pressure. Finance should
            investigate whether the delay is caused by:

            - payment terms that are too long
            - repeated overdue invoices
            - billing or documentation disputes
            - client approval delays
            - credit-risk or collection problems
            - concentration of receivables with a small number of clients

            Finance should compare the client's contractual payment terms,
            actual payment behaviour, overdue history and outstanding balance
            before deciding whether collection action or tighter credit
            controls are required.
            """
        )

        st.dataframe(
            slow_clients,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success(
            "No client has an average payment time above 75 days "
            "in the selected period."
        )


# ============================================================
# OPEN RECEIVABLE DETAILS
# ============================================================

with st.expander("View Open Receivable Details"):

    display_columns = [
        "invoice_id",
        "invoice_number",
        "client_name",
        "invoice_date",
        "due_date",
        "total_amount",
        "amount_paid",
        "balance_due",
        "status",
        "days_overdue",
        "ageing_bucket"
    ]

    st.dataframe(
        open_invoices[display_columns]
        .sort_values("balance_due", ascending=False),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "Source tables: warehouse.fact_invoice, warehouse.fact_invoice_payment, "
    "warehouse.dim_client and warehouse.fact_expense."
)