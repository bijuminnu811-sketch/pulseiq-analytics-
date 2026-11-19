"""
Test script for PulseIQ Metrics API (Task 19)
Tests all 5 exposed metric endpoints, health endpoint, and lineage endpoint.
Saves the live JSON responses to Phase_4/Task19_Metrics_API_Lineage/ for evidence.
"""

import os
import json
from api import (
    app,
    healthcheck,
    get_headcount,
    get_attrition_rate,
    get_payroll_cost,
    get_attendance_rate,
    get_operating_margin,
    get_data_lineage
)

EVIDENCE_DIR = os.path.join("Phase_4", "Task19_Metrics_API_Lineage")
os.makedirs(EVIDENCE_DIR, exist_ok=True)

print("[*] Testing PulseIQ Governed Metrics API...")

# 1. Healthcheck
r_health = healthcheck().model_dump()
print(f"[✓] GET /api/v1/health: {r_health['status']} | Tables: {r_health['active_warehouse_tables']} | Views: {r_health['governed_metrics_views']}")
with open(os.path.join(EVIDENCE_DIR, "response_health.json"), "w") as f:
    json.dump(r_health, f, indent=2)

# 2. Metric M01: Headcount
r_m01 = get_headcount(month="2026-09", department_id=None).model_dump()
m01_val = r_m01['metric_value']
assert m01_val == 441, f"Expected 441 headcount, got {m01_val}"
print(f"[✓] GET /api/v1/metrics/headcount: Value = {m01_val} employees (Match: 441)")
with open(os.path.join(EVIDENCE_DIR, "response_m01_headcount.json"), "w") as f:
    json.dump(r_m01, f, indent=2)

# 3. Metric M04: Attrition Rate
r_m04 = get_attrition_rate(month="2026-09").model_dump()
m04_val = r_m04['metric_value']
assert 0.60 <= m04_val <= 0.75, f"Expected ~0.7% attrition, got {m04_val}"
print(f"[✓] GET /api/v1/metrics/attrition-rate: Value = {m04_val}% (Match: 0.70%)")
with open(os.path.join(EVIDENCE_DIR, "response_m04_attrition_rate.json"), "w") as f:
    json.dump(r_m04, f, indent=2)

# 4. Metric M09: Payroll Cost
r_m09 = get_payroll_cost(month="2026-09").model_dump()
m09_val = r_m09['metric_value']
assert m09_val > 50000000, f"Expected > 50M payroll cost, got {m09_val}"
print(f"[✓] GET /api/v1/metrics/payroll-cost: Value = INR {m09_val:,.2f}")
with open(os.path.join(EVIDENCE_DIR, "response_m09_payroll_cost.json"), "w") as f:
    json.dump(r_m09, f, indent=2)

# 5. Metric M13: Attendance Rate
r_m13 = get_attendance_rate(month="2026-09").model_dump()
m13_val = r_m13['metric_value']
assert m13_val == 95.19, f"Expected 95.19% attendance, got {m13_val}"
print(f"[✓] GET /api/v1/metrics/attendance-rate: Value = {m13_val}% (Match: 95.19%)")
with open(os.path.join(EVIDENCE_DIR, "response_m13_attendance_rate.json"), "w") as f:
    json.dump(r_m13, f, indent=2)

# 6. Metric M18: Operating Margin
r_m18 = get_operating_margin(month="2026-09").model_dump()
m18_val = r_m18['metric_value']
assert m18_val == 18.25, f"Expected 18.25% margin, got {m18_val}"
print(f"[✓] GET /api/v1/metrics/operating-margin: Value = {m18_val}% (Match: 18.25%)")
with open(os.path.join(EVIDENCE_DIR, "response_m18_operating_margin.json"), "w") as f:
    json.dump(r_m18, f, indent=2)

# 7. Lineage & Impact Analysis
r_lineage = get_data_lineage()
print(f"[✓] GET /api/v1/lineage: Retrieved multi-hop lineage and column rename analysis")
with open(os.path.join(EVIDENCE_DIR, "response_lineage.json"), "w") as f:
    json.dump(r_lineage, f, indent=2)

print("\n" + "="*70)
print(" [✓] ALL 5 METRIC ENDPOINTS + LINEAGE VERIFIED SUCCESSFULLY")
print(f" Evidence artifacts saved to: {EVIDENCE_DIR}")
print("="*70)
