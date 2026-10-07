from apps.agents.groq_service import ask_groq as ask_gemini
from apps.core.models import AnnualReport, BusinessSegment, Company
import json
import logging

logger = logging.getLogger(__name__)


def build_segment_context(company_id):
    """Build text context of all segment data for a company."""
    try:
        company = Company.objects.get(company_id=company_id)
        reports = AnnualReport.objects.filter(company=company).order_by('year')

        lines = [f"Company: {company.company_name}",
                 f"Industry: {company.industry or 'Not specified'}",
                 "Business Segments by Year:"]

        has_data = False
        for report in reports:
            segments = BusinessSegment.objects.filter(report=report)
            if segments:
                has_data = True
                lines.append(f"\nYear {report.year}:")
                for seg in segments:
                    lines.append(f"  - {seg.segment_name}: "
                                 f"Revenue={seg.segment_revenue}, "
                                 f"Profit={seg.segment_profit}, "
                                 f"Growth={seg.segment_growth_rate}")

        if not has_data:
            return None
        return "\n".join(lines)
    except Company.DoesNotExist:
        return None


def analyze_segments_with_gemini(company_id):
    """Use Gemini to analyze business segment performance."""
    context = build_segment_context(company_id)
    if not context:
        return {'success': False, 'error': 'No segment data available for this company'}

    prompt = f"""You are a business segment analyst. Analyze the following segment data and provide insights.

{context}

Return ONLY valid JSON in this exact format (no markdown):
{{
    "overall_segment_health": "brief summary",
    "strongest_segment": "name of best-performing segment with reasoning",
    "weakest_segment": "name of worst-performing segment with reasoning",
    "segment_insights": ["insight 1", "insight 2", "insight 3"],
    "strategic_moves": ["recommendation 1", "recommendation 2", "recommendation 3"]
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