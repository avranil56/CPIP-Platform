from apps.agents.groq_service import ask_groq as ask_gemini
from apps.core.models import AnnualReport, FinancialMetric, BusinessSegment, Company
import json
import logging

logger = logging.getLogger(__name__)


def build_financial_context(company_id):
    """Build a text summary of all financial data for a company."""
    try:
        company = Company.objects.get(company_id=company_id)
        reports = AnnualReport.objects.filter(company=company).order_by('year')

        context_lines = [f"Company: {company.company_name}",
                         f"Industry: {company.industry or 'Not specified'}",
                         "Financial Data by Year:"]

        for report in reports:
            metric = FinancialMetric.objects.filter(report=report).first()
            if metric:
                context_lines.append(f"\nYear {report.year}:")
                context_lines.append(f"  Revenue: {metric.revenue}")
                context_lines.append(f"  Profit: {metric.profit}")
                context_lines.append(f"  Assets: {metric.assets}")
                context_lines.append(f"  Liabilities: {metric.liabilities}")
                context_lines.append(f"  Debt: {metric.debt}")
                context_lines.append(f"  Expenses: {metric.expenses}")
                context_lines.append(f"  Profit Margin: {metric.profit_margin}")

            segments = BusinessSegment.objects.filter(report=report)
            if segments:
                context_lines.append(f"  Segments:")
                for seg in segments:
                    context_lines.append(f"    - {seg.segment_name}: Revenue={seg.segment_revenue}, Profit={seg.segment_profit}")

        return "\n".join(context_lines)
    except Company.DoesNotExist:
        return None


def analyze_financials_with_gemini(company_id):
    """Use Gemini to analyze financial data and return structured insights."""
    context = build_financial_context(company_id)
    if not context:
        return {'success': False, 'error': 'Company not found or no data'}

    prompt = f"""You are a senior financial analyst. Analyze the following corporate financial data and return a structured JSON response.

{context}

Return ONLY valid JSON in this exact format (no markdown, no extra text):
{{
    "overall_assessment": "brief summary of financial health",
    "revenue_analysis": "analysis of revenue trends",
    "profitability_analysis": "analysis of profit and margins",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "key_insights": ["insight 1", "insight 2", "insight 3"]
}}
"""

    try:
        response = ask_gemini(prompt)
        # Clean response - remove markdown code blocks if present
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
        return {'success': False, 'error': f'Invalid JSON from Gemini: {str(e)}', 'raw': response}
    except Exception as e:
        return {'success': False, 'error': str(e)}