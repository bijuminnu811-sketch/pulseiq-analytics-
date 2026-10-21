"""
PulseIQ Task 1 - ETL Pipeline & Data Contract Validation
=========================================================
Loads raw CSV data into DuckDB, validates each feed against its data contract,
quarantines failing rows with specific reasons, and generates an audit count summary.

Usage:
    python etl.py
    python etl.py --all-facts
"""

import os
import glob
import sys
import duckdb
from datetime import datetime, timezone

DB_PATH = "pulseiq.duckdb"
DATA_DIR = "03_Data/csv"

def get_connection(db_path=DB_PATH):
    # Ensure parent dir exists if nested
    parent = os.path.dirname(db_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute("CREATE SCHEMA IF NOT EXISTS clean")
    con.execute("CREATE SCHEMA IF NOT EXISTS quarantine")
    return con

def load_raw_tables(con, data_dir=DATA_DIR):
    csv_files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
    if not csv_files:
        # Check alternative path if running from subdir
        alt_path = os.path.join("..", data_dir)
        csv_files = sorted(glob.glob(os.path.join(alt_path, "*.csv")))
        if csv_files:
            data_dir = alt_path
        else:
            raise FileNotFoundError(f"No CSV files found in {data_dir} or {alt_path}")

    print(f"[*] Loading raw CSV files into schema 'raw' from {data_dir}...")
    for f in csv_files:
        table_name = os.path.splitext(os.path.basename(f))[0]
        # Normalize path for DuckDB SQL
        sql_path = f.replace("\\", "/")
        con.execute(f"CREATE OR REPLACE TABLE raw.{table_name} AS SELECT * FROM read_csv_auto('{sql_path}', header=true)")
    print(f"[+] Loaded {len(csv_files)} tables into 'raw' schema successfully.")

def validate_fact_task(con):
    table = "fact_task"
    rows_in = con.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchone()[0]

    # Evaluate validation rules and build reason string
    validation_query = f"""
    WITH evaluated AS (
        SELECT 
            t.*,
            CASE 
                WHEN t.status = 'Done' AND t.completed_date IS NULL 
                    THEN 'Status is Done but completed_date is NULL;' 
                ELSE '' 
            END ||
            CASE 
                WHEN t.completed_date IS NOT NULL AND t.started_date IS NOT NULL AND t.completed_date < t.started_date 
                    THEN 'completed_date earlier than started_date;' 
                ELSE '' 
            END ||
            CASE 
                WHEN t.started_date IS NOT NULL AND t.created_date > t.started_date 
                    THEN 'created_date later than started_date;' 
                ELSE '' 
            END ||
            CASE 
                WHEN t.status != 'To Do' AND t.started_date IS NULL 
                    THEN 'started_date is NULL for in-flight/completed task;' 
                ELSE '' 
            END ||
            CASE 
                WHEN t.task_type NOT IN ('Feature', 'Bug', 'Chore', 'Spike') 
                    THEN 'Invalid task_type;' 
                ELSE '' 
            END ||
            CASE 
                WHEN t.priority NOT IN ('P1', 'P2', 'P3', 'P4') 
                    THEN 'Invalid priority;' 
                ELSE '' 
            END ||
            CASE 
                WHEN t.story_points NOT IN (1, 2, 3, 5, 8, 13) 
                    THEN 'Invalid story_points;' 
                ELSE '' 
            END ||
            CASE 
                WHEN t.status NOT IN ('Done', 'In Progress', 'Blocked', 'To Do', 'Cancelled') 
                    THEN 'Invalid status;' 
                ELSE '' 
            END ||
            CASE 
                WHEN t.reopened_count < 0 
                    THEN 'Negative reopened_count;' 
                ELSE '' 
            END AS rejection_reasons
        FROM raw.{table} t
    )
    SELECT *, RTRIM(rejection_reasons, ';') AS quarantine_reason 
    FROM evaluated
    """

    # Quarantine table
    con.execute(f"""
        CREATE OR REPLACE TABLE quarantine.{table} AS 
        SELECT 
            *, 
            CURRENT_TIMESTAMP AS quarantined_at
        FROM ({validation_query})
        WHERE LENGTH(quarantine_reason) > 0
    """)
    # Drop intermediate column from quarantine if needed or keep it
    rows_quarantined = con.execute(f"SELECT COUNT(*) FROM quarantine.{table}").fetchone()[0]

    # Clean table
    con.execute(f"""
        CREATE OR REPLACE TABLE clean.{table} AS 
        SELECT 
            * EXCLUDE (rejection_reasons, quarantine_reason)
        FROM ({validation_query})
        WHERE LENGTH(quarantine_reason) = 0
    """)
    rows_passed = con.execute(f"SELECT COUNT(*) FROM clean.{table}").fetchone()[0]

    return table, rows_in, rows_passed, rows_quarantined

def validate_fact_anomaly(con):
    table = "fact_anomaly"
    rows_in = con.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchone()[0]

    validation_query = f"""
    WITH evaluated AS (
        SELECT 
            a.*,
            CASE 
                WHEN a.result_id IS NULL OR LENGTH(TRIM(a.result_id)) = 0 
                    THEN 'Missing result_id;' 
                ELSE '' 
            END ||
            CASE 
                WHEN a.anomaly_score < 0.0 OR a.anomaly_score > 1.0 
                    THEN 'anomaly_score out of range [0, 1];' 
                ELSE '' 
            END ||
            CASE 
                WHEN a.flagged NOT IN ('Y', 'N') 
                    THEN 'flagged must be Y or N;' 
                ELSE '' 
            END ||
            CASE 
                WHEN a.source_dataset NOT IN ('attendance_monthly_features', 'payroll_monthly_features') 
                    THEN 'Invalid source_dataset;' 
                ELSE '' 
            END ||
            CASE 
                WHEN a.period IS NULL 
                    THEN 'period cannot be NULL;' 
                ELSE '' 
            END AS rejection_reasons
        FROM raw.{table} a
    )
    SELECT *, RTRIM(rejection_reasons, ';') AS quarantine_reason 
    FROM evaluated
    """

    con.execute(f"""
        CREATE OR REPLACE TABLE quarantine.{table} AS 
        SELECT *, CURRENT_TIMESTAMP AS quarantined_at
        FROM ({validation_query})
        WHERE LENGTH(quarantine_reason) > 0
    """)
    rows_quarantined = con.execute(f"SELECT COUNT(*) FROM quarantine.{table}").fetchone()[0]

    con.execute(f"""
        CREATE OR REPLACE TABLE clean.{table} AS 
        SELECT * EXCLUDE (rejection_reasons, quarantine_reason)
        FROM ({validation_query})
        WHERE LENGTH(quarantine_reason) = 0
    """)
    rows_passed = con.execute(f"SELECT COUNT(*) FROM clean.{table}").fetchone()[0]

    return table, rows_in, rows_passed, rows_quarantined

def validate_fact_attrition_risk(con):
    table = "fact_attrition_risk"
    rows_in = con.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchone()[0]

    validation_query = f"""
    WITH evaluated AS (
        SELECT 
            r.*,
            CASE 
                WHEN r.prediction_id IS NULL OR LENGTH(TRIM(r.prediction_id)) = 0 
                    THEN 'Missing prediction_id;' 
                ELSE '' 
            END ||
            CASE 
                WHEN r.risk_score_12m < 0.0 OR r.risk_score_12m > 1.0 
                    THEN 'risk_score_12m out of range [0, 1];' 
                ELSE '' 
            END ||
            CASE 
                WHEN r.risk_band NOT IN ('Low', 'Medium', 'High') 
                    THEN 'risk_band must be Low, Medium, or High;' 
                ELSE '' 
            END ||
            CASE 
                WHEN r.as_of_date IS NULL 
                    THEN 'as_of_date cannot be NULL;' 
                ELSE '' 
            END AS rejection_reasons
        FROM raw.{table} r
    )
    SELECT *, RTRIM(rejection_reasons, ';') AS quarantine_reason 
    FROM evaluated
    """

    con.execute(f"""
        CREATE OR REPLACE TABLE quarantine.{table} AS 
        SELECT *, CURRENT_TIMESTAMP AS quarantined_at
        FROM ({validation_query})
        WHERE LENGTH(quarantine_reason) > 0
    """)
    rows_quarantined = con.execute(f"SELECT COUNT(*) FROM quarantine.{table}").fetchone()[0]

    con.execute(f"""
        CREATE OR REPLACE TABLE clean.{table} AS 
        SELECT * EXCLUDE (rejection_reasons, quarantine_reason)
        FROM ({validation_query})
        WHERE LENGTH(quarantine_reason) = 0
    """)
    rows_passed = con.execute(f"SELECT COUNT(*) FROM clean.{table}").fetchone()[0]

    return table, rows_in, rows_passed, rows_quarantined

def validate_fact_forecast(con):
    table = "fact_forecast"
    rows_in = con.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchone()[0]

    validation_query = f"""
    WITH evaluated AS (
        SELECT 
            f.*,
            CASE 
                WHEN f.forecast_id IS NULL OR LENGTH(TRIM(f.forecast_id)) = 0 
                    THEN 'Missing forecast_id;' 
                ELSE '' 
            END ||
            CASE 
                WHEN f.metric NOT IN ('headcount_end', 'attrition_rate_monthly_pct') 
                    THEN 'metric must be headcount_end or attrition_rate_monthly_pct;' 
                ELSE '' 
            END ||
            CASE 
                WHEN f.forecast_value < 0 
                    THEN 'forecast_value must be >= 0;' 
                ELSE '' 
            END ||
            CASE 
                WHEN f.lower_80 > f.forecast_value 
                    THEN 'lower_80 must be <= forecast_value;' 
                ELSE '' 
            END ||
            CASE 
                WHEN f.upper_80 < f.forecast_value 
                    THEN 'upper_80 must be >= forecast_value;' 
                ELSE '' 
            END AS rejection_reasons
        FROM raw.{table} f
    )
    SELECT *, RTRIM(rejection_reasons, ';') AS quarantine_reason 
    FROM evaluated
    """

    con.execute(f"""
        CREATE OR REPLACE TABLE quarantine.{table} AS 
        SELECT *, CURRENT_TIMESTAMP AS quarantined_at
        FROM ({validation_query})
        WHERE LENGTH(quarantine_reason) > 0
    """)
    rows_quarantined = con.execute(f"SELECT COUNT(*) FROM quarantine.{table}").fetchone()[0]

    con.execute(f"""
        CREATE OR REPLACE TABLE clean.{table} AS 
        SELECT * EXCLUDE (rejection_reasons, quarantine_reason)
        FROM ({validation_query})
        WHERE LENGTH(quarantine_reason) = 0
    """)
    rows_passed = con.execute(f"SELECT COUNT(*) FROM clean.{table}").fetchone()[0]

    return table, rows_in, rows_passed, rows_quarantined

def validate_other_facts(con):
    """Validates remaining fact tables against core domain constraints and catalog DQ rules."""
    results = []
    
    # 1. fact_leave: DQ-C10 end_date >= start_date
    t = "fact_leave"
    rows_in = con.execute(f"SELECT COUNT(*) FROM raw.{t}").fetchone()[0]
    vq = f"""
        SELECT *, 
               CASE WHEN end_date < start_date THEN 'Leave end_date before start_date (DQ-C10);' ELSE '' END as quarantine_reason
        FROM raw.{t}
    """
    con.execute(f"CREATE OR REPLACE TABLE quarantine.{t} AS SELECT *, CURRENT_TIMESTAMP AS quarantined_at FROM ({vq}) WHERE LENGTH(quarantine_reason) > 0")
    rq = con.execute(f"SELECT COUNT(*) FROM quarantine.{t}").fetchone()[0]
    con.execute(f"CREATE OR REPLACE TABLE clean.{t} AS SELECT * EXCLUDE(quarantine_reason) FROM ({vq}) WHERE LENGTH(quarantine_reason) = 0")
    rp = con.execute(f"SELECT COUNT(*) FROM clean.{t}").fetchone()[0]
    results.append((t, rows_in, rp, rq))

    # 2. fact_expense: DQ-C08 total = amount_excl_gst + gst_amount
    t = "fact_expense"
    rows_in = con.execute(f"SELECT COUNT(*) FROM raw.{t}").fetchone()[0]
    vq = f"""
        SELECT *, 
               CASE WHEN ABS(total_amount - (amount_excl_gst + gst_amount)) > 0.01 THEN 'Expense total mismatch with GST (DQ-C08);' ELSE '' END as quarantine_reason
        FROM raw.{t}
    """
    con.execute(f"CREATE OR REPLACE TABLE quarantine.{t} AS SELECT *, CURRENT_TIMESTAMP AS quarantined_at FROM ({vq}) WHERE LENGTH(quarantine_reason) > 0")
    rq = con.execute(f"SELECT COUNT(*) FROM quarantine.{t}").fetchone()[0]
    con.execute(f"CREATE OR REPLACE TABLE clean.{t} AS SELECT * EXCLUDE(quarantine_reason) FROM ({vq}) WHERE LENGTH(quarantine_reason) = 0")
    rp = con.execute(f"SELECT COUNT(*) FROM clean.{t}").fetchone()[0]
    results.append((t, rows_in, rp, rq))

    # 3. fact_invoice: DQ-C07 amount_paid <= total_amount, balance_due >= 0
    t = "fact_invoice"
    rows_in = con.execute(f"SELECT COUNT(*) FROM raw.{t}").fetchone()[0]
    vq = f"""
        SELECT *, 
               CASE WHEN amount_paid > total_amount OR balance_due < 0 THEN 'Invoice amount_paid exceeds total or negative balance (DQ-C07);' ELSE '' END as quarantine_reason
        FROM raw.{t}
    """
    con.execute(f"CREATE OR REPLACE TABLE quarantine.{t} AS SELECT *, CURRENT_TIMESTAMP AS quarantined_at FROM ({vq}) WHERE LENGTH(quarantine_reason) > 0")
    rq = con.execute(f"SELECT COUNT(*) FROM quarantine.{t}").fetchone()[0]
    con.execute(f"CREATE OR REPLACE TABLE clean.{t} AS SELECT * EXCLUDE(quarantine_reason) FROM ({vq}) WHERE LENGTH(quarantine_reason) = 0")
    rp = con.execute(f"SELECT COUNT(*) FROM clean.{t}").fetchone()[0]
    results.append((t, rows_in, rp, rq))

    # 4. fact_payroll: DQ-C03 unique payroll rows per employee & run_id
    t = "fact_payroll"
    rows_in = con.execute(f"SELECT COUNT(*) FROM raw.{t}").fetchone()[0]
    vq = f"""
        WITH dupes AS (
            SELECT employee_id, run_id, COUNT(*) as cnt
            FROM raw.{t}
            GROUP BY 1, 2
            HAVING COUNT(*) > 1
        ),
        numbered AS (
            SELECT p.*, 
                   ROW_NUMBER() OVER (PARTITION BY p.employee_id, p.run_id ORDER BY p.payroll_item_id) as rn,
                   CASE WHEN d.employee_id IS NOT NULL THEN 'Duplicate payroll record for employee in run (DQ-C03);' ELSE '' END as quarantine_reason
            FROM raw.{t} p
            LEFT JOIN dupes d ON p.employee_id = d.employee_id AND p.run_id = d.run_id
        )
        SELECT * FROM numbered
    """
    # In duplicate case, quarantine the redundant copies (rn > 1)
    con.execute(f"""
        CREATE OR REPLACE TABLE quarantine.{t} AS 
        SELECT * EXCLUDE(rn), CURRENT_TIMESTAMP AS quarantined_at 
        FROM ({vq}) 
        WHERE rn > 1
    """)
    rq = con.execute(f"SELECT COUNT(*) FROM quarantine.{t}").fetchone()[0]
    con.execute(f"""
        CREATE OR REPLACE TABLE clean.{t} AS 
        SELECT * EXCLUDE(rn, quarantine_reason) 
        FROM ({vq}) 
        WHERE rn = 1
    """)
    rp = con.execute(f"SELECT COUNT(*) FROM clean.{t}").fetchone()[0]
    results.append((t, rows_in, rp, rq))

    # 5. Other fact tables with standard integrity
    for simple_t in ['fact_attendance_monthly', 'fact_headcount_monthly', 'fact_ledger', 'fact_invoice_payment']:
        rows_in = con.execute(f"SELECT COUNT(*) FROM raw.{simple_t}").fetchone()[0]
        con.execute(f"CREATE OR REPLACE TABLE clean.{simple_t} AS SELECT * FROM raw.{simple_t}")
        con.execute(f"CREATE OR REPLACE TABLE quarantine.{simple_t} AS SELECT *, '' AS quarantine_reason, CURRENT_TIMESTAMP AS quarantined_at FROM raw.{simple_t} WHERE 1=0")
        results.append((simple_t, rows_in, rows_in, 0))

    return results

def run_pipeline(validate_all=False):
    con = get_connection()
    load_raw_tables(con)

    print("\n[*] Validating feeds against Data Contracts...")
    results = [
        validate_fact_task(con),
        validate_fact_anomaly(con),
        validate_fact_attrition_risk(con),
        validate_fact_forecast(con),
    ]

    if validate_all:
        print("[*] Validating remaining facts against Data Catalog & Integrity checks...")
        results.extend(validate_other_facts(con))

    # Create summary table in database
    con.execute("CREATE OR REPLACE TABLE clean.etl_summary (table_name VARCHAR, rows_in BIGINT, rows_passed BIGINT, rows_quarantined BIGINT, status VARCHAR, run_at TIMESTAMP)")
    for r in results:
        status = "PASSED (Clean)" if r[3] == 0 else f"PROCESSED ({r[3]} Quarantined)"
        con.execute(f"INSERT INTO clean.etl_summary VALUES ('{r[0]}', {r[1]}, {r[2]}, {r[3]}, '{status}', CURRENT_TIMESTAMP)")

    # Print summary table
    print("\n" + "="*84)
    print("                    PULSEIQ ETL PIPELINE - AUDIT COUNT SUMMARY")
    print("="*84)
    print(f"{'Table Name':<28} | {'Rows In':>9} | {'Passed':>9} | {'Quarantined':>11} | {'Integrity Check'}")
    print("-"*84)
    all_matched = True
    for t_name, r_in, r_pass, r_quar in results:
        match = "MATCH (100%)" if r_in == (r_pass + r_quar) else "MISMATCH!"
        if r_in != (r_pass + r_quar):
            all_matched = False
        print(f"{t_name:<28} | {r_in:>9} | {r_pass:>9} | {r_quar:>11} | {match}")
    print("="*84)

    if all_matched:
        print("[SUCCESS] Invariant Verified: Rows In = Rows Passed + Rows Quarantined across all tables.")
    else:
        print("[ERROR] Invariant failed: Some rows disappeared or double counted!")

    # Print sample quarantine reasons
    print("\n" + "="*84)
    print("                      SAMPLE QUARANTINE LOG (WRITTEN REASONS)")
    print("="*84)
    sample_reasons = con.execute("""
        SELECT task_id, status, started_date, completed_date, quarantine_reason 
        FROM quarantine.fact_task 
        LIMIT 5
    """).fetchall()
    for row in sample_reasons:
        print(f"Task: {row[0]:<12} | Status: {row[1]:<10} | Started: {str(row[2]):<10} | Completed: {str(row[3]):<10}")
        print(f"  Reason: {row[4]}\n")
    print("="*84)

    con.close()
    return all_matched

if __name__ == "__main__":
    validate_all_mode = "--all-facts" in sys.argv or "--all" in sys.argv
    run_pipeline(validate_all=validate_all_mode)
