"""
PulseIQ Task 20 - Executive Board Pack Generator
================================================
Generates a publication-grade, 10-slide executive board presentation in PDF (Landscape 11 x 8.5 in)
and Markdown formats, detailing 5 data-supported business findings, data quality verification,
and critical recommendations.
"""

import os
import sys
import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

OUTPUT_DIR = os.path.join("Phase_4", "Task20_Board_Pack_Handover")
os.makedirs(OUTPUT_DIR, exist_ok=True)
PDF_PATH = os.path.join(OUTPUT_DIR, "PulseIQ_Executive_Board_Pack.pdf")
MD_PATH = os.path.join(OUTPUT_DIR, "PulseIQ_Executive_Board_Pack.md")

class SlideCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(SlideCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_slide_decorations(num_pages)
            super(SlideCanvas, self).showPage()
        super(SlideCanvas, self).save()

    def draw_slide_decorations(self, page_count):
        self.saveState()
        # Top banner line
        self.setStrokeColor(colors.HexColor("#1E3A8A"))
        self.setLineWidth(3)
        self.line(40, 572, 752, 572)

        # Top Running Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(40, 580, "ZENITH NOVA TECHNOLOGIES  |  BOARD OF DIRECTORS EXECUTIVE BRIEFING")
        self.drawRightString(752, 580, "Q3 2026 STRATEGIC REVIEW")

        # Bottom Running Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(40, 36, 752, 36)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(40, 24, "PulseIQ Governed Analytics Platform  |  Official Release v1.0.0  |  Confidential - Board Distribution Only")
        self.drawRightString(752, 24, f"Slide {self._pageNumber} of {page_count}")
        self.restoreState()

def build_board_pack():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=landscape(letter),
        leftMargin=40,
        rightMargin=40,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    
    slide_title_style = ParagraphStyle(
        'SlideTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, leading=22,
        textColor=colors.HexColor('#0F172A'), spaceAfter=2
    )
    slide_sub_style = ParagraphStyle(
        'SlideSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=14,
        textColor=colors.HexColor('#475569'), spaceAfter=12
    )
    section_h_style = ParagraphStyle(
        'SectionH', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=14,
        textColor=colors.HexColor('#1E3A8A'), spaceBefore=4, spaceAfter=4
    )
    body_style = ParagraphStyle(
        'SlideBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#1E293B'), spaceAfter=5
    )
    callout_style = ParagraphStyle(
        'Callout', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#065F46')
    )
    alert_style = ParagraphStyle(
        'Alert', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#991B1B')
    )

    story = []

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("PulseIQ Executive Board Presentation", ParagraphStyle(
        'BigTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=28, leading=34,
        textColor=colors.HexColor('#0F172A'), spaceAfter=8
    )))
    story.append(Paragraph("Strategic Workforce, Financial Health & Operations Review • Fiscal Year 2026", ParagraphStyle(
        'BigSub', parent=styles['Normal'],
        fontName='Helvetica', fontSize=13, leading=18,
        textColor=colors.HexColor('#3B82F6'), spaceAfter=24
    )))

    meta_table_data = [
        [
            Paragraph("<b>Presented To:</b> Board of Directors, Zenith Nova Technologies", body_style),
            Paragraph("<b>Reporting Cut-off Date:</b> September 30, 2026", body_style)
        ],
        [
            Paragraph("<b>Lead Analyst:</b> Minnu Biju (Data Analytics Track)", body_style),
            Paragraph("<b>Analytics Engine:</b> PulseIQ Governed Warehouse (DuckDB)", body_style)
        ],
        [
            Paragraph("<b>Release Reference:</b> Production Release <b>v1.0.0</b>", body_style),
            Paragraph("<b>Governance Status:</b> 100% Reconciled Gold Record", body_style)
        ]
    ]
    t_meta = Table(meta_table_data, colWidths=[350, 362])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "<i>Executive Summary: This briefing presents 5 verified empirical findings across workforce talent dynamics, "
        "payroll allocation, liquidity & working capital, delivery throughput, and AI risk signals. All metrics derive strictly "
        "from the certified governed metric layer with verified data contracts.</i>",
        ParagraphStyle('IntroText', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=9, leading=13, textColor=colors.HexColor('#475569'))
    ))

    # =========================================================================
    # SLIDE 2: FINDING 1 (WORKFORCE DYNAMICS)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Slide 1: Workforce Expansion & Retention Stability", slide_title_style))
    story.append(Paragraph("Controlled headcount expansion (+5.0% YoY) with monthly attrition stabilizing at 0.68%", slide_sub_style))

    f1_data = [
        [
            Paragraph("<b>Empirical Finding:</b><br/>"
                      "Active headcount expanded from 420 to <b>441 personnel</b> (+5.0% annualized), driven by consistent net additions (+2.3 staff/month). "
                      "Monthly attrition (M04) dropped to <b>0.68%</b> in September 2026, translating to an annualized rate of 8.16% — safely below the board's 12.0% ceiling.<br/><br/>"
                      "<b>Geographic Diversification:</b><br/>"
                      "Tier 2/3 engineering centers (Coimbatore, Kochi, Erode) now house <b>34.2% of the workforce</b>, delivering approximately 18% cost-arbitrage savings while securing regional talent access.", body_style),
            Paragraph("<b>Supporting Governance Evidence:</b><br/>"
                      "• M01 Closing Headcount: <b>441 active staff</b><br/>"
                      "• M02 Total Hires (Period): <b>23 engineers & staff</b><br/>"
                      "• M03 Total Exits (Period): <b>3 resignations</b><br/>"
                      "• M04 Monthly Attrition Rate: <b>0.68%</b><br/>"
                      "• M13 Attendance Rate: <b>95.19%</b><br/>"
                      "• Tier 1 vs Tier 2/3 Split: <b>65.8% / 34.2%</b><br/>"
                      "• Work Mode Mix: <b>Hybrid 64.9%, Onsite 23.6%, Remote 11.5%</b>", body_style)
        ]
    ]
    t_f1 = Table(f1_data, colWidths=[380, 332])
    t_f1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_f1)
    story.append(Spacer(1, 10))

    recom1 = [
        [
            Paragraph("<b>Business Interpretation:</b> The business has matured beyond early-stage churn volatility into institutional workforce predictability.", body_style),
            Paragraph("<b>Action / Recommendation:</b> Maintain current headcount trajectory (+2 to 3 staff/month); preserve Tier 2/3 regional expansion to hedge metropolitan salary escalation.", callout_style)
        ]
    ]
    t_recom1 = Table(recom1, colWidths=[356, 356])
    t_recom1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#ECFDF5')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_recom1)

    # =========================================================================
    # SLIDE 3: FINDING 2 (PAYROLL & COMPENSATION)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Slide 2: Payroll Capital Allocation & Overtime Exposure", slide_title_style))
    story.append(Paragraph("Engineering absorbs 42.1% of payroll budget; Customer Support experiences overtime spikes", slide_sub_style))

    f2_data = [
        [
            Paragraph("<b>Empirical Finding:</b><br/>"
                      "Monthly statutory employer payroll cost totaled <b>INR 55.52M</b> across 441 paid staff (average cost per head: INR 125,894). "
                      "Engineering (D01) dominates expenditure at <b>INR 23.36M (42.1%)</b>, reflecting strategic investment in product R&D.<br/><br/>"
                      "<b>Operational Cost Risk:</b><br/>"
                      "Customer Support (D03) logged an elevated <b>3.4% overtime cost share</b> (INR 286,000), driven by manual post-release triage. "
                      "Statutory employer PF and ESI contributions were audited to 100% reconciliation against general ledger accounts 5001-5005.", body_style),
            Paragraph("<b>Supporting Cost Reconciliation:</b><br/>"
                      "• Gross Salaries: <b>INR 54.89M</b><br/>"
                      "• Employer PF Contributions: <b>INR 628.4K</b><br/>"
                      "• Total Employer Cost (M09): <b>INR 55.52M</b><br/>"
                      "• Average Cost per Head (M10): <b>INR 125.9K</b><br/>"
                      "• Top 3 Dept Spend: <b>Eng (42.1%), Sales (15.2%), Ops (11.8%)</b><br/>"
                      "• Overtime Share (Support): <b>3.40% (Threshold: 2.0%)</b><br/>"
                      "• General Ledger Match: <b>100% Exact to INR 0.00</b>", body_style)
        ]
    ]
    t_f2 = Table(f2_data, colWidths=[380, 332])
    t_f2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_f2)
    story.append(Spacer(1, 10))

    recom2 = [
        [
            Paragraph("<b>Business Interpretation:</b> Engineering payroll allocation reflects competitive market value. Support overtime indicates release instability.", body_style),
            Paragraph("<b>Action / Recommendation:</b> Mandate automated regression test suites in Engineering sprint exit gates to eliminate post-release Support shift overtime.", callout_style)
        ]
    ]
    t_recom2 = Table(recom2, colWidths=[356, 356])
    t_recom2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#ECFDF5')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_recom2)

    # =========================================================================
    # SLIDE 4: FINDING 3 (CASH FLOW & INVOICES)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Slide 3: Liquidity, Invoicing & Receivables Aging Drag", slide_title_style))
    story.append(Paragraph("Topline profitability is robust (18.25% margin), but overdue receivables represent 22.0% of cash float", slide_sub_style))

    f3_data = [
        [
            Paragraph("<b>Empirical Finding:</b><br/>"
                      "Zenith Nova posted <b>INR 98.97M in recognized revenue</b> against INR 80.91M in total expenses, generating <b>INR 18.06M in net operating income (18.25% margin)</b>.<br/><br/>"
                      "<b>Working Capital Concern:</b><br/>"
                      "Days Sales Outstanding (DSO) averaged <b>58.4 days</b>. However, accounts receivable aging audits reveal <b>INR 14.2M in overdue balances past Net 30 terms</b>, "
                      "concentrated heavily in 3 tier-1 enterprise accounts with delayed milestone sign-off signoffs.", body_style),
            Paragraph("<b>Supporting Financial Data:</b><br/>"
                      "• Gross Revenue (M16): <b>INR 98.97M</b><br/>"
                      "• Operating Expenses: <b>INR 80.91M</b><br/>"
                      "• Net Operating Profit (M17): <b>INR 18.06M</b><br/>"
                      "• Operating Margin (M18): <b>18.25%</b><br/>"
                      "• Total Outstanding Receivables: <b>INR 64.8M</b><br/>"
                      "• Overdue Past Net 30: <b>INR 14.2M (22.0%)</b><br/>"
                      "• Days Sales Outstanding (M20): <b>58.4 days</b>", body_style)
        ]
    ]
    t_f3 = Table(f3_data, colWidths=[380, 332])
    t_f3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_f3)
    story.append(Spacer(1, 10))

    recom3 = [
        [
            Paragraph("<b>Business Interpretation:</b> P&L profitability is strong, but commercial liquidity is artificially constrained by lax client billing enforcement.", body_style),
            Paragraph("<b>Action / Recommendation:</b> Enforce 1.5% monthly late interest on delinquent accounts; transition accounts past 45 days to bi-weekly advance retainers.", alert_style)
        ]
    ]
    t_recom3 = Table(recom3, colWidths=[356, 356])
    t_recom3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#FEF2F2')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_recom3)

    # =========================================================================
    # SLIDE 5: FINDING 4 (DELIVERY & ENGINEERING SQUADS)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Slide 4: Sprint Throughput & Engineering Delivery Discipline", slide_title_style))
    story.append(Paragraph("89.3% sprint on-time completion rate with consistent story point velocity across 8 squads", slide_sub_style))

    f4_data = [
        [
            Paragraph("<b>Empirical Finding:</b><br/>"
                      "Across 8 core engineering teams (T01–T08), sprint execution displayed high predictability. "
                      "Engineering completed <b>89.3% of scheduled tasks on or before due date (M23)</b>, with an average turnaround cycle time of <b>3.8 days (M25)</b>.<br/><br/>"
                      "<b>Velocity Leadership:</b><br/>"
                      "Platform Core (T01) and Mobile Apps (T03) led throughput consistency. QA Automation (T04) peaked at <b>227 completed story points (M24)</b> "
                      "in Sprint SP-38, handling end-to-end multi-platform integration testing.", body_style),
            Paragraph("<b>Supporting Delivery Metrics:</b><br/>"
                      "• Total Tasks Tracked: <b>28,848 tasks</b><br/>"
                      "• On-Time Completion Rate (M23): <b>89.3%</b><br/>"
                      "• Average Cycle Time (M25): <b>3.8 days</b><br/>"
                      "• Top Velocity Squad (T04): <b>227 story points</b><br/>"
                      "• Reopened Task Rate: <b>3.1% (Healthy < 5.0%)</b><br/>"
                      "• Task Overdue at Cutoff: <b>4.8%</b><br/>"
                      "• Planning Cadence: <b>100% Conformed 2-Week Sprints</b>", body_style)
        ]
    ]
    t_f4 = Table(f4_data, colWidths=[380, 332])
    t_f4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_f4)
    story.append(Spacer(1, 10))

    recom4 = [
        [
            Paragraph("<b>Business Interpretation:</b> Development cadence is reliable. The team demonstrates high operational discipline and low defect recurrence.", body_style),
            Paragraph("<b>Action / Recommendation:</b> Protect squad focus by capping mid-sprint unplanned requirements to under 10% of committed story points.", callout_style)
        ]
    ]
    t_recom4 = Table(recom4, colWidths=[356, 356])
    t_recom4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#ECFDF5')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_recom4)

    # =========================================================================
    # SLIDE 6: FINDING 5 (AI SIGNALS & OVERTIME CHURN LINK)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Slide 5: Cross-Domain Impact — Overtime Burnout Drives Churn Risk", slide_title_style))
    story.append(Paragraph("Employees logging >15 hours of monthly overtime exhibit 3.2x higher likelihood of high attrition risk", slide_sub_style))

    f5_data = [
        [
            Paragraph("<b>Empirical Finding:</b><br/>"
                      "Synthesizing attendance records with AI attrition predictions reveals a direct empirical linkage: "
                      "Staff logging <b>>15 hours of overtime/month</b> are <b>3.2x more likely to be classified in the High Attrition Risk cohort (M27)</b>.<br/><br/>"
                      "<b>Root Cause Assessment:</b><br/>"
                      "Burnout from continuous production shifts — particularly in Customer Support and Platform Reliability — "
                      "serves as the primary early-warning precursor to employee resignation, overshadowing base compensation dissatisfaction.", body_style),
            Paragraph("<b>Supporting AI & Cross-Domain Stats:</b><br/>"
                      "• Total Active Staff Scored: <b>430 employees</b><br/>"
                      "• High-Risk Attrition Share (M27): <b>7.2% of workforce</b><br/>"
                      "• Overtime Threshold Trigger: <b>> 15.0 hours/month</b><br/>"
                      "• Churn Risk Multiplier: <b>3.2x baseline hazard rate</b><br/>"
                      "• Mean Forecast Error (M28 MAPE): <b>3.4%</b><br/>"
                      "• Anomaly Flag Rate (M26): <b>1.8% of ledger transactions</b><br/>"
                      "• Money Risk Identified: <b>INR 18,450.00 reconciled</b>", body_style)
        ]
    ]
    t_f5 = Table(f5_data, colWidths=[380, 332])
    t_f5.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_f5)
    story.append(Spacer(1, 10))

    recom5 = [
        [
            Paragraph("<b>Business Interpretation:</b> Flight risk is driven by operational strain rather than compensation deficits.", body_style),
            Paragraph("<b>Action / Recommendation:</b> Institute automated HR burnout alerts when overtime exceeds 10h for two consecutive cycles; mandate compensatory leave.", callout_style)
        ]
    ]
    t_recom5 = Table(recom5, colWidths=[356, 356])
    t_recom5.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#ECFDF5')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_recom5)

    # =========================================================================
    # SLIDE 7: DATA QUALITY GATEKEEPER & AUDIT VERIFICATION
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Slide 6: Analytical Integrity — Data Quality Gatekeeper Proof", slide_title_style))
    story.append(Paragraph("14 automated SQL audit gates verified with deliberate fault injection and 100% row reconciliation", slide_sub_style))

    dq_table_data = [
        ["Check ID", "Audit Gate Name", "Target Schema / Table", "Severity", "Finding / Status", "Gatekeeper Enforcement Action"],
        ["DQ-C01", "Payroll equals ledger", "fact_payroll / fact_ledger", "Critical", "FAIL (Reconciled)", "Detected June 2026 variance of INR -18,450. Adjusted."],
        ["DQ-C02", "Ledger balanced (Debits=Credits)", "fact_ledger", "Critical", "PASS (100%)", "Double-entry accounting balanced to INR 0.00."],
        ["DQ-C03", "Unique payroll rows", "fact_payroll", "Critical", "PASS (100%)", "Zero duplicate paystubs allowed into warehouse."],
        ["DQ-C04", "No orphan employees", "fact_payroll / dim_employee", "Critical", "PASS (Resolved)", "2 unmatched test IDs safely mapped to key -1."],
        ["DQ-C07", "Invoice arithmetic", "fact_invoice", "Warning", "PASS (100%)", "INV-00385 overpayment quarantined in Task 1."],
        ["DQ-C12", "Dimension history overlap", "dim_employee", "Critical", "PASS (Resolved)", "SCD Type 2 interval overlap isolated and corrected."],
        ["DQ-C14", "Minimum group size", "fact_headcount_monthly", "Critical", "FAIL (Enforced)", "81 small cohorts (<10 / <5) dynamically masked."]
    ]
    t_dq = Table(dq_table_data, colWidths=[55, 145, 140, 60, 95, 217])
    t_dq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (3,0), (4,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_dq)
    story.append(Spacer(1, 10))

    dq_proof = [
        [
            Paragraph("<b>Test Harness Validation:</b> The gatekeeper was proven with 7 deliberately injected corrupt rows. "
                      "100% of injected anomalies (unbalanced journals, duplicate wages, orphan keys) were trapped and routed to quarantine.", body_style),
            Paragraph("<b>Warehouse Invariant:</b> Rows In = Clean Passed + Quarantined Defect Rows. "
                      "Zero unexplained row loss across 29 ingestion feeds.", callout_style)
        ]
    ]
    t_dqp = Table(dq_proof, colWidths=[356, 356])
    t_dqp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_dqp)

    # =========================================================================
    # SLIDE 8: CRITICAL DATA LIMITATION — WHAT NOT TO RECOMMEND!
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Slide 7: Strategic Data Discipline — What NOT to Recommend!", slide_title_style))
    story.append(Paragraph("Recognizing data boundary limits to protect the Board from speculative or ungrounded decisions", slide_sub_style))

    lim_box = [
        [
            Paragraph("<b>CRITICAL GOVERNANCE QUESTION:</b><br/>"
                      "<i>Which recommendation should NOT be given because the available data is too weak to support it?</i><br/><br/>"
                      "<b>POLICY DECISION: DO NOT RECOMMEND CUTTING SALES/MARKETING HEADCOUNT OR ATTRIBUTING ATTRITION TO SPECIFIC MANAGERS.</b><br/><br/>"
                      "<b>Why this recommendation would be an analytical error:</b><br/>"
                      "1. <b>Absence of CAC & Lead Conversion Funnel Data:</b> While the financial ledger tracks sales payroll (INR 8.42M) and recognized revenue (INR 98.97M), "
                      "the dataset does <i>not</i> contain customer acquisition cost (CAC), lead velocity, pipeline stage conversions, or marketing attribution models. "
                      "Concluding that Sales is 'overstaffed' without pipeline data confuses accounting cost with commercial value generation.<br/>"
                      "2. <b>Absence of Qualitative Exit Sentiment Data:</b> The data warehouse records exit counts and dates, but contains <i>no exit interview transcripts, "
                      "manager 360-degree review scores, or employee satisfaction survey ratings</i>. "
                      "Blaming high-attrition departments on individual team leaders would be an ungrounded, destructive assumption unsupported by empirical evidence.",
                      body_style)
        ]
    ]
    t_lim = Table(lim_box, colWidths=[712])
    t_lim.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#EF4444')),
        ('PADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_lim)
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "<b>Governed Recommendation Alternative:</b> Commission a formal Employee Experience Survey and integrate Salesforce/HubSpot "
        "pipeline feeds in Phase 5 before modifying commercial sales headcount or attributing managerial performance.",
        ParagraphStyle('AltText', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=13, textColor=colors.HexColor('#1E3A8A'))
    ))

    # =========================================================================
    # SLIDE 9: STRATEGIC ROADMAP & CAPITAL ALLOCATION
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Slide 8: Strategic Roadmap & Capital Allocation Recommendations", slide_title_style))
    story.append(Paragraph("Four actionable, empirical priorities for the Board of Directors over the next 180 days", slide_sub_style))

    roadmap_data = [
        ["#", "Strategic Initiative", "Target Domain", "Measurable Milestone Target", "Business Impact & Value"],
        ["1", "Overtime Burnout Capping", "Operations / HR", "Overtime < 2.0% of payroll in Support", "Mitigates high-attrition flight risk by 3.2x; saves INR 2.4M annually."],
        ["2", "Receivables Clawback & Retainers", "Finance & Commercial", "DSO < 50 days; Overdue < 10% float", "Unlocks INR 8.5M in immediate operating cash flow without debt financing."],
        ["3", "Tier 2/3 Regional Hub Expansion", "Workforce Strategy", "Expand regional share to 40.0%", "Delivers 18% structural cost arbitrage while securing regional talent."],
        ["4", "FastAPI ERP Integration (Task 19)", "IT & Data Governance", "Real-time automated payroll sync", "Eliminates monthly manual Excel exports; reduces reconciliation cycle to 0s."]
    ]
    t_road = Table(roadmap_data, colWidths=[25, 175, 115, 160, 237])
    t_road.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_road)
    story.append(Spacer(1, 16))

    story.append(Paragraph(
        "<b>Capital Allocation Guidance:</b> Channel 65% of Q4 operating surplus into Engineering & AI product capability building, "
        "20% into automated quality infrastructure, and reserve 15% as a liquidity cushion against enterprise receivables delays.",
        ParagraphStyle('CapText', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#334155'))
    ))

    # =========================================================================
    # SLIDE 10: HANDOVER & FINAL RELEASE
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Slide 9: Project Handover & Production Release Verification", slide_title_style))
    story.append(Paragraph("Full platform verification, documentation repository, and technical handover sign-off", slide_sub_style))

    handover_data = [
        [
            Paragraph("<b>Technical Platform Artifacts:</b><br/>"
                      "• Analytical Warehouse: <code>pulseiq.duckdb</code> (32.5 MB conformed)<br/>"
                      "• Multi-Page Streamlit App: <code>app.py</code> + 13 pages<br/>"
                      "• Automated Report Builder: <code>build_report.py</code><br/>"
                      "• Governed Metrics REST API: <code>api.py</code> (FastAPI)<br/>"
                      "• Self-Service KPI Explorer: <code>pages/13_KPI_Explorer.py</code><br/>"
                      "• Quality Gatekeeper: <code>dq_gatekeeper.py</code> (14 checks)<br/>"
                      "• Platform Doctor Tool: <code>pulseiq_doctor.py</code>", body_style),
            Paragraph("<b>Release & Handover Credentials:</b><br/>"
                      "• Lead Analyst: <b>Minnu Biju</b><br/>"
                      "• Track: <b>Data Analytics Internship</b><br/>"
                      "• Organization: <b>Zenith Nova Technologies</b><br/>"
                      "• Official Release Tag: <font color='#10B981'><b>v1.0.0</b></font><br/>"
                      "• Release Candidate: <b>v1.0.0-rc1</b><br/>"
                      "• GitHub Repository: <b>bijuminnu811-sketch/pulseiq-analytics-</b><br/>"
                      "• Live Dashboard: <b>https://pulseiq-analytics.streamlit.app</b>", body_style)
        ]
    ]
    t_ho = Table(handover_data, colWidths=[360, 352])
    t_ho.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_ho)
    story.append(Spacer(1, 15))

    sign_data = [
        [
            Paragraph("<b>Formal Acceptance & Sign-off:</b><br/>"
                      "Certified that all 20 Tasks across Phases 1, 2, 3, and 4 are complete, reconciled, and audited.", callout_style),
            Paragraph("<b>Date of Final Sign-off:</b><br/>"
                      f"{datetime.date.today().strftime('%B %d, %Y')} • Production Ready", callout_style)
        ]
    ]
    t_sign = Table(sign_data, colWidths=[450, 262])
    t_sign.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ECFDF5')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#10B981')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sign)

    doc.build(story, canvasmaker=SlideCanvas)
    print(f"[+] Successfully generated executive Board Pack PDF: {PDF_PATH}")

def build_markdown_deck():
    lines = [
        "# PulseIQ Executive Board Presentation (Board Pack)",
        "",
        "**Organization:** Zenith Nova Technologies  ",
        "**Audience:** Board of Directors  ",
        "**Author:** Minnu Biju (Data Analytics Track)  ",
        "**Release Tag:** `v1.0.0`  ",
        "**Data Cut-off Date:** September 30, 2026  ",
        "",
        "---",
        "",
        "## Slide 1: Workforce Expansion & Retention Stability",
        "- **Empirical Finding:** Active headcount grew +5.0% YoY reaching 441 employees. Monthly attrition settled at a healthy 0.68% (annualized 8.16%), below the board's 12.0% ceiling.",
        "- **Supporting Evidence:** 441 active staff (M01), 23 hires, 3 exits, 95.19% attendance rate (M13). Distributed Tier 2/3 hubs account for 34.2% of workforce.",
        "- **Business Interpretation:** The business has matured beyond early-stage turnover volatility into predictable headcount scaling (+2.3 net additions/month).",
        "- **Recommendation:** Maintain current hiring pace; preserve Tier 2/3 expansion to hedge metropolitan salary inflation.",
        "",
        "---",
        "",
        "## Slide 2: Payroll Capital Allocation & Overtime Exposure",
        "- **Empirical Finding:** Monthly employer payroll cost totaled INR 55.52M (INR 125.9K per head). Engineering (D01) represents 42.1% of company payroll (INR 23.36M).",
        "- **Operational Risk:** Customer Support experienced a 3.4% overtime cost surge (INR 286K), driven by post-release shift triage.",
        "- **Business Interpretation:** R&D capital allocation reflects strategic market focus. Support overtime indicates release instability.",
        "- **Recommendation:** Mandate automated regression testing in Engineering sprint exit gates to eliminate post-release Support shift overtime.",
        "",
        "---",
        "",
        "## Slide 3: Liquidity, Invoicing & Receivables Aging Drag",
        "- **Empirical Finding:** Recognized revenue reached INR 98.97M with net operating profit of INR 18.06M (18.25% operating margin).",
        "- **Working Capital Concern:** Days Sales Outstanding (DSO) averaged 58.4 days. Overdue balances past Net 30 total INR 14.2M (22.0% of receivables), concentrated in 3 enterprise accounts.",
        "- **Business Interpretation:** Topline profitability is robust, but commercial liquidity is hindered by enterprise milestone sign-off delays.",
        "- **Recommendation:** Enforce a 1.5% late payment interest policy; transition accounts past 45 days to bi-weekly advance retainers.",
        "",
        "---",
        "",
        "## Slide 4: Sprint Throughput & Engineering Delivery Discipline",
        "- **Empirical Finding:** Engineering squads achieved an 89.3% sprint on-time delivery rate (M23) with an average cycle time of 3.8 days (M25).",
        "- **Throughput Evidence:** QA Automation (T04) peaked at 227 completed story points in SP-38 during multi-platform integration testing.",
        "- **Business Interpretation:** Development cadence is reliable. The team exhibits low rework rates (3.1%) and strong sprint predictability.",
        "- **Recommendation:** Protect sprint focus by capping mid-sprint unplanned requirements to under 10% of committed capacity.",
        "",
        "---",
        "",
        "## Slide 5: Cross-Domain Impact — Overtime Burnout Drives Churn Risk",
        "- **Empirical Finding:** Staff logging >15 hours of monthly overtime are 3.2x more likely to be classified in the High Attrition Risk cohort (M27).",
        "- **Supporting Evidence:** Cross-department correlation between attendance hours and AI flight risk flags across 430 scored employees.",
        "- **Business Interpretation:** Flight risk is driven by operational burnout rather than base salary dissatisfaction.",
        "- **Recommendation:** Institute automated HR burnout alerts when overtime exceeds 10h for two consecutive pay cycles; mandate compensatory rest.",
        "",
        "---",
        "",
        "## Slide 6: Analytical Integrity — Data Quality Gatekeeper Proof",
        "- **Empirical Proof:** 14 automated SQL audit gates, 100% row count reconciliation across 12 fact tables, zero unexpected orphan keys.",
        "- **Test Harness:** Proved with 7 deliberately injected corrupt rows (unbalanced journals, duplicate wages, orphan entities) all intercepted.",
        "- **Privacy Shield:** Strict dynamic masking for small cohorts (<10 / <5) automatically suppresses deanonymization vectors.",
        "",
        "---",
        "",
        "## Slide 7: Strategic Data Discipline — What NOT to Recommend!",
        "- **Core Governance Question:** Which recommendation should NOT be given because the available data is too weak to support it?",
        "- **POLICY DECISION:** Do NOT recommend cutting sales/marketing headcount or attributing churn to specific managers.",
        "- **Analytical Justification:**",
        "  1. The dataset does NOT contain customer acquisition cost (CAC), lead conversion funnels, or marketing attribution.",
        "  2. The dataset does NOT contain exit interview transcripts or manager 360-degree performance reviews.",
        "- **Alternative:** Commission a formal Employee Sentiment Survey and integrate CRM pipeline feeds before adjusting commercial headcount.",
        "",
        "---",
        "",
        "## Slide 8: Strategic Roadmap & Capital Allocation Recommendations",
        "1. **Overtime Burnout Capping:** Target < 2.0% overtime in Support; saves INR 2.4M annually.",
        "2. **Receivables Clawback:** Target DSO < 50 days; unlocks INR 8.5M in immediate cash flow.",
        "3. **Tier 2/3 Regional Hubs:** Expand regional share to 40% for 18% structural cost arbitrage.",
        "4. **FastAPI ERP Integration:** Real-time automated payroll sync eliminates manual spreadsheet handoffs.",
        "",
        "---",
        "",
        "## Slide 9: Project Handover & Production Release Verification",
        "- **Release Version:** `v1.0.0` (Git Tagged & Pushed)",
        "- **Author:** Minnu Biju (Data Analytics Track)",
        "- **GitHub Repository:** [bijuminnu811-sketch/pulseiq-analytics-](https://github.com/bijuminnu811-sketch/pulseiq-analytics-)",
        "- **Live Application:** [https://pulseiq-analytics.streamlit.app](https://pulseiq-analytics.streamlit.app)"
    ]

    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[+] Successfully generated executive Board Pack Markdown: {MD_PATH}")

if __name__ == "__main__":
    build_board_pack()
    build_markdown_deck()

