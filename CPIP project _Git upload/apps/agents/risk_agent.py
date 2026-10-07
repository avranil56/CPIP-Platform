from apps.agents.groq_service import ask_groq as ask_gemini
from apps.core.models import AnnualReport, FinancialMetric, BusinessSegment, Company
import json
import logging

logger = logging.getLogger(__name__)


def build_risk_context(company_id):
    """Build text context for risk analysis."""
    try:
        company = Company.objects.get(company_id=company_id)
        reports = AnnualReport.objects.filter(company=company).order_by('year')

        lines = [f"Company: {company.company_name}",
                 f"Industry: {company.industry or 'Not specified'}",
                 "Financial Data:"]

        for report in reports:
            metric = FinancialMetric.objects.filter(report=report).first()
            if metric:
                lines.append(f"\nYear {report.year}:")
                lines.append(f"  Revenue: {metric.revenue}")
                lines.append(f"  Profit: {metric.profit}")
                lines.append(f"  Debt: {metric.debt}")
                lines.append(f"  Liabilities: {metric.liabilities}")
                lines.append(f"  Expenses: {metric.expenses}")
                lines.append(f"  Profit Margin: {metric.profit_margin}")
                lines.append(f"  Debt-to-Equity: {metric.debt_to_equity}")

        return "\n".join(lines)
    except Company.DoesNotExist:
        return None


def detect_risks_with_gemini(company_id):
    """Use Gemini to detect risks and propose mitigations."""
    context = build_risk_context(company_id)
    if not context:
        return {'success': False, 'error': 'Company not found or no data'}

    prompt = f"""You are a corporate risk analyst. Analyze the following financial data and identify business risks.

{context}

Identify 3-6 significant risks. For each risk, provide:
- risk_type: short name (e.g., "Declining Profit Margin")
- severity: integer 1-10 (10 = most severe)
- risk_category: one of "operational", "financial", "market", "compliance"
- description: 1-2 sentence explanation
- mitigation: concrete mitigation strategy
- priority: "high", "medium", or "low"

Return ONLY valid JSON in this exact format (no markdown):
{{
    "risks": [
        {{
            "risk_type": "...",
            "severity": 7,
            "risk_category": "financial",
            "description": "...",
            "mitigation": "...",
            "priority": "high"
        }}
    ]
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