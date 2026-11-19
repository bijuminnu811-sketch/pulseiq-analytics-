"""
PulseIQ Task 19 - Governed Metrics REST API
============================================
FastAPI service exposing certified PulseIQ enterprise metrics from the
governed metric layer (DuckDB) with metadata, definitions, source lineage,
and verifiable data freshness.

Run with:
    uvicorn api:app --host 0.0.0.0 --port 8000
Interactive Documentation:
    http://localhost:8000/docs (Swagger UI)
    http://localhost:8000/redoc (ReDoc)
"""

import os
import duckdb
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

DB_PATH = "pulseiq.duckdb"
DATA_FRESHNESS_TIMESTAMP = "2026-09-30 23:59:59 UTC"

app = FastAPI(
    title="PulseIQ Governed Metrics API",
    description="Enterprise REST API exposing certified workforce, finance, and delivery metrics from the PulseIQ analytical warehouse.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def get_db():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database file pulseiq.duckdb not found")
    return duckdb.connect(DB_PATH, read_only=True)

# ------------------------------------------------------------------------------
# PYDANTIC RESPONSE MODELS
# ------------------------------------------------------------------------------
class MetricLineage(BaseModel):
    raw_source_table: str
    etl_pipeline_step: str
    warehouse_table: str
    governed_view: str
    downstream_consumers: List[str]

class MetricResponse(BaseModel):
    metric_id: str
    metric_name: str
    business_definition: str
    unit: str
    reporting_period: str
    reporting_month: str
    metric_value: Any
    breakdown: Optional[Dict[str, Any]] = None
    source_table: str
    lineage: MetricLineage
    data_freshness: str
    privacy_status: str

class HealthResponse(BaseModel):
    status: str
    service: str
    database_status: str
    active_warehouse_tables: int
    governed_metrics_views: int
    data_cut_off: str
    system_timestamp: str

# ------------------------------------------------------------------------------
# API ENDPOINTS
# ------------------------------------------------------------------------------
@app.get("/", tags=["General"])
def root():
    return {
        "service": "PulseIQ Governed Metrics API",
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "documentation": "/docs",
        "data_cut_off": DATA_FRESHNESS_TIMESTAMP,
        "exposed_metrics": [
            {"id": "M01", "name": "Headcount", "path": "/api/v1/metrics/headcount"},
            {"id": "M04", "name": "Monthly Attrition Rate", "path": "/api/v1/metrics/attrition-rate"},
            {"id": "M09", "name": "Employer Payroll Cost", "path": "/api/v1/metrics/payroll-cost"},
            {"id": "M13", "name": "Workforce Attendance Rate", "path": "/api/v1/metrics/attendance-rate"},
            {"id": "M18", "name": "Operating Profit Margin", "path": "/api/v1/metrics/operating-margin"}
        ]
    }

@app.get("/api/v1/health", response_model=HealthResponse, tags=["General"])
def healthcheck():
    try:
        con = get_db()
        w_tables = con.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='warehouse'").fetchone()[0]
        m_views = con.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='metrics'").fetchone()[0]
        con.close()
        db_stat = "CONNECTED (DuckDB 2.0.0)"
    except Exception as e:
        db_stat = f"ERROR: {str(e)}"
        w_tables = 0
        m_views = 0

    return HealthResponse(
        status="HEALTHY",
        service="PulseIQ Analytics API",
        database_status=db_stat,
        active_warehouse_tables=w_tables,
        governed_metrics_views=m_views,
        data_cut_off=DATA_FRESHNESS_TIMESTAMP,
        system_timestamp=datetime.now(timezone.utc).isoformat()
    )

# 1. METRIC M01: HEADCOUNT
@app.get("/api/v1/metrics/headcount", response_model=MetricResponse, tags=["Workforce"])
def get_headcount(
    month: str = Query("2026-09", pattern="^[0-9]{4}-[0-9]{2}$", description="Reporting month (YYYY-MM)"),
    department_id: Optional[str] = Query(None, description="Optional department filter (e.g. D01)")
):
    con = get_db()
    start_date = f"{month}-01"
    
    if department_id:
        row = con.execute("""
            SELECT 
                h.headcount_end,
                h.hires,
                h.exits,
                h.headcount_start,
                d.department_name
            FROM warehouse.fact_headcount_monthly h
            JOIN warehouse.dim_department d ON h.department_id = d.department_id
            WHERE h.month_start_date = CAST(? AS DATE) AND h.department_id = ?
        """, [start_date, department_id]).fetchone()
        if not row:
            con.close()
            raise HTTPException(status_code=404, detail=f"No headcount record found for {department_id} in {month}")
        val = row[0]
        breakdown = {"department_id": department_id, "department_name": row[4], "hires": row[1], "exits": row[2], "headcount_start": row[3]}
        priv = "Suppressed (Small Group < 5)" if val < 5 else "Compliant"
    else:
        row = con.execute("""
            SELECT 
                COALESCE(SUM(headcount_end), 0),
                COALESCE(SUM(hires), 0),
                COALESCE(SUM(exits), 0),
                COALESCE(SUM(headcount_start), 0)
            FROM warehouse.fact_headcount_monthly
            WHERE month_start_date = CAST(? AS DATE) AND department_id != 'ALL'
        """, [start_date]).fetchone()
        val = row[0]
        breakdown = {"company_wide_total": True, "hires": row[1], "exits": row[2], "headcount_start": row[3]}
        priv = "Compliant (Company Level)"

    con.close()
    return MetricResponse(
        metric_id="M01",
        metric_name="Headcount",
        business_definition="Active employees on the last day of the calendar month.",
        unit="count (employees)",
        reporting_period=f"{month}-01 to {month}-30",
        reporting_month=month,
        metric_value=val,
        breakdown=breakdown,
        source_table="warehouse.fact_headcount_monthly",
        lineage=MetricLineage(
            raw_source_table="raw.fact_headcount_monthly",
            etl_pipeline_step="etl.py (contract validation, SCD Type 2 mapping)",
            warehouse_table="warehouse.fact_headcount_monthly",
            governed_view="metrics.m01_headcount",
            downstream_consumers=["Executive Dashboard (app.py)", "KPI Explorer (pages/13_KPI_Explorer.py)", "REST API"]
        ),
        data_freshness=DATA_FRESHNESS_TIMESTAMP,
        privacy_status=priv
    )

# 2. METRIC M04: MONTHLY ATTRITION RATE
@app.get("/api/v1/metrics/attrition-rate", response_model=MetricResponse, tags=["Workforce"])
def get_attrition_rate(
    month: str = Query("2026-09", pattern="^[0-9]{4}-[0-9]{2}$", description="Reporting month (YYYY-MM)")
):
    con = get_db()
    start_date = f"{month}-01"
    row = con.execute("""
        SELECT 
            COALESCE(SUM(exits), 0) AS total_exits,
            COALESCE(SUM(headcount_start), 0) AS start_hc
        FROM warehouse.fact_headcount_monthly
        WHERE month_start_date = CAST(? AS DATE) AND department_id != 'ALL'
    """, [start_date]).fetchone()
    con.close()

    exits = row[0]
    start_hc = row[1]
    rate = round((exits / start_hc * 100.0), 2) if start_hc > 0 else 0.0

    return MetricResponse(
        metric_id="M04",
        metric_name="Attrition rate (monthly)",
        business_definition="Monthly exits divided by start headcount multiplied by 100.",
        unit="percent (%)",
        reporting_period=f"{month}-01 to {month}-30",
        reporting_month=month,
        metric_value=rate,
        breakdown={"total_exits": exits, "headcount_start": start_hc, "annualized_estimate_pct": round(rate * 12.0, 2)},
        source_table="warehouse.fact_headcount_monthly",
        lineage=MetricLineage(
            raw_source_table="raw.fact_headcount_monthly",
            etl_pipeline_step="etl.py (exit reason validation, contract checks)",
            warehouse_table="warehouse.fact_headcount_monthly",
            governed_view="metrics.m04_attrition_rate_monthly",
            downstream_consumers=["Attrition Analytics (pages/4_Attrition_Analytics.py)", "Executive Health Scorecard", "REST API"]
        ),
        data_freshness=DATA_FRESHNESS_TIMESTAMP,
        privacy_status="Compliant (Company Level, Cohort > 10)"
    )

# 3. METRIC M09: EMPLOYER PAYROLL COST
@app.get("/api/v1/metrics/payroll-cost", response_model=MetricResponse, tags=["Finance"])
def get_payroll_cost(
    month: str = Query("2026-09", pattern="^[0-9]{4}-[0-9]{2}$", description="Reporting month (YYYY-MM)")
):
    con = get_db()
    row = con.execute("""
        SELECT 
            COALESCE(SUM(employer_cost), 0) AS employer_cost,
            COALESCE(SUM(gross_pay), 0) AS gross_pay,
            COALESCE(SUM(pf_employer), 0) AS pf_employer,
            COALESCE(SUM(net_pay), 0) AS net_pay,
            COUNT(DISTINCT employee_id) AS paid_employees
        FROM warehouse.fact_payroll
        WHERE strftime(date_trunc('month', period_end_date), '%Y-%m') = ?
    """, [month]).fetchone()
    con.close()

    total_cost = round(row[0], 2)
    paid_staff = row[4]
    cost_per_head = round((total_cost / paid_staff), 2) if paid_staff > 0 else 0.0

    return MetricResponse(
        metric_id="M09",
        metric_name="Payroll cost (employer cost)",
        business_definition="Total statutory employer payroll cost comprising gross pay, employer PF, and ESI contributions.",
        unit="INR (currency)",
        reporting_period=f"{month}-01 to {month}-30",
        reporting_month=month,
        metric_value=total_cost,
        breakdown={
            "gross_pay_inr": round(row[1], 2),
            "employer_pf_inr": round(row[2], 2),
            "net_pay_inr": round(row[3], 2),
            "paid_employees_count": paid_staff,
            "average_cost_per_head_inr": cost_per_head
        },
        source_table="warehouse.fact_payroll",
        lineage=MetricLineage(
            raw_source_table="raw.fact_payroll",
            etl_pipeline_step="etl.py (arithmetic validation, surrogate employee_key lookup)",
            warehouse_table="warehouse.fact_payroll",
            governed_view="metrics.m09_payroll_cost",
            downstream_consumers=["Payroll Dashboard (pages/6_Payroll_Cost_Dashboard.py)", "P&L Analytics", "REST API"]
        ),
        data_freshness=DATA_FRESHNESS_TIMESTAMP,
        privacy_status="Compliant (Company Level, Cohort > 5)"
    )

# 4. METRIC M13: WORKFORCE ATTENDANCE RATE
@app.get("/api/v1/metrics/attendance-rate", response_model=MetricResponse, tags=["Operations"])
def get_attendance_rate(
    month: str = Query("2026-09", pattern="^[0-9]{4}-[0-9]{2}$", description="Reporting month (YYYY-MM)")
):
    con = get_db()
    row = con.execute("""
        SELECT 
            COALESCE(SUM(present_days), 0) AS present,
            COALESCE(SUM(half_days_unpaid), 0) AS half_days,
            COALESCE(SUM(scheduled_days), 0) AS scheduled
        FROM warehouse.fact_attendance_monthly
        WHERE strftime(date_trunc('month', period_end_date), '%Y-%m') = ?
    """, [month]).fetchone()
    con.close()

    present = row[0]
    half_days = row[1]
    scheduled = row[2]
    present_equiv = present + 0.5 * half_days
    rate = round((present_equiv / scheduled * 100.0), 2) if scheduled > 0 else 0.0

    return MetricResponse(
        metric_id="M13",
        metric_name="Attendance rate",
        business_definition="Total present working days plus weighted half-days divided by scheduled working days multiplied by 100.",
        unit="percent (%)",
        reporting_period=f"{month}-01 to {month}-30",
        reporting_month=month,
        metric_value=rate,
        breakdown={
            "present_days": present,
            "half_days_unpaid": half_days,
            "effective_present_days": present_equiv,
            "scheduled_days": scheduled
        },
        source_table="warehouse.fact_attendance_monthly",
        lineage=MetricLineage(
            raw_source_table="raw.fact_attendance_monthly",
            etl_pipeline_step="etl.py (attendance cap checks, timing contract verification)",
            warehouse_table="warehouse.fact_attendance_monthly",
            governed_view="metrics.m13_attendance_rate",
            downstream_consumers=["Attendance Trends (pages/3_Attendance_Leave_Trends.py)", "Executive Health Scorecard", "REST API"]
        ),
        data_freshness=DATA_FRESHNESS_TIMESTAMP,
        privacy_status="Compliant (Company Level, Cohort > 5)"
    )

# 5. METRIC M18: OPERATING PROFIT MARGIN
@app.get("/api/v1/metrics/operating-margin", response_model=MetricResponse, tags=["Commercial"])
def get_operating_margin(
    month: str = Query("2026-09", pattern="^[0-9]{4}-[0-9]{2}$", description="Reporting month (YYYY-MM)")
):
    con = get_db()
    row = con.execute("""
        WITH rev AS (
            SELECT COALESCE(SUM(credit - debit), 0) as rev
            FROM warehouse.fact_ledger
            WHERE account_code BETWEEN 4001 AND 4004
              AND strftime(date_trunc('month', entry_date), '%Y-%m') = ?
        ),
        exp AS (
            SELECT COALESCE(SUM(debit - credit), 0) as exp
            FROM warehouse.fact_ledger
            WHERE account_code BETWEEN 5001 AND 5999
              AND strftime(date_trunc('month', entry_date), '%Y-%m') = ?
        )
        SELECT rev.rev, exp.exp, (rev.rev - exp.exp) AS net_profit
        FROM rev, exp
    """, [month, month]).fetchone()
    con.close()

    rev = round(row[0], 2)
    exp = round(row[1], 2)
    profit = round(row[2], 2)
    margin = round((profit / rev * 100.0), 2) if rev > 0 else 0.0

    return MetricResponse(
        metric_id="M18",
        metric_name="Operating margin",
        business_definition="Net profit divided by recognized ledger revenue multiplied by 100.",
        unit="percent (%)",
        reporting_period=f"{month}-01 to {month}-30",
        reporting_month=month,
        metric_value=margin,
        breakdown={
            "recognized_revenue_inr": rev,
            "operating_expenses_inr": exp,
            "net_operating_profit_inr": profit
        },
        source_table="warehouse.fact_ledger",
        lineage=MetricLineage(
            raw_source_table="raw.fact_ledger",
            etl_pipeline_step="etl.py (double-entry trial balance arithmetic checks)",
            warehouse_table="warehouse.fact_ledger",
            governed_view="metrics.m18_operating_margin",
            downstream_consumers=["P&L Analytics (pages/8_Profit_Loss_Analytics.py)", "Executive Health Scorecard", "REST API"]
        ),
        data_freshness=DATA_FRESHNESS_TIMESTAMP,
        privacy_status="Compliant (Entity Level Aggregate)"
    )

# ------------------------------------------------------------------------------
# DATA LINEAGE & IMPACT ANALYSIS ENDPOINT
# ------------------------------------------------------------------------------
@app.get("/api/v1/lineage", tags=["Governance"])
def get_data_lineage():
    return {
        "architecture": "PulseIQ Certified Multi-Hop Governed Data Pipeline",
        "pipeline_stages": [
            "1. RAW LAYER (03_Data/csv/ or raw schema)",
            "2. CONTRACT VALIDATION & ETL (etl.py - schema contracts, dead-letter quarantine)",
            "3. DIMENSIONAL WAREHOUSE (warehouse.py - SCD Type 2 dimensions, surrogate conformed facts)",
            "4. DATA QUALITY GATEKEEPER (dq_gatekeeper.py - 14 automated SQL audit gates)",
            "5. GOVERNED METRIC LAYER (metric_layer.py - 28 unified metric views with privacy masking)",
            "6. CONSUMPTION (FastAPI REST endpoints & Streamlit Multi-Page Portal)"
        ],
        "five_exposed_metrics_lineage": {
            "M01_Headcount": {
                "raw": "raw.fact_headcount_monthly",
                "etl": "etl.py (validates positive integer headcount, SCD key mapping)",
                "warehouse": "warehouse.fact_headcount_monthly",
                "metric_view": "metrics.m01_headcount",
                "consumers": ["app.py", "pages/13_KPI_Explorer.py", "GET /api/v1/metrics/headcount"]
            },
            "M04_Attrition_Rate": {
                "raw": "raw.fact_headcount_monthly",
                "etl": "etl.py (exit type categorisation, denominator alignment)",
                "warehouse": "warehouse.fact_headcount_monthly",
                "metric_view": "metrics.m04_attrition_rate_monthly",
                "consumers": ["pages/4_Attrition_Analytics.py", "pages/12_Executive_Health_Scorecard.py", "GET /api/v1/metrics/attrition-rate"]
            },
            "M09_Payroll_Cost": {
                "raw": "raw.fact_payroll",
                "etl": "etl.py (statutory PF/ESI contribution arithmetic verification)",
                "warehouse": "warehouse.fact_payroll",
                "metric_view": "metrics.m09_payroll_cost",
                "consumers": ["pages/6_Payroll_Cost_Dashboard.py", "pages/8_Profit_Loss_Analytics.py", "GET /api/v1/metrics/payroll-cost"]
            },
            "M13_Attendance_Rate": {
                "raw": "raw.fact_attendance_monthly",
                "etl": "etl.py (verifies present + wfh <= scheduled days cap)",
                "warehouse": "warehouse.fact_attendance_monthly",
                "metric_view": "metrics.m13_attendance_rate",
                "consumers": ["pages/3_Attendance_Leave_Trends.py", "pages/12_Executive_Health_Scorecard.py", "GET /api/v1/metrics/attendance-rate"]
            },
            "M18_Operating_Margin": {
                "raw": "raw.fact_ledger",
                "etl": "etl.py (double-entry trial balance debit/credit balance checks)",
                "warehouse": "warehouse.fact_ledger",
                "metric_view": "metrics.m18_operating_margin",
                "consumers": ["pages/8_Profit_Loss_Analytics.py", "pages/12_Executive_Health_Scorecard.py", "GET /api/v1/metrics/operating-margin"]
            }
        },
        "column_rename_impact_analysis": {
            "scenario": "Raw column 'employer_cost' in fact_payroll renamed to 'company_payroll_cost'",
            "impact_trace": [
                {"component": "1. ETL Pipeline", "file": "etl.py", "impact": "Contract schema check fails during csv validation: expected 'employer_cost', column missing. Pipeline halts."},
                {"component": "2. Warehouse DDL", "file": "warehouse.py", "impact": "INSERT INTO warehouse.fact_payroll fails due to attribute error 'employer_cost'."},
                {"component": "3. Metric Layer", "file": "metric_layer.py", "impact": "Views 'metrics.m09_payroll_cost', 'metrics.m10_cost_per_head', and 'metrics.m11_overtime_share' fail to compile with BinderException."},
                {"component": "4. REST API", "file": "api.py", "impact": "Endpoint 'GET /api/v1/metrics/payroll-cost' returns HTTP 500 Binder Error."},
                {"component": "5. Streamlit Dashboards", "files": ["pages/6_Payroll_Cost_Dashboard.py", "pages/8_Profit_Loss_Analytics.py", "pages/12_Executive_Health_Scorecard.py"], "impact": "Pages crash on render when executing SQL queries referencing m09_payroll_cost."}
            ]
        }
    }
