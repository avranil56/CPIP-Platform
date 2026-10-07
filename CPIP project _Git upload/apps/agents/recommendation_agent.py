from apps.agents.groq_service import ask_groq as ask_gemini
from apps.core.models import AnnualReport, FinancialMetric, BusinessSegment, Risk, Company
import json
import logging

logger = logging.getLogger(__name__)


def build_strategy_context(company_id):
    """Build comprehensive context for strategic recommendations."""
    try:
        company = Company.objects.get(company_id=company_id)
        reports = AnnualReport.objects.filter(company=company).order_by('year')

        lines = [f"Company: {company.company_name}",
                 f"Industry: {company.industry or 'Not specified'}",
                 "\nFinancial Data:"]

        for report in reports:
            metric = FinancialMetric.objects.filter(report=report).first()
            if metric:
                lines.append(f"Year {report.year}: Revenue={metric.revenue}, "
                             f"Profit={metric.profit}, Debt={metric.debt}, "
                             f"Profit Margin={metric.profit_margin}")

        # Add detected risks
        risks = Risk.objects.filter(report__company=company, risk_type__startswith='[AI]')
        if risks.exists():
            lines.append("\nDetected Risks:")
            for r in risks:
                lines.append(f"  - {r.risk_type.replace('[AI] ', '')} (severity {r.severity}/10)")

        return "\n".join(lines)
    except Company.DoesNotExist:
        return None


def generate_recommendations_with_gemini(company_id):
    """Use Gemini to generate strategic recommendations."""
    context = build_strategy_context(company_id)
    if not context:
        return {'success': False, 'error': 'Company not found or no data'}

    prompt = f"""You are a corporate strategy consultant. Based on the following data, generate strategic recommendations.

{context}

Return ONLY valid JSON in this format (no markdown):
{{
    "executive_direction": "one-sentence strategic direction",
    "short_term_actions": ["action 1", "action 2", "action 3"],
    "medium_term_actions": ["action 1", "action 2", "action 3"],
    "long_term_initiatives": ["initiative 1", "initiative 2"],
    "investment_priorities": ["priority 1", "priority 2", "priority 3"],
    "risk_mitigation_focus": ["focus 1", "focus 2"]
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
