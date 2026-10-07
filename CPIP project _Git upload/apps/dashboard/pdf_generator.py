import io
import os
from datetime import datetime
from decimal import Decimal

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)

from django.conf import settings
from apps.core.models import Company, AnnualReport, FinancialMetric, BusinessSegment, Risk


# Colors matching dark theme (but for print, we use readable light theme)
PRIMARY = colors.HexColor('#0F172A')
ACCENT = colors.HexColor('#2563EB')
SUCCESS = colors.HexColor('#16A34A')
DANGER = colors.HexColor('#DC2626')
WARNING = colors.HexColor('#EA580C')
LIGHT_BG = colors.HexColor('#F1F5F9')
BORDER = colors.HexColor('#CBD5E1')
TEXT = colors.HexColor('#1E293B')
MUTED = colors.HexColor('#64748B')


def _styles():
    """Return a dict of paragraph styles."""
    ss = getSampleStyleSheet()
    return {
        'title': ParagraphStyle('title', parent=ss['Title'], fontSize=22, textColor=PRIMARY, spaceAfter=6, alignment=TA_CENTER, fontName='Helvetica-Bold'),
        'subtitle': ParagraphStyle('subtitle', parent=ss['Normal'], fontSize=11, textColor=MUTED, spaceAfter=20, alignment=TA_CENTER, fontName='Helvetica'),
        'h2': ParagraphStyle('h2', parent=ss['Heading2'], fontSize=14, textColor=ACCENT, spaceBefore=16, spaceAfter=10, fontName='Helvetica-Bold'),
        'h3': ParagraphStyle('h3', parent=ss['Heading3'], fontSize=11, textColor=PRIMARY, spaceBefore=8, spaceAfter=6, fontName='Helvetica-Bold'),
        'body': ParagraphStyle('body', parent=ss['Normal'], fontSize=10, textColor=TEXT, leading=14, alignment=TA_JUSTIFY, spaceAfter=8),
        'label': ParagraphStyle('label', parent=ss['Normal'], fontSize=8, textColor=MUTED, fontName='Helvetica-Bold'),
        'value': ParagraphStyle('value', parent=ss['Normal'], fontSize=11, textColor=TEXT, fontName='Helvetica-Bold'),
        'footer': ParagraphStyle('footer', parent=ss['Normal'], fontSize=8, textColor=MUTED, alignment=TA_CENTER),
    }


def _build_header(story, styles, company):
    """Add report header."""
    story.append(Paragraph(f"{company.company_name}", styles['title']))
    story.append(Paragraph(f"Executive Intelligence Report · Generated {datetime.now().strftime('%B %d, %Y')}", styles['subtitle']))

    # Company info table
    data = [
        ['Industry', company.industry or 'Not specified'],
        ['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M')],
        ['Platform', 'CPIP · Corporate Performance Intelligence Platform'],
    ]
    table = Table(data, colWidths=[4.5*cm, 11*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_BG),
        ('TEXTCOLOR', (0, 0), (0, -1), MUTED),
        ('TEXTCOLOR', (1, 0), (1, -1), TEXT),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.25, BORDER),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))


def _build_financial_section(story, styles, company):
    """Add financial metrics table."""
    reports = AnnualReport.objects.filter(company=company).order_by('year')
    if not reports.exists():
        return

    story.append(Paragraph("1. Financial Performance", styles['h2']))

    cell_style = ParagraphStyle('cell', fontName='Helvetica', fontSize=9, leading=11, textColor=TEXT, alignment=1)
    cell_bold = ParagraphStyle('cell_bold', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white, alignment=1)
    cell_left = ParagraphStyle('cell_left', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white)

    data = [[
        Paragraph('<b>Year</b>', cell_bold),
        Paragraph('<b>Revenue</b>', cell_bold),
        Paragraph('<b>Profit</b>', cell_bold),
        Paragraph('<b>Assets</b>', cell_bold),
        Paragraph('<b>Debt</b>', cell_bold),
        Paragraph('<b>Margin</b>', cell_bold),
    ]]

    for r in reports:
        m = FinancialMetric.objects.filter(report=r).first()
        if m:
            data.append([
                Paragraph(str(r.year), cell_style),
                Paragraph(f"{m.revenue:,.0f}" if m.revenue else '—', cell_style),
                Paragraph(f"{m.profit:,.0f}" if m.profit else '—', cell_style),
                Paragraph(f"{m.assets:,.0f}" if m.assets else '—', cell_style),
                Paragraph(f"{m.debt:,.0f}" if m.debt else '—', cell_style),
                Paragraph(f"{m.profit_margin:.1f}%" if m.profit_margin else '—', cell_style),
            ])

    table = Table(data, colWidths=[2*cm, 3.2*cm, 3.2*cm, 3.2*cm, 2.5*cm, 2.4*cm], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.25, BORDER),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 15))


def _build_segment_section(story, styles, company):
    """Add business segment table."""
    latest = AnnualReport.objects.filter(company=company).order_by('-year').first()
    if not latest:
        return

    segments = BusinessSegment.objects.filter(report=latest)
    if not segments.exists():
        return

    story.append(Paragraph("2. Business Segments", styles['h2']))

    cell_style = ParagraphStyle('cell', fontName='Helvetica', fontSize=9, leading=11, textColor=TEXT)
    cell_num = ParagraphStyle('cell_num', fontName='Helvetica', fontSize=9, leading=11, textColor=TEXT, alignment=2)
    cell_bold = ParagraphStyle('cell_bold', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white)
    cell_bold_num = ParagraphStyle('cell_bold_num', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white, alignment=2)

    data = [[
        Paragraph('<b>Segment</b>', cell_bold),
        Paragraph('<b>Revenue</b>', cell_bold_num),
        Paragraph('<b>Profit</b>', cell_bold_num),
        Paragraph('<b>Growth</b>', cell_bold_num),
    ]]

    for s in segments:
        data.append([
            Paragraph(s.segment_name, cell_style),
            Paragraph(f"{s.segment_revenue:,.0f}" if s.segment_revenue else '—', cell_num),
            Paragraph(f"{s.segment_profit:,.0f}" if s.segment_profit else '—', cell_num),
            Paragraph(f"{s.segment_growth_rate:.1f}%" if s.segment_growth_rate else '—', cell_num),
        ])

    table = Table(data, colWidths=[6*cm, 3.5*cm, 3.5*cm, 2.5*cm], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.25, BORDER),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 15))


def _build_risk_section(story, styles, company):
    """Add risks and mitigations."""
    risks = Risk.objects.filter(report__company=company).order_by('-severity')[:8]
    if not risks.exists():
        return

    story.append(Paragraph("3. Risk Analysis & Mitigation", styles['h2']))

    # Cell paragraph style (wraps text)
    cell_style = ParagraphStyle(
        'cell', fontName='Helvetica', fontSize=8, leading=10, textColor=TEXT
    )
    cell_bold = ParagraphStyle(
        'cell_bold', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=TEXT
    )

    data = [[
        Paragraph('<b>Severity</b>', cell_bold),
        Paragraph('<b>Risk</b>', cell_bold),
        Paragraph('<b>Category</b>', cell_bold),
        Paragraph('<b>Description</b>', cell_bold),
    ]]

    for r in risks:
        risk_name = r.risk_type.replace('[AI] ', '')
        data.append([
            Paragraph(f"{r.severity}/10", cell_style),
            Paragraph(risk_name, cell_style),
            Paragraph(r.risk_category.capitalize(), cell_style),
            Paragraph(r.description, cell_style),
        ])

    table = Table(data, colWidths=[1.6*cm, 3.5*cm, 2.0*cm, 8.4*cm], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DANGER),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.25, BORDER),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 15))


def _build_forecast_section(story, styles, company):
    """Add forecast table."""
    from apps.forecasting.forecaster import forecast_metric
    result = forecast_metric(company.company_id, 'revenue', 3)
    if not result.get('success'):
        return

    story.append(Paragraph("4. Revenue Forecast", styles['h2']))

    data = [['Year', 'Projected Revenue', 'Lower Bound', 'Upper Bound']]
    for row in result['forecast']:
        data.append([
            str(row['year']),
            f"{row['predicted']:,.0f}",
            f"{row['lower']:,.0f}",
            f"{row['upper']:,.0f}",
        ])

    table = Table(data, colWidths=[2.5*cm, 4.5*cm, 4*cm, 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SUCCESS),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.25, BORDER),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 15))


def generate_executive_pdf(company_id):
    """
    Generate a complete executive PDF report for a company.

    Returns:
        BytesIO buffer containing the PDF.
    """
    company = Company.objects.get(company_id=company_id)
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title=f'{company.company_name} — Executive Report',
        author='CPIP Platform',
    )

    styles = _styles()
    story = []

    _build_header(story, styles, company)
    _build_financial_section(story, styles, company)
    _build_segment_section(story, styles, company)
    _build_risk_section(story, styles, company)
    _build_forecast_section(story, styles, company)

    # Footer note
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        f"Report generated by CPIP — Corporate Performance Intelligence Platform · "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles['footer']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer