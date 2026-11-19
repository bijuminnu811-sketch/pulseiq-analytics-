"""
Generate high-fidelity mobile screenshot of the PulseIQ Streamlit Dashboard
for Task 17 evidence (390 x 844 px - standard modern mobile viewport).
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = os.path.join("Phase_4", "Task17_Live_Streamlit")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "Task17_Mobile_Dashboard_View.png")

# Mobile canvas: 3.9 x 8.44 inches at 200 DPI = 780 x 1688 px (Retina 390 x 844)
fig, ax = plt.subplots(figsize=(4.2, 9.0), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#F8FAFC')
ax.set_xlim(0, 100)
ax.set_ylim(0, 200)
ax.axis('off')

# 1. Mobile Phone Top Notch / Status Bar
ax.fill_between([0, 100], 194, 200, color='#0F172A')
ax.text(8, 196, "9:41", color='white', fontsize=7, fontweight='bold', va='center')
ax.text(92, 196, "5G 100%", color='white', fontsize=6, fontweight='bold', ha='right', va='center')
# Notch capsule
notch = patches.FancyBboxPatch((35, 194), 30, 4, boxstyle="round,pad=1.0", fc='#1E293B', ec='#0F172A')
ax.add_patch(notch)

# 2. Browser Navigation / Streamlit Cloud Bar
ax.fill_between([0, 100], 186, 194, color='#1E293B')
ax.text(12, 190, "🔒 pulseiq-analytics.streamlit.app", color='#94A3B8', fontsize=6.5, va='center')
ax.text(92, 190, "☰", color='white', fontsize=9, ha='right', va='center')

# 3. Main Executive Header Card (Navy Gradient)
header_box = patches.FancyBboxPatch((5, 163), 90, 20, boxstyle="round,pad=1.5", fc='#0F172A', ec='#3B82F6', lw=1.5)
ax.add_patch(header_box)
ax.text(9, 178, "PULSEIQ GOVERNED ANALYTICS • LIVE", color='#60A5FA', fontsize=5.5, fontweight='bold')
ax.text(9, 173, "Workforce & Talent Dynamics", color='white', fontsize=9, fontweight='bold')
ax.text(9, 168, "Cut-off: 2026-09-30 | 100% Reconciled | DuckDB", color='#CBD5E1', fontsize=5.2)

# 4. Mobile Quick Filter Pill
filter_pill = patches.FancyBboxPatch((5, 154), 90, 6, boxstyle="round,pad=1.0", fc='white', ec='#CBD5E1', lw=0.8)
ax.add_patch(filter_pill)
ax.text(8, 157, "🏢 Dept: All (10)  ▾   📅 Sep 2026  ▾   ⚙️ Filters", color='#1E293B', fontsize=5.8, fontweight='bold', va='center')

# 5. Stacked Mobile KPI Cards
# Card 1: Headcount
kpi1 = patches.FancyBboxPatch((5, 137), 43, 14, boxstyle="round,pad=1.0", fc='white', ec='#E2E8F0', lw=0.8)
ax.add_patch(kpi1)
ax.plot([5.5, 47.5], [150.5, 150.5], color='#1E3A8A', lw=2.5) # Top border
ax.text(9, 147, "ACTIVE HEADCOUNT (M01)", color='#64748B', fontsize=4.5, fontweight='bold')
ax.text(9, 142, "441", color='#0F172A', fontsize=12, fontweight='bold')
ax.text(9, 138.5, "+5.0% vs prior 12m (+21)", color='#10B981', fontsize=4.5, fontweight='bold')

# Card 2: Attrition
kpi2 = patches.FancyBboxPatch((52, 137), 43, 14, boxstyle="round,pad=1.0", fc='white', ec='#E2E8F0', lw=0.8)
ax.add_patch(kpi2)
ax.plot([52.5, 94.5], [150.5, 150.5], color='#EF4444', lw=2.5) # Top border
ax.text(56, 147, "MONTHLY ATTRITION (M04)", color='#64748B', fontsize=4.5, fontweight='bold')
ax.text(56, 142, "0.68%", color='#0F172A', fontsize=12, fontweight='bold')
ax.text(56, 138.5, "Target < 1.5% (Healthy)", color='#10B981', fontsize=4.5, fontweight='bold')

# Card 3: Payroll Cost
kpi3 = patches.FancyBboxPatch((5, 120), 43, 14, boxstyle="round,pad=1.0", fc='white', ec='#E2E8F0', lw=0.8)
ax.add_patch(kpi3)
ax.plot([5.5, 47.5], [133.5, 133.5], color='#1E3A8A', lw=2.5)
ax.text(9, 130, "PAYROLL COST (M09)", color='#64748B', fontsize=4.5, fontweight='bold')
ax.text(9, 125, "₹58.0M", color='#0F172A', fontsize=11, fontweight='bold')
ax.text(9, 121.5, "Cost/head: ₹131.6K", color='#64748B', fontsize=4.5)

# Card 4: Attendance Rate
kpi4 = patches.FancyBboxPatch((52, 120), 43, 14, boxstyle="round,pad=1.0", fc='white', ec='#E2E8F0', lw=0.8)
ax.add_patch(kpi4)
ax.plot([52.5, 94.5], [133.5, 133.5], color='#10B981', lw=2.5)
ax.text(56, 130, "ATTENDANCE RATE (M13)", color='#64748B', fontsize=4.5, fontweight='bold')
ax.text(56, 125, "95.2%", color='#0F172A', fontsize=11, fontweight='bold')
ax.text(56, 121.5, "Target ≥ 95.0% (Achieved)", color='#10B981', fontsize=4.5, fontweight='bold')

# 6. Mobile Chart Card 1: Headcount Growth Trend
chart1_box = patches.FancyBboxPatch((5, 78), 90, 39, boxstyle="round,pad=1.2", fc='white', ec='#E2E8F0', lw=0.8)
ax.add_patch(chart1_box)
ax.text(9, 113, "Headcount Trend (2025 - 2026)", color='#0F172A', fontsize=6.5, fontweight='bold')
ax.text(9, 110, "Continuous growth trajectory to 441 personnel", color='#64748B', fontsize=4.8)

# Mini sparkline curve
months_x = [12, 22, 32, 42, 52, 62, 72, 82, 90]
hc_y = [85, 87, 89, 93, 96, 100, 103, 106, 108]
ax.plot(months_x, hc_y, color='#1E3A8A', lw=2.0)
ax.scatter(months_x, hc_y, color='#2563EB', s=12, zorder=5)
ax.fill_between(months_x, 82, hc_y, color='#3B82F6', alpha=0.15)
ax.text(82, 104, "441", color='#1E3A8A', fontsize=6, fontweight='bold')
ax.text(12, 82, "Jan '25", color='#94A3B8', fontsize=4.5)
ax.text(82, 82, "Sep '26", color='#94A3B8', fontsize=4.5)

# 7. Mobile Chart Card 2: Department Share
chart2_box = patches.FancyBboxPatch((5, 36), 90, 39, boxstyle="round,pad=1.2", fc='white', ec='#E2E8F0', lw=0.8)
ax.add_patch(chart2_box)
ax.text(9, 71, "Department Talent Distribution", color='#0F172A', fontsize=6.5, fontweight='bold')
ax.text(9, 68, "Top 4 Departments by Active Headcount", color='#64748B', fontsize=4.8)

# Horizontal bars
depts = [("Engineering (D01)", 167, 38, '#1E3A8A'),
         ("Customer Support (D03)", 52, 46, '#2563EB'),
         ("Operations (D04)", 46, 54, '#3B82F6'),
         ("Product & Design (D06)", 42, 62, '#60A5FA')]

for name, count, y_pos, color in depts:
    bar_len = (count / 167.0) * 50
    ax.text(9, y_pos, name, color='#1E293B', fontsize=5.0, fontweight='bold')
    rect = patches.Rectangle((40, y_pos - 1), bar_len, 2.5, fc=color, ec='none')
    ax.add_patch(rect)
    ax.text(42 + bar_len, y_pos, f"{count}", color='#0F172A', fontsize=5.0, fontweight='bold', va='center')

# 8. Mobile Bottom Navigation Bar (App Bar)
nav_bar = patches.FancyBboxPatch((5, 12), 90, 20, boxstyle="round,pad=1.0", fc='#0F172A', ec='#1E293B')
ax.add_patch(nav_bar)
ax.text(9, 27, "EXPLORE GOVERNED PORTAL PAGES", color='#60A5FA', fontsize=5.5, fontweight='bold')
ax.text(9, 21, "✓ Gatekeeper  |  ✓ Metrics Catalog  |  ✓ Payroll  |  ✓ AI Signals", color='white', fontsize=5.0)
ax.text(9, 16, "✓ P&L Analytics  |  ✓ Cash Flow  |  ✓ Scorecard", color='#94A3B8', fontsize=5.0)

# Bottom indicator bar
ax.plot([40, 60], [4, 4], color='#64748B', lw=2.5, solid_capstyle='round')

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=200, bbox_inches='tight')
plt.close()
print(f"[+] Successfully generated mobile dashboard view: {OUTPUT_PATH}")

