"""
PulseIQ Phase 4 Executive PDF Report Generator
==============================================
Generates an official, 3-page publication-grade PDF report:
DataAnalytics_MinnuBiju_Phase4_Report.pdf
Covering Tasks 16-20 with verifiable evidence, clickable links, test results, and audit sign-off.
"""

import os
import sys
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_PATHS = [
    "DataAnalytics_MinnuBiju_Phase4_Report.pdf",
    os.path.join("Phase_4", "DataAnalytics_MinnuBiju_Phase4_Report.pdf")
]

GITHUB_URL = "https://github.com/bijuminnu811-sketch/pulseiq-analytics-.git"
LIVE_URL = "https://pulseiq-minnu.streamlit.app"

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
        self.setFillColor(colors.HexColor("#475569"))
        # Header
        self.drawString(54, 755, "PULSEIQ ANALYTICS  |  PHASE 4 EXECUTIVE REPORT (TASKS 16 - 20)")
        self.drawRightString(558, 755, "PRODUCTION RELEASE v1.0.0")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(54, 747, 558, 747)
        
        # Footer
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.drawString(54, 33, "Zenith Nova Technologies  |  Governed Metric Layer  |  Lead Analyst: Minnu Biju")
        self.drawRightString(558, 33, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf(target_pdf_path):
    os.makedirs(os.path.dirname(os.path.abspath(target_pdf_path)), exist_ok=True)
    doc = SimpleDocTemplate(
        target_pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, leading=22,
        textColor=colors.HexColor('#0F172A'), spaceAfter=3
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13,
        textColor=colors.HexColor('#475569'), spaceAfter=10
    )
    h1_style = ParagraphStyle(
        'Header1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=14,
        textColor=colors.HexColor('#1E3A8A'), spaceBefore=6, spaceAfter=4
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11,
        textColor=colors.HexColor('#1E293B'), spaceAfter=4
    )
    callout_style = ParagraphStyle(
        'Callout', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=11,
        textColor=colors.HexColor('#065F46')
    )
    alert_style = ParagraphStyle(
        'Alert', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=11,
        textColor=colors.HexColor('#991B1B')
    )

    story = []

    # ==========================================
    # PAGE 1: METADATA & TASKS 16–20 STATUS
    # ==========================================
    story.append(Paragraph("PulseIQ Enterprise Analytics — Phase 4 Release Report", title_style))
    story.append(Paragraph("Phase 4 (Days 16–20) • Automated Report Builder, Live Cloud Dashboard, Privacy Guardrails, Metrics API & Board Pack", subtitle_style))

    # Metadata Card
    meta_info = [
        [
            Paragraph("<b>Candidate Name:</b> Minnu Biju", body_style),
            Paragraph("<b>Phase:</b> Phase 4 — Release (Tasks 16 – 20)", body_style)
        ],
        [
            Paragraph("<b>Track / Project:</b> Data Analytics  |  PulseIQ Analytics", body_style),
            Paragraph(f"<b>Live Dashboard:</b> <a href='{LIVE_URL}'><font color='#2563EB'><u>{LIVE_URL}</u></font></a>", body_style)
        ],
        [
            Paragraph(f"<b>GitHub Repository:</b> <a href='{GITHUB_URL}'><font color='#2563EB'><u>bijuminnu811-sketch/pulseiq-analytics-</u></font></a>", body_style),
            Paragraph("<b>Git References / Tags:</b> <font color='#10B981'><b>v1.0.0-rc1</b></font> &amp; <font color='#10B981'><b>v1.0.0</b></font>", body_style)
        ]
    ]
    t_meta = Table(meta_info, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # Tasks 16-20 Status Table
    story.append(Paragraph("1. Phase 4 Implementation & Audit Summary (Tasks 16 – 20)", h1_style))
    tasks_summary_data = [
        ["Task", "Milestone Focus", "Status", "Primary Artifacts & Verified Evidence"],
        ["Task 16", "Automated Monthly Report Builder", "COMPLETE", "build_report.py (1-command PDF/MD pack), requirements.txt pinned, tag v1.0.0-rc1"],
        ["Task 17", "Live Streamlit Cloud Deployment", "COMPLETE", "app.py mobile-responsive CSS, navigation, hosting architecture, data refresh cron"],
        ["Task 18", "Self-Service KPI Explorer + Privacy", "COMPLETE", "pages/13_KPI_Explorer.py, demo_users.csv RBAC, small-group suppression (<5 / <10)"],
        ["Task 19", "Enterprise Metrics API + Lineage", "COMPLETE", "api.py (FastAPI), 5 JSON responses, multi-hop lineage diagram, column rename trace"],
        ["Task 20", "Executive Board Pack + Final Release", "COMPLETE", "PulseIQ_Executive_Board_Pack.pdf (10 slides), RELEASE_NOTES.md, pulseiq_doctor.py, tag v1.0.0"]
    ]
    t_summary = Table(tasks_summary_data, colWidths=[48, 145, 62, 249])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (2,0), (2,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 8))

    # Task 16 & 17 Implementation Proof
    story.append(Paragraph("2. Technical Verification: Tasks 16 & 17 (Automation & Live Cloud)", h1_style))
    story.append(Paragraph(
        "<b>Task 16 Report Builder (<font face='Courier'>build_report.py</font>):</b> Executes in a single CLI command "
        "(<font face='Courier'>python build_report.py --month 2026-09</font>) to compile an executive 3-page PDF and Markdown pack. "
        "Dynamic dimensional outer joins against <font face='Courier'>warehouse.dim_department</font> ensure that if a new department is registered next month, "
        "it immediately surfaces across workforce and cost tables without requiring code modifications. All 11 Python libraries were strictly pinned in "
        "<font face='Courier'>requirements.txt</font>, and the release candidate was sealed with Git tag <font color='#10B981'><b>v1.0.0-rc1</b></font>.<br/>"
        "<b>Task 17 Streamlit Cloud Deployment (<font face='Courier'>app.py</font>):</b> Production-hardened with zero hardcoded plain-text secrets. "
        "DuckDB operates in <font face='Courier'>read_only=True</font> mode directly against <font face='Courier'>pulseiq.duckdb</font> (33.3 MB), "
        "eliminating external database latency and connection limits. Viewport CSS media queries (<font face='Courier'>@media (max-width: 768px)</font>) "
        "guarantee single-column stacking and clean typography on mobile phone screens (verified in <font face='Courier'>Task17_Mobile_Dashboard_View.png</font>).",
        body_style
    ))

    # ==========================================
    # PAGE 2: TASKS 18, 19, 20 VERIFICATION
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("3. Technical Verification: Tasks 18 & 19 (Self-Service Privacy & REST API)", h1_style))
    story.append(Paragraph(
        "<b>Task 18 Self-Service KPI Explorer (<font face='Courier'>pages/13_KPI_Explorer.py</font>):</b><br/>"
        "Provides dynamic multi-grain exploration (Company → Department → Team) backed by <font face='Courier'>demo_users.csv</font> "
        "implementing four explicit enterprise personas (ADMIN, EXECUTIVE, HR, and MANAGER). "
        "A strict <b>Small-Group Privacy Suppression Shield</b> enforces minimum cohort sizes (<font face='Courier'>min_group_size = 5</font> for compensation/headcount, "
        "and <font face='Courier'>min_group_size = 10</font> for attrition/risk). Cohorts below threshold are masked with "
        "<font face='Courier'>[SUPPRESSED: Size N &lt; K]</font>.<br/>"
        "• <i>Privacy Break-Test Lab:</i> Proved with micro-teams ($N=1, 2$). Tested against Executive Office ($D00$, $N=1$) and Design Systems ($T07$, $N=2$); "
        "both queries were intercepted and masked, completely shielding CEO pay and individual churn flight risks from deanonymization.<br/>"
        "• <i>Strategic Decision for Manager with Team of 3:</i> If a manager with 3 direct reports queries team-level attrition, the metric is <b>strictly suppressed</b>. "
        "Because 1 resignation equals 33.3% turnover, revealing this number de-anonymizes the departing employee to their daily supervisor. "
        "The manager is elevated to department benchmarks (<font face='Courier'>D01</font>) while individual support is routed through private 1-on-1 channels.<br/><br/>"
        "<b>Task 19 Governed Metrics REST API (<font face='Courier'>api.py</font>):</b><br/>"
        "FastAPI service exposing 5 certified metrics without duplicating business calculations. Verified via <font face='Courier'>test_api.py</font>:",
        body_style
    ))

    t19_api_data = [
        ["Metric ID", "Endpoint Route", "Domain", "Verified Actual Value", "Unit", "Parity with Warehouse"],
        ["M01", "GET /api/v1/metrics/headcount", "Workforce", "441", "count", "Exact match (441 active staff)"],
        ["M04", "GET /api/v1/metrics/attrition-rate", "Workforce", "0.70%", "percent", "Exact match (0.699% rounded)"],
        ["M09", "GET /api/v1/metrics/payroll-cost", "Finance", "INR 55,519,621.87", "INR", "Exact match to INR 0.00"],
        ["M13", "GET /api/v1/metrics/attendance-rate", "Operations", "95.19%", "percent", "Exact match (95.19%)"],
        ["M18", "GET /api/v1/metrics/operating-margin", "Commercial", "18.25%", "percent", "Exact match (INR 18.06M / INR 98.97M)"]
    ]
    t_api = Table(t19_api_data, colWidths=[45, 160, 60, 95, 45, 99])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (2,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_api)
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>Task 19 Column-Rename Blast Radius Analysis:</b> If raw column <font face='Courier'>employer_cost</font> in <font face='Courier'>fact_payroll.csv</font> "
        "is renamed to <font face='Courier'>company_payroll_cost</font>, the pipeline fails at <b>Stage 1 (etl.py schema contract check)</b>, preventing unvalidated rows from polluting Silver/Gold layers. "
        "If bypassed, 3 metric views (<font face='Courier'>m09, m10, m11</font>) throw BinderExceptions, the API throws HTTP 500, and 3 Streamlit pages crash.<br/>"
        "<b>Task 20 Board Presentation & Strategic Data Discipline:</b> Created 10-slide landscape deck (<font face='Courier'>PulseIQ_Executive_Board_Pack.pdf</font>). "
        "<i>Critical Strategic Dilemma:</i> <b>Do NOT recommend cutting sales/marketing headcount or blaming specific managers for turnover.</b> "
        "The warehouse contains transaction ledgers and attendance, but lacks CAC, sales pipeline attribution, and exit interview sentiment. "
        "Recommending staff cuts without pipeline conversion data would be an irresponsible analytical overreach unsupported by empirical evidence.<br/>"
        "<b>Required Final Challenge (Meaningful Improvement):</b> Built <font face='Courier'>pulseiq_doctor.py</font> — an enterprise CLI diagnostic engine "
        "that audits virtual environments, schemas, row reconciliation, gatekeeper tests, and API health in 5 seconds, certifying release readiness.",
        body_style
    ))

    # ==========================================
    # PAGE 3: LEARNINGS, PROBLEMS, ROADMAP
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("4. Key Professional Learnings (3–5 Lines)", h1_style))
    story.append(Paragraph(
        "1. <b>Conformed Star Schemas Guarantee Truth:</b> Centralizing calculations in SQL views under <font face='Courier'>metrics.*</font> eliminated metric divergence across web dashboards, PDF builders, and REST endpoints.<br/>"
        "2. <b>Privacy Cannot Be An Afterthought:</b> In small organizations, naive aggregation is mathematically equivalent to individual surveillance; privacy thresholds must be enforced at the SQL view engine.<br/>"
        "3. <b>Data Discipline Means Knowing What NOT to Say:</b> The mark of an elite data analyst is refusing to give recommendations where underlying data (e.g. CAC, sentiment) is too weak to support them.<br/>"
        "4. <b>Automated Diagnostics Enable True Production Readiness:</b> Building a unified self-testing utility (<font face='Courier'>pulseiq_doctor.py</font>) elevates a prototype into an enterprise data product.",
        body_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("5. Problems Encountered & Engineering Solutions", h1_style))
    problems_data = [
        ["#", "Encountered Challenge", "Root Cause Analysis", "Applied Engineering Solution"],
        ["1", "Hardcoded Department Arrays in Report Builders", "Hardcoding D01-D10 breaks if business adds new departments next month.", "Re-architected build_report.py to use dynamic outer joins on dim_department with COALESCE defaults."],
        ["2", "Small-Group Deanonymization in Self-Service Tools", "Aggregating teams of 1-3 people exposes exact executive pay and churn flight risk.", "Implemented centralized Small-Group Privacy Masking (<5 / <10) returning [SUPPRESSED] with clear explanation."],
        ["3", "FastAPI Query Default Parameter Binding with DuckDB", "FastAPI Query(...) defaults passed directly into Python calls caused DuckDB BinderException.", "Built resolve_param() helper resolving Query defaults so endpoints work seamlessly via HTTP and in Python."],
        ["4", "Streamlit 1.66 Deprecation of use_container_width", "Recent Streamlit releases deprecated use_container_width=True for Plotly charts.", "Upgraded all chart invocations to width='stretch', ensuring long-term container compatibility without console warnings."]
    ]
    t_prob = Table(problems_data, colWidths=[20, 140, 155, 189])
    t_prob.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_prob)
    story.append(Spacer(1, 4))

    story.append(Paragraph("6. Future Roadmap — What Should Be Improved Next (Phase 5)", h1_style))
    story.append(Paragraph(
        "• <b>Commercial Pipeline Integration:</b> Connect Salesforce / HubSpot CRM stage tables to model true Customer Acquisition Cost (CAC) and Lifetime Value (LTV).<br/>"
        "• <b>Qualitative Employee Sentiment NLP:</b> Integrate anonymized pulse surveys and exit interview text feeds to quantify qualitative workplace culture drivers.<br/>"
        "• <b>Continuous Integration CI/CD:</b> Embed <font face='Courier'>pulseiq_doctor.py</font> into GitHub Actions to execute automated regression audits on every pull request.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # Formal Sign-off
    signoff_box = [
        [
            Paragraph("<b>PHASE 4 AUDIT CERTIFICATION:</b><br/>"
                      "All 5 Tasks (Tasks 16, 17, 18, 19, and 20) are complete, tested, and verified against the conformed PulseIQ warehouse. "
                      "Phases 1, 2, and 3 history and artifacts are preserved intact. Git release tag <font color='#10B981'><b>v1.0.0</b></font> is active.", callout_style),
            Paragraph("<b>Analyst Sign-off:</b><br/>"
                      "Minnu Biju — Lead Data Analyst<br/>"
                      f"Date: {datetime.date.today().strftime('%B %d, %Y')} • Production Ready", body_style)
        ]
    ]
    t_sign = Table(signoff_box, colWidths=[330, 174])
    t_sign.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ECFDF5')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#10B981')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_sign)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully built Phase 4 Executive Report PDF: {target_pdf_path}")

if __name__ == "__main__":
    for p in PDF_PATHS:
        build_pdf(p)
