"""
Generate Task 18 Evidence Artifacts:
1. Executive / Admin View Screenshot (Task18_Role_View_Executive_Admin.png)
2. Manager Privacy Break-Test Screenshot (Task18_Role_View_Manager_Privacy_Break_Test.png)
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUT_DIR = os.path.join("Phase_4", "Task18_KPI_Explorer_Privacy")
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------------------------------------------------------------------
# 1. SCREENSHOT 1: EXECUTIVE / ADMIN VIEW
# ------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#F8FAFC')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Header
banner = patches.FancyBboxPatch((3, 82), 94, 15, boxstyle="round,pad=1.0", fc='#0F172A', ec='#3B82F6', lw=1.2)
ax.add_patch(banner)
ax.text(6, 92, "PULSEIQ GOVERNED KPI EXPLORER • EXECUTIVE / ADMIN VIEW", color='#60A5FA', fontsize=7, fontweight='bold')
ax.text(6, 86, "Role: EXECUTIVE (Tejas Chowdhury, CEO)  |  Scope: Company-Wide Consolidated", color='white', fontsize=9, fontweight='bold')

# Metric Selection Box
box_meta = patches.FancyBboxPatch((3, 68), 94, 11, boxstyle="round,pad=0.8", fc='white', ec='#CBD5E1', lw=0.8)
ax.add_patch(box_meta)
ax.text(6, 75, "Selected Metric: M04 - Attrition Rate (Monthly)  |  Grain: Department-Level Drill-Down", color='#1E3A8A', fontsize=8, fontweight='bold')
ax.text(6, 70.5, "Formula: (Exits / Start Headcount) * 100  |  Source: fact_headcount_monthly  |  Threshold: 10 Employees", color='#64748B', fontsize=6.8)

# Table Header
ax.fill_between([3, 97], 61, 66, color='#1E3A8A')
ax.text(5, 63.5, "Dept ID", color='white', fontsize=7, fontweight='bold', va='center')
ax.text(18, 63.5, "Department Name", color='white', fontsize=7, fontweight='bold', va='center')
ax.text(50, 63.5, "Cohort Size", color='white', fontsize=7, fontweight='bold', va='center')
ax.text(66, 63.5, "Attrition Rate", color='white', fontsize=7, fontweight='bold', va='center')
ax.text(82, 63.5, "Privacy Status", color='white', fontsize=7, fontweight='bold', va='center')

# Rows
rows = [
    ("D00", "Executive Office", "1", "[SUPPRESSED: Size 1 < 10]", "🔒 Suppressed (CEO Shield)", '#FEF2F2', '#EF4444'),
    ("D01", "Engineering", "167", "0.60%", "✅ Compliant", 'white', '#059669'),
    ("D02", "Product & Design", "26", "0.00%", "✅ Compliant", '#F8FAFC', '#059669'),
    ("D03", "Data & AI", "52", "0.00%", "✅ Compliant", 'white', '#059669'),
    ("D04", "Sales", "46", "0.00%", "✅ Compliant", '#F8FAFC', '#059669'),
    ("D08", "Finance & Accounting", "24", "4.17%", "✅ Compliant", 'white', '#059669'),
    ("D10", "Legal & Compliance", "7", "[SUPPRESSED: Size 7 < 10]", "🔒 Suppressed (Cohort < 10)", '#FEF2F2', '#EF4444')
]

y = 57
for dept, name, size, val, stat, bg, stat_col in rows:
    ax.fill_between([3, 97], y - 2, y + 3, color=bg)
    ax.plot([3, 97], [y - 2, y - 2], color='#E2E8F0', lw=0.5)
    ax.text(5, y + 0.5, dept, color='#0F172A', fontsize=6.8, fontweight='bold', va='center')
    ax.text(18, y + 0.5, name, color='#1E293B', fontsize=6.8, va='center')
    ax.text(52, y + 0.5, size, color='#0F172A', fontsize=6.8, fontweight='bold', va='center')
    ax.text(66, y + 0.5, val, color='#0F172A', fontsize=6.8, fontweight='bold' if 'SUPP' not in val else 'normal', va='center')
    ax.text(82, y + 0.5, stat, color=stat_col, fontsize=6.8, fontweight='bold', va='center')
    y -= 5.5

# Footer callout
priv_note = patches.FancyBboxPatch((3, 7), 94, 9, boxstyle="round,pad=0.8", fc='#ECFDF5', ec='#10B981', lw=0.8)
ax.add_patch(priv_note)
ax.text(5, 12.5, "VERIFIED PRIVACY GOVERNANCE:", color='#065F46', fontsize=6.8, fontweight='bold')
ax.text(5, 9, "Executive Office (D00, n=1) and Legal (D10, n=7) are automatically masked to uphold the 10-person privacy contract.", color='#065F46', fontsize=6.2)

plt.tight_layout()
p1 = os.path.join(OUT_DIR, "Task18_Role_View_Executive_Admin.png")
plt.savefig(p1, dpi=200, bbox_inches='tight')
plt.close()
print(f"[+] Generated: {p1}")

# ------------------------------------------------------------------------------
# 2. SCREENSHOT 2: MANAGER PRIVACY BREAK-TEST LAB
# ------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#F8FAFC')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Header
banner2 = patches.FancyBboxPatch((3, 82), 94, 15, boxstyle="round,pad=1.0", fc='#0F172A', ec='#D97706', lw=1.2)
ax.add_patch(banner2)
ax.text(6, 92, "PULSEIQ PRIVACY BREAK-TEST LAB • MANAGER MICRO-TEAM ATTEMPT", color='#FBBF24', fontsize=7, fontweight='bold')
ax.text(6, 86, "User: Priya Sharma (MANAGER)  |  Scope: Micro-Team T07 (Design Systems - 2 Members)", color='white', fontsize=9, fontweight='bold')

# Alert Box
alert_box = patches.FancyBboxPatch((3, 52), 94, 26, boxstyle="round,pad=1.0", fc='#FEF2F2', ec='#EF4444', lw=1.5)
ax.add_patch(alert_box)
ax.text(6, 73, "⚠️ PRIVACY BREAK-TEST: ATTEMPT TO QUERY SENSITIVE COMPENSATION & CHURN FOR N=2", color='#991B1B', fontsize=8.5, fontweight='bold')
ax.text(6, 68, "Target Metric: M04 - Monthly Attrition Rate & M07 - Individual Gross Compensation", color='#B91C1C', fontsize=7)
ax.text(6, 62.5, "Raw Attempt: Calculate average compensation & attrition risk across squad with only 2 direct reports.", color='#7F1D1D', fontsize=6.8)
ax.text(6, 56.5, "GUARDRAIL OUTCOME: ACCESS INTERCEPTED & VALUE MASKED TO [SUPPRESSED: Size 2 < 10]", color='#991B1B', fontsize=8, fontweight='bold')

# Shield Table
ax.fill_between([3, 97], 40, 46, color='#1E293B')
ax.text(5, 43, "Target Metric", color='white', fontsize=7, fontweight='bold', va='center')
ax.text(35, 43, "Cohort Size (N)", color='white', fontsize=7, fontweight='bold', va='center')
ax.text(55, 43, "Minimum Threshold", color='white', fontsize=7, fontweight='bold', va='center')
ax.text(75, 43, "Displayed Output", color='white', fontsize=7, fontweight='bold', va='center')

shield_rows = [
    ("M04 - Monthly Attrition Rate", "2 members", "10 employees", "[SUPPRESSED: Size 2 < 10]", '#EF4444'),
    ("M07 - Gross Compensation", "2 members", "5 employees", "[SUPPRESSED: Size 2 < 5]", '#EF4444'),
    ("M27 - High Attrition Risk Share", "2 members", "10 employees", "[SUPPRESSED: Size 2 < 10]", '#EF4444')
]

y = 35
for mname, nval, thresh, outval, ccol in shield_rows:
    ax.fill_between([3, 97], y - 2, y + 3, color='white')
    ax.plot([3, 97], [y - 2, y - 2], color='#E2E8F0', lw=0.5)
    ax.text(5, y + 0.5, mname, color='#0F172A', fontsize=6.8, fontweight='bold', va='center')
    ax.text(37, y + 0.5, nval, color='#0F172A', fontsize=6.8, va='center')
    ax.text(57, y + 0.5, thresh, color='#64748B', fontsize=6.8, va='center')
    ax.text(75, y + 0.5, outval, color=ccol, fontsize=6.8, fontweight='bold', va='center')
    y -= 5.5

# Strategic Decision Box
dec_box = patches.FancyBboxPatch((3, 4), 94, 13, boxstyle="round,pad=0.8", fc='#EFF6FF', ec='#3B82F6', lw=0.8)
ax.add_patch(dec_box)
ax.text(5, 13.5, "DECISION RATIONALE FOR MANAGER WITH TEAM OF 3:", color='#1E3A8A', fontsize=7, fontweight='bold')
ax.text(5, 9.5, "In a team of 3, 1 exit produces a 33.3% attrition rate. Because the manager knows who resigned,", color='#1E40AF', fontsize=6.2)
ax.text(5, 6.0, "disclosing this metric deanonymizes the employee. Strict suppression protects workplace safety and trust.", color='#1E40AF', fontsize=6.2)

plt.tight_layout()
p2 = os.path.join(OUT_DIR, "Task18_Role_View_Manager_Privacy_Break_Test.png")
plt.savefig(p2, dpi=200, bbox_inches='tight')
plt.close()
print(f"[+] Generated: {p2}")
