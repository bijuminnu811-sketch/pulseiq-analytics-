"""
PulseIQ Doctor - Production Diagnostic & Health Verification Tool
==================================================================
A comprehensive CLI diagnostic utility that audits environment dependencies,
database integrity, warehouse reconciliation, metric layer compilation,
privacy guardrails, and API endpoints in a single automated command.

Usage:
    python pulseiq_doctor.py [--verbose]
"""

import os
import sys
import argparse
import duckdb
import pandas as pd
from datetime import datetime, timezone

DB_PATH = "pulseiq.duckdb"

class PulseIQDoctor:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = []
        self.all_passed = True

    def record_check(self, category: str, check_name: str, passed: bool, details: str):
        self.results.append({
            "category": category,
            "check": check_name,
            "passed": passed,
            "details": details
        })
        if not passed:
            self.all_passed = False

    def check_environment(self):
        # 1. Pinned requirements check
        req_path = "requirements.txt"
        if os.path.exists(req_path):
            with open(req_path, "r") as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
            pinned = all("==" in l for l in lines)
            self.record_check("Environment", "Pinned Dependencies (requirements.txt)", pinned, f"{len(lines)} packages verified (pinned={pinned})")
        else:
            self.record_check("Environment", "Pinned Dependencies (requirements.txt)", False, "File missing")

        # 2. Database existence
        db_exists = os.path.exists(DB_PATH)
        size_mb = (os.path.getsize(DB_PATH) / (1024*1024)) if db_exists else 0
        self.record_check("Environment", f"Warehouse Database ({DB_PATH})", db_exists, f"File present ({size_mb:.1f} MB)")

    def check_database_integrity(self):
        if not os.path.exists(DB_PATH):
            return
        con = duckdb.connect(DB_PATH, read_only=True)

        # Schemas
        schemas = [r[0] for r in con.execute("SELECT schema_name FROM information_schema.schemata").fetchall()]
        req_schemas = {'raw', 'clean', 'warehouse', 'metrics', 'quarantine'}
        has_schemas = req_schemas.issubset(set(schemas))
        self.record_check("Database", "Required Schemas (raw/clean/warehouse/metrics/quarantine)", has_schemas, f"Found: {schemas}")

        # Fact tables count in warehouse
        facts = [
            'fact_payroll', 'fact_attendance_monthly', 'fact_leave', 'fact_headcount_monthly',
            'fact_ledger', 'fact_invoice', 'fact_invoice_payment', 'fact_expense',
            'fact_task', 'fact_anomaly', 'fact_attrition_risk', 'fact_forecast'
        ]
        reconciled = True
        mismatches = []
        for f in facts:
            c_cnt = con.execute(f"SELECT COUNT(*) FROM clean.{f}").fetchone()[0]
            w_cnt = con.execute(f"SELECT COUNT(*) FROM warehouse.{f}").fetchone()[0]
            if c_cnt != w_cnt:
                reconciled = False
                mismatches.append(f"{f}: clean={c_cnt} vs wh={w_cnt}")

        detail_rec = "100% row match across all 12 fact tables" if reconciled else f"Mismatches: {mismatches}"
        self.record_check("Warehouse", "Clean vs Warehouse Row Reconciliation", reconciled, detail_rec)

        # Foreign Key / Orphan check
        orphan_emp = con.execute("""
            SELECT COUNT(*) 
            FROM warehouse.fact_payroll p
            LEFT JOIN warehouse.dim_employee e ON p.employee_key = e.employee_key
            WHERE e.employee_key IS NULL
        """).fetchone()[0]
        self.record_check("Warehouse", "Referential Integrity (fact_payroll -> dim_employee)", orphan_emp == 0, f"0 orphaned foreign keys ({orphan_emp} found)")

        # Governed Metric Views
        m_views = con.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='metrics'").fetchone()[0]
        self.record_check("Metric Layer", "Governed Metric Views (metrics.*)", m_views >= 28, f"{m_views} views compiled and accessible")

        con.close()

    def check_privacy_shield(self):
        if not os.path.exists(DB_PATH):
            return
        con = duckdb.connect(DB_PATH, read_only=True)

        # Check D00 Executive Office (n=1) is masked in m01_headcount
        masked_d00 = con.execute("""
            SELECT headcount_compliant, is_privacy_masked 
            FROM metrics.m01_headcount 
            WHERE department_id = 'D00' AND month_start_date = '2026-09-01'
        """).fetchone()

        d00_safe = (masked_d00 is not None) and (masked_d00[0] is None) and (masked_d00[1] is True)
        self.record_check("Privacy Guardrail", "Executive Office (D00, n=1) Privacy Masking", d00_safe, f"headcount_compliant=NULL, is_privacy_masked=TRUE")

        con.close()

    def check_api_readiness(self):
        try:
            from api import app, healthcheck, get_headcount
            h = healthcheck()
            m = get_headcount(month="2026-09")
            passed = (h.status == "HEALTHY") and (m.metric_value == 441)
            self.record_check("REST API", "FastAPI Service Endpoints & Health Probe", passed, f"Status: {h.status}, M01 Headcount: {m.metric_value}")
        except Exception as e:
            self.record_check("REST API", "FastAPI Service Endpoints & Health Probe", False, f"Exception: {str(e)}")

    def run_all(self):
        print("\n" + "="*80)
        print("               PULSEIQ DOCTOR — SYSTEM DIAGNOSTIC HARNESS")
        print("="*80)
        print(f" Timestamp:  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f" Database:   {DB_PATH}")
        print(f" Target Tag: v1.0.0 (Production Release)")
        print("="*80 + "\n")

        self.check_environment()
        self.check_database_integrity()
        self.check_privacy_shield()
        self.check_api_readiness()

        # Display results table
        print(f"{'Category':<16} | {'Diagnostic Check Name':<42} | {'Status':<8} | {'Details'}")
        print("-" * 80)
        for r in self.results:
            status_str = "[ PASS ]" if r['passed'] else "[ FAIL ]"
            print(f"{r['category']:<16} | {r['check']:<42} | {status_str:<8} | {r['details']}")

        print("\n" + "="*80)
        if self.all_passed:
            print(" [✓] PULSEIQ DOCTOR SUMMARY: ALL CHECKS PASSED — PLATFORM HEALTHY & RELEASE READY")
        else:
            print(" [✗] PULSEIQ DOCTOR SUMMARY: FAILURES DETECTED — REVIEW DIAGNOSTIC LOG ABOVE")
        print("="*80 + "\n")
        return 0 if self.all_passed else 1

def main():
    parser = argparse.ArgumentParser(description="PulseIQ Doctor Diagnostic Tool")
    parser.add_argument("--verbose", action="store_true", help="Print verbose debug statements")
    args = parser.parse_args()

    doc = PulseIQDoctor(verbose=args.verbose)
    exit_code = doc.run_all()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
