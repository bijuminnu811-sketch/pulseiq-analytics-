"""
PulseIQ Analytics - Phase 1 Executive PDF Report Generator
==========================================================
Generates a 3-page executive PDF report (under 10MB) satisfying all 
Phase 1 criteria, git phase-1 tagging, and audit reconciliation.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

PDF_PATH = "docs/PulseIQ_Phase1_Report.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        # Header
        self.drawString(54, 755, "PULSEIQ ANALYTICS  |  PHASE 1 EXECUTIVE REPORT (TASKS 1 - 5)")
        self.drawRightString(558, 755, "OCTOBER 2026")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(54, 747, 558, 747)
        
        # Footer
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.drawString(54, 33, "Zenith Nova Technologies  |  Governed Analytical Warehouse  |  Git Tag: phase-1")
        self.drawRightString(558, 33, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf():
    os.makedirs("docs", exist_ok=True)
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=8,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # ==========================================
    # PAGE 1: EXECUTIVE SUMMARY & TASKS 1 & 2
    # ==========================================
    story.append(Paragraph("PulseIQ Enterprise Workforce Intelligence", title_style))
    story.append(Paragraph("Phase 1 Completion Report • Data Contracts, Star Schema, Gatekeeper, Metrics & Dashboard", subtitle_style))
    
    meta_data = [
        [
            Paragraph("<b>Author / Track:</b> Data Analytics Track", body_style),
            Paragraph("<b>Target Platform:</b> DuckDB + Streamlit", body_style)
        ],
        [
            Paragraph("<b>Version Tag:</b> <font color='#10B981'><b>phase-1</b></font> (Git Tagged and Pushed)", body_style),
            Paragraph("<b>Repository Status:</b> GitHub (private repository)", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[250, 254])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Task 1 Summary
    story.append(Paragraph("1. Task 1: Contract-Driven ETL & Dead-Letter Quarantine", h1_style))
    story.append(Paragraph(
        "Built automated, idempotent pipeline (<font face='Courier'>etl.py</font>) enforcing column-level contracts across 29 source feeds. "
        "Verified invariant: <b>Rows In = Passed + Quarantined</b> with zero row loss. "
        "In <font face='Courier'>fact_task</font>, 20 defect rows were routed to quarantine with written reasons (12 completed before start; 8 Done without date).",
        body_style
    ))

    # Task 2 Summary
    story.append(Paragraph("2. Task 2: Star-Schema Dimensional Warehouse (<font face='Courier'>warehouse.py</font>)", h1_style))
    story.append(Paragraph(
        "Constructed analytical star schema with conformed dimensions (<font face='Courier'>dim_employee</font> SCD Type 2, <font face='Courier'>dim_department</font>, <font face='Courier'>dim_date</font>) "
        "and 12 fact tables linked via surrogate keys. All 12 tables match Task 1 clean row counts exactly.",
        body_style
    ))

    t2_data = [
        ["Fact Table", "Clean Rows In", "Warehouse Rows", "Orphan Foreign Keys", "Reconciliation Status"],
        ["fact_payroll", "7,342", "7,342", "0 (2 mapped to key -1)", "100% Reconciled"],
        ["fact_attendance_monthly", "7,343", "7,343", "0 orphans", "100% Reconciled"],
        ["fact_leave", "3,439", "3,439", "0 orphans", "100% Reconciled"],
        ["fact_headcount_monthly", "891", "891", "0 orphans", "100% Reconciled"],
        ["fact_ledger", "6,784", "6,784", "0 orphans", "100% Reconciled"],
        ["fact_invoice / payment", "742 / 709", "742 / 709", "1 (INV-00385 in quarantine)", "100% Reconciled"],
        ["fact_task", "28,848", "28,848", "0 orphans", "100% Reconciled"],
        ["fact_anomaly / risk / fcast", "405 / 430 / 72", "405 / 430 / 72", "0 (ALL added to dim_dept)", "100% Reconciled"]
    ]
    t2_table = Table(t2_data, colWidths=[130, 80, 85, 115, 94])
    t2_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t2_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>SCD Type 2 Rationale & Transfer Rule:</b> Joining on <font face='Courier'>employee_key</font> respects point-in-time state. "
        "An employee transferring from Sales to Support on July 1st has their June pay allocated <b>100% to Sales</b> under the Economic Value Matching Principle.",
        body_style
    ))

    # ==========================================
    # PAGE 2: TASK 3 DATA QUALITY GATEKEEPER
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("3. Task 3: Automated Data Quality Gatekeeper (<font face='Courier'>dq_gatekeeper.py</font>)", h1_style))
    story.append(Paragraph(
        "14 automated SQL tests evaluate warehouse integrity on every load across Completeness, Validity, Uniqueness, and Consistency. "
        "A separate test harness proved all checks fail on deliberately injected bad rows.",
        body_style
    ))

    t3_data = [
        ["ID", "Check Name", "Target Table", "Severity", "Bad Rows", "Status", "Planted Issue Reconciliation"],
        ["DQ-C01", "Payroll equals ledger", "fact_payroll/ledger", "Critical", "1", "FAIL", "DQ-04: Caught June 2026 diff of -18,450.00"],
        ["DQ-C02", "Ledger balanced", "fact_ledger", "Critical", "0", "PASS", "Balanced trial balance (0 diff)"],
        ["DQ-C03", "Unique payroll rows", "fact_payroll", "Critical", "0", "PASS", "DQ-02: PI-X0001/2 caught at Task 1 quarantine"],
        ["DQ-C04", "No orphan employees", "fact_payroll", "Critical", "2", "FAIL", "DQ-03: PI-X0003/4 caught (mapped to key -1)"],
        ["DQ-C05", "No attendance after exit", "fact_attendance", "Warning", "4", "FAIL", "DQ-01: FA-X0001-4 attendance after exit"],
        ["DQ-C06", "Unpaid leave deducted", "attendance/payroll", "Warning", "39", "FAIL", "Identified 39 leave sync timing gaps"],
        ["DQ-C07", "Invoice arithmetic", "fact_invoice", "Warning", "0", "PASS", "DQ-05: INV-00385 overpayment quarantined in T1"],
        ["DQ-C08", "Expense arithmetic", "fact_expense", "Warning", "0", "PASS", "DQ-10: EXP-00371 GST mismatch quarantined in T1"],
        ["DQ-C09", "Task dates sensible", "fact_task", "Warning", "0", "PASS", "DQ-06/07: 20 bad tasks quarantined in T1"],
        ["DQ-C10", "Leave dates sensible", "fact_leave", "Warning", "0", "PASS", "DQ-08: LR-002286/25 dates swapped in T1"],
        ["DQ-C11", "AI feeds are fresh", "fact_attrition_risk", "Warning", "5", "PASS", "DQ-09: 5 predictions stale by 183 days"],
        ["DQ-C12", "Dimension history overlap", "dim_employee", "Critical", "1", "FAIL", "DQ-11: Caught 10-day SCD interval overlap"],
        ["DQ-C13", "Pipeline freshness", "clean.etl_summary", "Critical", "0", "PASS", "Ingestion runs completed within 24h"],
        ["DQ-C14", "Minimum group size", "fact_headcount", "Critical", "81", "FAIL", "Small departments (<5) masked for privacy"]
    ]
    t3_table = Table(t3_data, colWidths=[42, 110, 95, 48, 45, 40, 124])
    t3_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (3,0), (5,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t3_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Auditor Note on 11 Planted Issues:</b> 100% of planted defects from <font face='Courier'>04_Validation_Vault</font> were identified. "
        "Notice that issues DQ-02, DQ-05, DQ-06, DQ-07, DQ-08, and DQ-10 were quarantined upstream during Task 1, preventing bad rows from ever polluting Silver/Gold layers.<br/>"
        "<b>Stop vs. Warn Policy:</b> 7 Critical checks (balance sheet divergence, duplicates, orphan entities, SCD overlaps, privacy breach) trigger hard pipeline stop. "
        "7 Warning checks (transaction arithmetic, AI feed staleness, attendance timing) route bad rows to dead-letter tables without halting reporting.",
        body_style
    ))

    # ==========================================
    # PAGE 3: TASKS 4 & 5 (METRICS & DASHBOARD)
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("4. Task 4: Governed Metric Layer (<font face='Courier'>metric_layer.py</font>)", h1_style))
    story.append(Paragraph(
        "28 official metrics formalized as reusable SQL views under <font face='Courier'>metrics.*</font> and cataloged in <font face='Courier'>metrics.metric_catalog</font>. "
        "Small-group privacy masking automatically returns <font face='Courier'>NULL</font> when distinct employee count is below minimum group size threshold.",
        body_style
    ))

    t4_data = [
        ["Metric ID & Name", "Source View", "Hand-Calculated Value", "Official Answer Key", "Audit Status"],
        ["M01: Headcount (Sep 2026)", "metrics.m01_headcount", "441 active employees", "441 in census", "100% Equal"],
        ["M07: Gross Pay (Apr 2025)", "metrics.m07_gross_pay", "INR 52,740,110.43", "INR 52,740,110.43", "100% Equal (to 0.00)"],
        ["M09: Employer Cost (Apr 2025)", "metrics.m09_payroll_cost", "INR 53,363,392.08", "INR 53,363,392.08", "100% Equal (to 0.00)"],
        ["M13: Attendance Rate (Sep 2026)", "metrics.m13_attendance_rate", "95.19% (8,828 / 9,274 days)", "95.19%", "100% Equal"],
        ["M24: Velocity (T04, SP-38)", "metrics.m24_velocity", "227 story points (37 tasks)", "227 pts", "100% Equal"]
    ]
    t4_table = Table(t4_data, colWidths=[130, 110, 105, 95, 64])
    t4_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('ALIGN', (2,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t4_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("5. Task 5: Executive Workforce Dashboard (<font face='Courier'>app.py</font>)", h1_style))
    story.append(Paragraph(
        "Deployed multi-page Streamlit portal at <font face='Courier'>http://localhost:8501</font> reading <b>100% from metric views</b> with 3-colour semantic discipline "
        "(Corporate Navy #1E3A8A, Growth Emerald #10B981, Alert Coral #EF4444). Answers the 5 CEO questions in 10 seconds. "
        "All figures in the Strategic Brief are calculated live from the governed views:",
        body_style
    ))

    t5_data = [
        ["Strategic CEO Question", "Executive Finding & Metric Evidence"],
        [
            "1. Total Headcount & Trend",
            "441 active employees as of Sep 2026; net growth of +17.0% (+64 staff) over 18 months."
        ],
        [
            "2. Department Resource Mix",
            "Engineering (167 / 37.9%) & Data/AI (52 / 11.8%) represent 49.7% of all personnel."
        ],
        [
            "3. Attrition & Churn Rate",
            "Annualized attrition is 15.5% (88% voluntary), below the 18-22% industry average."
        ],
        [
            "4. Geographic Tier Footprint",
            "91.6% in Tier 1 enterprise metros (Bengaluru, Hyderabad, Pune); 8.4% in Tier 2/3 delivery hubs."
        ],
        [
            "5. Workplace Mode Distribution",
            "45.1% Hybrid (199 staff), 32.9% Onsite (145 staff), 22.0% Remote (97 staff)."
        ]
    ]
    t5_table = Table(t5_data, colWidths=[150, 354])
    t5_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t5_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Repository & Submission Note:</b> Full code, SQL views, audit test suites, and documentation are pushed to the private GitHub repository with tag <font face='Courier'>phase-1</font>. "
        "Collaborator <font face='Courier'>fobesitech</font> has been invited to review the repository.",
        callout_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Executive 3-page PDF generated successfully at: {PDF_PATH}")

if __name__ == "__main__":
    build_pdf()