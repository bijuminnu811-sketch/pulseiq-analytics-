"""
PulseIQ Consolidated Project Report generator (revised).
Run:  python generate_consolidated_report_pdf.py
Output: DataAnalytics_MinnuBiju_Consolidated_Report.pdf (+ copy in Phase_4/)
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether, Flowable)
from reportlab.pdfgen import canvas

NAME = "Minnu Biju"
GITHUB = "https://github.com/bijuminnu811-sketch/pulseiq-analytics-"
LIVE = "https://pulseiq-minnu.streamlit.app"
VIDEO = "https://drive.google.com/file/d/1oXB0SsAtvfDHPw9qN4p8SUR48N1vz92B/view?usp=drivesdk"
OUT = "DataAnalytics_MinnuBiju_Consolidated_Report.pdf"
OUT_COPIES = [OUT, os.path.join("Phase_4", OUT)]

NAVY = colors.HexColor("#1E3A8A")
INK = colors.HexColor("#1E293B")
GREY = colors.HexColor("#475569")
LINE = colors.HexColor("#CBD5E1")
SOFT = colors.HexColor("#F1F5F9")
AMBER = colors.HexColor("#FEF3C7")

ss = getSampleStyleSheet()
def S(name, **kw):
    base = dict(parent=ss["Normal"], fontName="Helvetica", fontSize=9.5,
                leading=13, textColor=INK, spaceAfter=4)
    base.update(kw)
    return ParagraphStyle(name, **base)

title = S("t", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=NAVY, spaceAfter=4)
sub = S("s", fontSize=10.5, leading=14, textColor=GREY, spaceAfter=10)
h1 = S("h1", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=NAVY, spaceBefore=6, spaceAfter=6)
h2 = S("h2", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=NAVY, spaceBefore=6, spaceAfter=2)
body = S("b")
small = S("sm", fontSize=8.5, leading=11)
cell = S("c", fontSize=8.5, leading=11, spaceAfter=0)
cellb = S("cb", fontSize=8.5, leading=11, spaceAfter=0, fontName="Helvetica-Bold", textColor=colors.white)
bullet = S("bl", leftIndent=12, bulletIndent=2, spaceAfter=2)

def P(t, st=body): return Paragraph(t, st)
def B(t): return Paragraph(t, bullet, bulletText="-")
def link(u, label=None): return f"<a href='{u}'><font color='#2563EB'><u>{label or u}</u></font></a>"

def table(rows, widths, header=True):
    data = []
    for i, r in enumerate(rows):
        data.append([Paragraph(str(c), cellb if (header and i == 0) else cell) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.5, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT])]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    t.setStyle(TableStyle(st))
    return t

def module(heading, does, proofs, lesson):
    items = [P(heading, h1), P("<b>What it does.</b> " + does)]
    items.append(P("<b>One proof.</b>"))
    items += [B(p) for p in proofs]
    items.append(P("<b>One lesson.</b> " + lesson))
    items.append(Spacer(1, 4))
    return items

# ---------------- diagrams ----------------
class Arch(Flowable):
    def __init__(self, w=504, h=150):
        super().__init__(); self.width, self.height = w, h
    def box(self, c, x, y, w, h, t1, t2="", fill=SOFT):
        c.setFillColor(fill); c.setStrokeColor(NAVY); c.setLineWidth(0.8)
        c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + w / 2, y + h - 12, t1)
        c.setFont("Helvetica", 7)
        for i, ln in enumerate(t2.split("|")):
            c.drawCentredString(x + w / 2, y + h - 23 - 9 * i, ln)
    def arrow(self, c, x1, y1, x2, y2):
        c.setStrokeColor(GREY); c.setFillColor(GREY); c.setLineWidth(1)
        c.line(x1, y1, x2, y2)
        if y1 == y2:
            c.line(x2, y2, x2 - 4, y2 + 2.5); c.line(x2, y2, x2 - 4, y2 - 2.5)
        else:
            c.line(x2, y2, x2 - 2.5, y2 + 4); c.line(x2, y2, x2 + 2.5, y2 + 4)
    def draw(self):
        c = self.canv; w, h, g = 88, 62, 16
        y = 70
        xs = [i * (w + g) for i in range(5)]
        self.box(c, xs[0], y, w, h, "1. RAW", "29 CSV feeds|schema raw|never edited")
        self.box(c, xs[1], y, w, h, "2. ETL (etl.py)", "contract checks|bad rows leave|the pipeline")
        self.box(c, xs[2], y, w, h, "3. CLEAN + STAR", "clean, warehouse|dims + 12 facts|SCD2 employees")
        self.box(c, xs[3], y, w, h, "4. METRIC LAYER", "metrics.* views|one definition|per KPI + privacy")
        self.box(c, xs[4], y, w, h, "5. CONSUME", "Streamlit app|FastAPI (local)|PDF report builder")
        for i in range(4):
            self.arrow(c, xs[i] + w, y + h / 2, xs[i + 1], y + h / 2)
        self.box(c, xs[1], 4, w, 42, "QUARANTINE", "rejected rows +|reason", fill=colors.HexColor("#FEE2E2"))
        self.arrow(c, xs[1] + w / 2, y, xs[1] + w / 2, 46)
        self.box(c, xs[2], 4, w, 42, "DQ GATEKEEPER", "14 checks|pulseiq_doctor.py", fill=colors.HexColor("#DCFCE7"))
        self.arrow(c, xs[2] + w / 2, y, xs[2] + w / 2, 46)
        c.setFont("Helvetica-Oblique", 7); c.setFillColor(GREY)
        c.drawString(xs[3], 24, "Rule: rows in = clean rows + quarantined rows")
        c.drawString(xs[3], 14, "Every layer reads only from the layer before.")

class Star(Flowable):
    def __init__(self, w=504, h=150):
        super().__init__(); self.width, self.height = w, h
    def draw(self):
        c = self.canv
        def box(x, y, w, h, t, fill):
            c.setFillColor(fill); c.setStrokeColor(NAVY); c.setLineWidth(0.8)
            c.roundRect(x, y, w, h, 3, fill=1, stroke=1)
            c.setFillColor(INK); c.setFont("Helvetica-Bold", 7.5)
            lines = t.split("|")
            for i, ln in enumerate(lines):
                c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", 7.5 if i == 0 else 6.8)
                c.drawCentredString(x + w / 2, y + h - 11 - 9 * i, ln)
        facts = [("fact_payroll", 118), ("fact_attendance_monthly", 84), ("fact_ledger", 50), ("fact_task", 16)]
        fx, fw, fh = 10, 150, 26
        dims = [("dim_employee|SCD Type 2: valid_from,|valid_to, is_current", 100, 54),
                ("dim_department|includes node 'ALL'|for company-wide rows", 20, 54)]
        dx, dw = 330, 165
        coords = {}
        for name, y in facts:
            box(fx, y, fw, fh, name + "|(fact table)", colors.HexColor("#DBEAFE")); coords[name] = (fx + fw, y + fh / 2)
        dcoords = {}
        for t, y, h in dims:
            box(dx, y, dw, h, t, colors.HexColor("#DCFCE7")); dcoords[t.split("|")[0]] = (dx, y + h / 2)
        c.setStrokeColor(GREY); c.setLineWidth(0.7)
        for name, _ in facts:
            x1, y1 = coords[name]
            x2, y2 = dcoords["dim_department"]; c.line(x1, y1, x2, y2)
            if name != "fact_ledger":
                x2, y2 = dcoords["dim_employee"]; c.line(x1, y1, x2, y2)
        c.setFont("Helvetica-Oblique", 7); c.setFillColor(GREY)
        c.drawString(10, 2, "Simplified view: the warehouse has 10 dimensions and 12 fact tables; four facts and two shared dimensions are drawn.")
        c.drawString(10, 146, "Unknown employee rows map to surrogate key -1, so no financial row is dropped.")

# ---------------- page furniture ----------------
class Numbered(canvas.Canvas):
    def __init__(self, *a, **k):
        super().__init__(*a, **k); self._pages = []
    def showPage(self):
        self._pages.append(dict(self.__dict__)); self._startPage()
    def save(self):
        n = len(self._pages)
        for st in self._pages:
            self.__dict__.update(st)
            self.setFont("Helvetica-Bold", 8); self.setFillColor(GREY)
            self.drawString(54, 758, "AURA WORKFORCE BY GROWMAR  |  PULSEIQ ANALYTICS  |  CONSOLIDATED PROJECT REPORT")
            self.setStrokeColor(LINE); self.line(54, 751, 558, 751); self.line(54, 44, 558, 44)
            self.setFont("Helvetica", 8)
            self.drawString(54, 32, f"{NAME}  |  Data Analytics Internship  |  Zenith Nova Technologies case study")
            self.drawRightString(558, 32, f"Page {self._pageNumber} of {n}")
            super().showPage()
        super().save()

def build(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=54, rightMargin=54,
                            topMargin=62, bottomMargin=58, title="PulseIQ Consolidated Project Report",
                            author=NAME)
    s = []

    # ---- 1 Cover
    s += [Spacer(1, 6), P("PulseIQ Analytics", title),
          P("Consolidated Project Report: workforce, finance and delivery analytics on one governed warehouse", sub)]
    cover = [
        ["Candidate", NAME],
        ["Track / programme", "Data Analytics internship (Growmar)"],
        ["Case-study company", "Zenith Nova Technologies (HR, Finance, Commercial, Engineering)"],
        ["GitHub repository", link(GITHUB)],
        ["Live dashboard", link(LIVE)],
        ["Demo video (unlisted)", link(VIDEO, "Watch the 5-minute demo on Google Drive")],
        ["Git tags", "phase-1, phase-2, phase-4, v1.0.0-rc1, v1.0.0, v1.0.1"],
        ["Final-challenge branch", "feature/pulseiq-doctor-diagnostics"],
        ["Report date", "21 November 2026"],
    ]
    s.append(table(cover, [130, 374], header=False))
    s += [Spacer(1, 10), P("Summary", h2),
          P("PulseIQ turns 29 raw company data feeds into one checked star-schema warehouse in DuckDB. "
            "A governed metric layer gives every KPI one definition. The same numbers feed a live Streamlit dashboard, "
            "a self-service KPI explorer with small-group privacy rules, a FastAPI metrics service (tested locally), "
            "an automated monthly report builder and a board presentation. A diagnostic tool, <font face='Courier'>pulseiq_doctor.py</font>, "
            "checks the whole platform in one command."),
          P("How to read this report", h2),
          P("Section 1 explains the problem. Section 2 shows the architecture and star schema. Sections 3 to 7 cover the five modules "
            "(what it does, one proof, one lesson). Section 8 follows one number from a raw row to the dashboard. "
            "Sections 9 and 10 give reconciliation, data quality and how to test the live link. "
            "Sections 11 and 12 cover challenges, mistakes, honest limits and the final challenge."),
          PageBreak()]

    # ---- 2 One page
    s += [P("1. The project in one page", h1),
          P("The problem", h2),
          P("In many companies, HR, Finance, Sales and Engineering keep their numbers in separate files. Leaders then see different answers "
            "to the same question: payroll does not match the ledger, resignations are noticed late, overdue invoices squeeze cash, "
            "and a small team report can reveal one person's salary. PulseIQ gives one trusted place for people, cost and cash."),
          P("The users", h2),
          table([["User", "What they need"],
                 ["CEO", "One view of headcount, cost and cash, with a clear data cut-off date"],
                 ["CFO", "Payroll reconciled to the general ledger; receivables and DSO"],
                 ["HR / People lead", "Attrition, attendance and overtime signals, without exposing individuals"],
                 ["Engineering managers", "Sprint delivery numbers and a self-service explorer that hides small groups"],
                 ["Auditors / reviewers", "Data contracts, quarantine of bad rows, and lineage from raw file to dashboard"]],
                [120, 384]),
          Spacer(1, 6), P("What was built", h2)]
    for t in [
        "<b>ETL pipeline</b> (<font face='Courier'>etl.py</font>): checks 29 feeds against data contracts; bad rows go to a quarantine schema.",
        "<b>Star-schema warehouse</b> (<font face='Courier'>warehouse.py</font>): conformed dimensions, 12 fact tables, SCD Type 2 employee history.",
        "<b>Data-quality gatekeeper</b> (<font face='Courier'>dq_gatekeeper.py</font>): 14 SQL checks, tested with deliberately injected faults.",
        "<b>Governed metric layer</b> (<font face='Courier'>metric_layer.py</font>): metrics.* SQL views, one definition per KPI.",
        "<b>Streamlit dashboard</b> (<font face='Courier'>app.py</font> and pages): six pages, role simulator, data-freshness line.",
        "<b>KPI Explorer</b> with role views (ADMIN, HR, MANAGER, EXECUTIVE) and small-group suppression.",
        "<b>Metrics API</b> (<font face='Courier'>api.py</font>, FastAPI): five metrics, Swagger docs, lineage endpoint. Tested locally.",
        "<b>Report builder</b> (<font face='Courier'>build_report.py</font>), <b>board pack</b> (10 slides) and <b>pulseiq_doctor.py</b> (platform diagnostic)."]:
        s.append(B(t))
    s.append(PageBreak())

    # ---- 3 Architecture
    s += [P("2. Architecture and star schema", h1),
          P("Architecture diagram", h2), Arch(), Spacer(1, 8),
          P("Star schema", h2), Star(), Spacer(1, 8),
          table([["Layer", "Schema", "Contents", "Guarantee"],
                 ["Raw", "raw", "29 source feeds", "Loaded as received; never edited"],
                 ["Quarantine", "quarantine", "12 defect tables", "Rejected rows with a written reason"],
                 ["Clean", "clean", "12 clean fact tables", "Rows in = clean + quarantined"],
                 ["Warehouse", "warehouse", "10 dimensions, 12 facts", "Surrogate keys; SCD Type 2 employees"],
                 ["Metric layer", "metrics", "32 governed views", "One SQL definition per KPI; privacy masking"],
                 ["Consumers", "app / API / PDF", "Streamlit, FastAPI, ReportLab", "Read from metrics.* only"]],
                [70, 80, 150, 204]),
          Spacer(1, 6),
          P("<b>Why SCD Type 2 for employees?</b> If someone moves department mid-year, their earlier pay stays with the earlier department. "
            "<b>Why an unknown row (-1)?</b> A payroll or ledger row with an unmatched employee is kept and counted, not silently dropped. "
            "<b>Why department 'ALL'?</b> Company-wide budget and ledger rows need a valid department key."),
          PageBreak()]

    # ---- 4-8 modules
    s += module("3. Module 1: Data Foundations and Governance (Tasks 1 to 5)",
        "Loads 29 feeds, checks column contracts and types, sends bad rows to quarantine, builds the star schema, "
        "runs 14 SQL data-quality checks and creates the metric catalogue.",
        ["Clean rows equal warehouse rows in all 12 fact tables (checked by <font face='Courier'>pulseiq_doctor.py</font>). Examples: "
         "fact_payroll 7,342 = 7,342; fact_attendance_monthly 7,343 = 7,343; fact_ledger 6,784 = 6,784; fact_task 28,848 = 28,848 "
         "(20 bad tasks were already quarantined upstream).",
         "Fault injection: 7 deliberately broken records (unbalanced ledger entry, duplicate payroll row, backward task dates) were all caught by the gatekeeper."],
        "Never change raw data in place. If every excluded row has a written reason, a finance reviewer can trust the totals.")
    s += module("4. Module 2: People Analytics (Tasks 6 and 7)",
        "Shows headcount, attrition, leave and attendance patterns, and an attrition-risk signal, so leaders can see workforce stability.",
        ["September 2026: active headcount (M01) 441, up from 420 (+5.0%). Monthly attrition (M04) 0.70%, about 8.4% a year "
         "(0.70% x 12) against a 12.0% board ceiling. Attendance (M13) 95.19% (8,828 effective present days / 9,274 scheduled days).",
         "Work mode: hybrid 64.9%, on-site 23.6%, remote 11.5%. Regional centres (Coimbatore, Kochi, Erode) hold 34.2% of staff."],
        "Use average headcount as the attrition denominator: exits / ((start headcount + end headcount) / 2). "
        "Start headcount overstates turnover in a growing team and end headcount understates it.")
    s.append(PageBreak())
    s += module("5. Module 3: Finance and Cost Analytics (Tasks 9 to 12)",
        "Combines employer payroll cost, the general-ledger trial balance, budget variance, invoices and receivables ageing.",
        ["April 2025 gross pay (M07) INR 52,740,110.43 and employer payroll cost (M09) INR 53,363,392.08 match the official answer key exactly.",
         "Ledger trial balance: debits minus credits = INR 0.00 across all 6,784 entries.",
         "Receivables: INR 64.8M outstanding, DSO 58.4 days; INR 14.2M (22.0%) is past Net 30 terms and sits with 3 enterprise clients waiting on milestone sign-off. "
         "Operating margin (M18) is 18.25% (INR 18.06M profit on INR 98.97M revenue)."],
        "Reconcile payroll to the ledger on employer cost, not net pay. Employer PF and statutory contributions are real company expenses; "
        "comparing net take-home pay to ledger debits gives false differences.")
    s += module("6. Module 4: Intelligence and Storytelling (Tasks 8, 13, 14, 15)",
        "Links delivery, overtime, risk signals and transaction anomalies, and brings them together in the Executive Health Scorecard.",
        ["Across 430 active staff, people logging more than 15 overtime hours a month were 3.2 times more likely to have a high attrition-risk score. "
         "This is an association, not proof of cause.",
         "Engineering: 28,848 tasks, 89.3% on-time (M23), average cycle time 3.8 days (M25).",
         "Anomaly check flagged 1.8% of transactions, including a June 2026 difference of INR 18,450.00."],
        "Cross-team numbers raise better questions. For example, high overtime in support may be linked to release practices in engineering. "
        "That is a hypothesis to test with more data, not a conclusion.")
    s.append(PageBreak())
    s += module("7. Module 5: Go-Live, Privacy and Release (Tasks 16 to 20)",
        "Packages PulseIQ for use: automated monthly report, live cloud dashboard, KPI explorer with privacy rules, metrics API with lineage, "
        "10-slide board pack and a tagged release.",
        ["Privacy test: queries for the Executive Office (D00, n=1) and Design Systems (T07, n=2) were masked as [SUPPRESSED], "
         "so one person's pay or attrition risk cannot be read.",
         "API check (<font face='Courier'>test_api.py</font>, run locally): five endpoints match the warehouse. Headcount 441, attrition 0.70%, "
         "payroll cost INR 55,519,621.87, attendance 95.19%, operating margin 18.25%. The lineage endpoint also returned correctly.",
         "<font face='Courier'>pulseiq_doctor.py</font> (20 Nov 2026): 8 of 8 checks passed (environment, database, row reconciliation, "
         "referential integrity, 32 metric views, privacy mask, API health)."],
        "Put privacy rules in the SQL view layer, not only in the screen. Then every tool that reads the views gets the same protection.")

    # ---- 9 Lineage
    s += [P("8. How the modules connect: one number from raw data to dashboard", h1),
          P("The number traced here is <b>September 2026 employer payroll cost, INR 55,519,621.87</b>."),
          table([["Hop", "Object", "What happens"],
                 ["1. Raw", "raw fact_payroll feed", "Employer cost recorded per employee-month; loaded unchanged."],
                 ["2. ETL", "etl.py", "Column contract and arithmetic checks; bad rows go to quarantine."],
                 ["3. Star schema", "warehouse.py", "Surrogate employee keys added; clean rows = warehouse rows (7,342 = 7,342); 0 orphan keys."],
                 ["4. Quality gate", "dq_gatekeeper.py (DQ-C01)", "Payroll employer cost compared with ledger payroll accounts. September matches; the June 2026 exception is described in section 9."],
                 ["5. Metric layer", "metrics.m09_payroll_cost", "One SQL view defines the metric. Value: INR 55,519,621.87."],
                 ["6. API", "GET /api/v1/metrics/payroll-cost", "Reads the view; does not recalculate. Same value in the JSON response."],
                 ["7. Dashboard", "Streamlit pages", "Read the same metric views, so the dashboard and API share one definition."]],
                [80, 150, 274]),
          Spacer(1, 6),
          P("<b>Rename test.</b> If the raw column <font face='Courier'>employer_cost</font> were renamed, the pipeline should stop at the "
            "ETL schema check. If that check were bypassed, the payroll metric views would fail and the API and dashboard pages that use them would error. "
            "This impact analysis is documented in the Task 19 lineage notes and served by the <font face='Courier'>/api/v1/lineage</font> endpoint."),
          PageBreak()]

    # ---- 10 Reconciliation + DQ
    s += [P("9. Reconciliation and data-quality results", h1),
          table([["Check", "Result", "Evidence"],
                 ["Clean rows vs warehouse rows (12 fact tables)", "100% match", "pulseiq_doctor.py, 20 Nov 2026"],
                 ["Orphan keys, fact_payroll to dim_employee", "0 found", "pulseiq_doctor.py"],
                 ["Ledger trial balance (6,784 entries)", "Debits - credits = INR 0.00", "DQ gatekeeper"],
                 ["Payroll vs official answer key (April 2025)", "Exact match (M07 and M09)", "Module 3"],
                 ["API vs warehouse (5 metrics + lineage)", "All matched", "test_api.py, run locally"],
                 ["Privacy mask, Executive Office (D00, n=1)", "Masked", "pulseiq_doctor.py"],
                 ["Metric views compiled", "32 views accessible", "pulseiq_doctor.py"],
                 ["Fault-injection test (7 injected defects)", "All 7 caught", "Gatekeeper test vault"],
                 ["Small-group masking (DQ-C14)", "81 sub-threshold groups masked", "DQ gatekeeper"]],
                [210, 150, 144]),
          Spacer(1, 6),
          P("Known exceptions (explained, not hidden)", h2),
          B("<b>June 2026:</b> DQ-C01 found a difference of INR 18,450.00 between payroll and ledger. It was isolated and explained; "
            "the same amount appears in the anomaly check. It does not affect the September 2026 figures used above."),
          B("<b>Headcount 440 vs 441:</b> the Executive Overview card on the live dashboard shows 440, while metric M01 for September 2026 "
            "and the API show 441. I have not yet traced the reason (it may be a different reference month or an export timing difference). "
            "I list it as an open item in section 12 instead of changing a number."),
          Spacer(1, 6),
          P("10. Live dashboard and how to test it", h1),
          P(f"Live link: {link(LIVE)}. Opened by the author on 21 November 2026; the landing page, sidebar and Executive Overview load without a login."),
          B("Open the link in a private (incognito) window or on a phone. No account is needed."),
          B("The landing page shows the data-freshness line: dashboard exports last refreshed 19 Nov 2026, 18:57 UTC (file timestamps, not a live feed)."),
          B("Use the sidebar: Executive Overview, Workforce Overview, Financial Overview, Receivables Overview, Anomaly Overview, KPI Explorer."),
          B("In KPI Explorer, choose a very small team or the Executive Office: the value is hidden by the small-group rule."),
          B("The role selector (ADMIN, HR, MANAGER, EXECUTIVE) is a demo. The app states that it is not a login system and must not be used as production security."),
          PageBreak()]

    # ---- 11 challenges
    s += [P("11. Challenges, mistakes and what I learned", h1),
          P("Challenges", h2),
          table([["Challenge", "How I solved it"],
                 ["Report builder broke when a department was added", "Used outer joins on dim_department instead of a fixed list of departments."],
                 ["Small teams could reveal one person's pay or attrition", "Added suppression rules in the SQL views (groups below the minimum size are masked)."],
                 ["FastAPI default parameters caused a DuckDB binder error", "Wrote a helper that resolves the default values so endpoints work over HTTP and in Python."],
                 ["Streamlit deprecated use_container_width for charts", "Changed chart calls to width='stretch'."]],
                [190, 314]),
          P("Mistakes I made", h2),
          B("<b>I first described the API test as 'pytest: 5 passed'.</b> test_api.py is a plain script, so pytest found no tests. "
            "I ran the script directly, saw all checks pass, and now describe it correctly."),
          B("<b>The first live deployment was connected to a different Streamlit account.</b> The dashboard code was mine, but the hosting was not. "
            "I redeployed from my own account and updated the link in every file and report."),
          B("<b>The scheduled refresh failed on GitHub.</b> The workflow needs raw data files that are not stored in the repository. "
            "I switched the schedule off and documented the limit rather than leaving a red failure."),
          B("<b>I almost left numbers that disagreed.</b> The attrition rate appeared as 0.68% in one place and 0.70% in another. "
            "I rechecked and used 0.70%, the value the metric view returns."),
          P("What I learned", h2),
          B("One metric definition used everywhere is what stops the dashboard, API and reports from disagreeing."),
          B("Privacy is a design choice made early. Small groups are the real risk in a company of this size."),
          B("A check that never fails proves nothing. Injecting faults showed that the checks really catch problems."),
          B("Saying what the data cannot support is part of the analysis. I would not recommend cutting sales staff or blaming managers for turnover, "
            "because the warehouse has no customer-acquisition cost, pipeline or exit-interview data."),
          P("I also learned to check every statement against evidence before writing it, and to say clearly when something is not finished.", body),
          PageBreak()]

    # ---- 12 limits + final challenge
    s += [P("12. Honest limits and the final challenge", h1),
          P("Honest limits", h2),
          B("<b>The API is not hosted online.</b> It runs locally and passed its checks. A Dockerfile is ready for Render, but I have not deployed it, so there is no public API link."),
          B("<b>Scheduled refresh is switched off.</b> The ETL refresh works on my computer. The GitHub Actions run failed because the raw source files are not in the repository. "
            "The workflow can still be started by hand."),
          B("<b>The role selector is a demo, not security.</b> The app does not authenticate users."),
          B("<b>Open item:</b> dashboard headcount card (440) differs from metric M01 and the API (441). The cause is not yet confirmed."),
          B("<b>Free hosting:</b> the dashboard runs on Streamlit Community Cloud. It may sleep when idle and load slowly the first time."),
          B("<b>Data freshness</b> reflects export file timestamps, not a live link to source systems."),
          B("<b>Weak-evidence recommendation I will not make:</b> cutting sales or marketing headcount, or blaming managers for turnover. "
            "The data has no customer-acquisition cost, pipeline stages or exit-interview themes to support it."),
          P("Final challenge (own branch: feature/pulseiq-doctor-diagnostics)", h2),
          P("<b>What I built:</b> <font face='Courier'>pulseiq_doctor.py</font>, one command that checks the platform. "
            "<b>Why:</b> before this I ran several scripts and read logs by hand. Now one command checks dependencies, database file, schemas, "
            "row reconciliation, referential integrity, metric views, the privacy mask and API health, and prints PASS or FAIL for each. "
            "<b>Result:</b> all 8 checks passed on 20 November 2026."),
          P("What I would improve next", h2),
          B("Deploy the API on a free hosting service and add its public health-check link."),
          B("Add the raw data (or a small sample) to the repository so the scheduled refresh can run, then run pulseiq_doctor.py in GitHub Actions."),
          B("Find the cause of the 440 vs 441 headcount difference and add a check that compares the dashboard card with the metric view."),
          B("Add customer-acquisition and exit-survey data so sales and turnover questions can be answered with evidence."),
          Spacer(1, 10),
          table([["Prepared by", f"{NAME}, Data Analytics intern"],
                 ["Repository", link(GITHUB)],
                 ["Release tag", "v1.0.1 (v1.0.0 = Phase 4 release; v1.0.1 adds live-URL update, API deployment files, documentation)"]],
                [90, 414], header=False)]

    doc.build(s, canvasmaker=Numbered)
    print("Built", path)

if __name__ == "__main__":
    for p in OUT_COPIES:
        build(p)
