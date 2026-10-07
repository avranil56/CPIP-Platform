from apps.agents.groq_service import ask_groq as ask_gemini
from apps.core.models import AnnualReport, FinancialMetric, BusinessSegment, Risk, Company
import json
import logging

logger = logging.getLogger(__name__)


def build_full_context(company_id):
    """Build comprehensive context pulling all data."""
    try:
        company = Company.objects.get(company_id=company_id)
        reports = AnnualReport.objects.filter(company=company).order_by('year')

        lines = [f"COMPANY: {company.company_name}",
                 f"INDUSTRY: {company.industry or 'Not specified'}",
                 ""]

        # Financial overview
        lines.append("FINANCIAL DATA BY YEAR:")
        for report in reports:
            metric = FinancialMetric.objects.filter(report=report).first()
            if metric:
                lines.append(f"  {report.year}: Revenue={metric.revenue}, Profit={metric.profit}, "
                             f"Debt={metric.debt}, Margin={metric.profit_margin}")

        # Segments
        seg_lines = []
        for report in reports:
            for seg in BusinessSegment.objects.filter(report=report):
                seg_lines.append(f"  {report.year} - {seg.segment_name}: Revenue={seg.segment_revenue}")
        if seg_lines:
            lines.append("\nBUSINESS SEGMENTS:")
            lines.extend(seg_lines)

        # Risks
        risks = Risk.objects.filter(report__company=company, risk_type__startswith='[AI]')
        if risks.exists():
            lines.append("\nIDENTIFIED RISKS:")
            for r in risks:
                lines.append(f"  - {r.risk_type.replace('[AI] ', '')} (severity {r.severity}/10): {r.description}")

        return "\n".join(lines)
    except Company.DoesNotExist:
        return None


def generate_executive_summary(company_id):
    """Generate a boardroom-ready executive summary."""
    context = build_full_context(company_id)
    if not context:
        return {'success': False, 'error': 'Company not found or no data'}

    prompt = f"""You are a Chief Strategy Officer preparing a boardroom briefing. Based on the data below, write a concise executive summary.

{context}

Return ONLY valid JSON in this format (no markdown):
{{
    "headline": "one-line summary of overall position",
    "situation_overview": "2-3 sentences summarizing the company's current state",
    "key_findings": ["finding 1", "finding 2", "finding 3", "finding 4"],
    "critical_risks": ["risk 1", "risk 2", "risk 3"],
    "strategic_priorities": ["priority 1", "priority 2", "priority 3"],
    "board_recommendation": "one-paragraph actionable recommendation for the board"
}}
"""

    try:
        response = ask_gemini(prompt)
        cleaned = response.strip()
        if cleaned.startswith('```'):
            cleaned = cleaned.split('```')[1]
            if cleaned.startswith('json'):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)
        data['success'] = True
        return data
    except json.JSONDecodeError as e:
        return {'success': False, 'error': f'Invalid JSON: {str(e)}', 'raw': response}
    except Exception as e:
        return {'success': False, 'error': str(e)}