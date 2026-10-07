from apps.agents.groq_service import ask_groq as ask_gemini
from apps.core.models import AnnualReport, FinancialMetric, Company, Forecast
from .forecaster import forecast_metric
import json
import logging

logger = logging.getLogger(__name__)


def build_investment_context(company_id):
    """Build context combining historical + forecast data."""
    try:
        company = Company.objects.get(company_id=company_id)
        reports = AnnualReport.objects.filter(company=company).order_by('year')

        lines = [f"Company: {company.company_name}",
                 f"Industry: {company.industry or 'Not specified'}",
                 "\nHistorical Financial Data:"]

        for report in reports:
            metric = FinancialMetric.objects.filter(report=report).first()
            if metric:
                lines.append(f"  {report.year}: Revenue={metric.revenue}, "
                             f"Profit={metric.profit}, Margin={metric.profit_margin}")

        # Add forecasts
        lines.append("\nForecast (Linear Projection):")
        for m in ['revenue', 'profit']:
            result = forecast_metric(company_id, m, 3)
            if result.get('success'):
                for row in result['forecast']:
                    lines.append(f"  {m.title()} {row['year']}: ~{row['predicted']}")

        return "\n".join(lines)
    except Company.DoesNotExist:
        return None


def generate_investment_suggestions(company_id):
    """Use Gemini to generate strategic investment suggestions."""
    context = build_investment_context(company_id)
    if not context:
        return {'success': False, 'error': 'Company not found or no data'}

    prompt = f"""You are a corporate investment advisor. Based on historical data and forecasts below, suggest strategic investments.

{context}

Return ONLY valid JSON in this exact format (no markdown):
{{
    "investment_thesis": "one-paragraph overall investment view",
    "growth_investments": ["investment 1", "investment 2", "investment 3"],
    "efficiency_investments": ["investment 1", "investment 2"],
    "defensive_investments": ["investment 1", "investment 2"],
    "risk_considerations": ["consideration 1", "consideration 2"],
    "capital_allocation_priority": "one paragraph on where to prioritize capital"
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