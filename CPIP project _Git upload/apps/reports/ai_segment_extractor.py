import json
import logging
from apps.agents.groq_service import ask_groq
from apps.reports.pdf_extractor import extract_text_from_pdf

logger = logging.getLogger(__name__)


def extract_segments_via_ai(report):
    """
    Use Groq LLM to extract business segments from PDF text.

    Args:
        report: AnnualReport instance

    Returns:
        dict with 'success', 'segments' (list), or 'error'
    """
    try:
        text = extract_text_from_pdf(report.file_path)
    except Exception as e:
        return {'success': False, 'error': f'PDF read failed: {e}'}

    # Truncate to keep prompt manageable (first 20k chars typically covers segment tables)
    snippet = text[:20000]

    prompt = f"""You are a financial data extraction assistant. Below is text extracted from an annual report.

COMPANY: {report.company.company_name}
YEAR: {report.year}

Extract ALL business segments mentioned with their revenue and profit (or operating income).

Return ONLY valid JSON in this exact format (no markdown, no explanation):
{{
  "segments": [
    {{
      "name": "Segment Name",
      "revenue": 12345.67,
      "profit": 1234.56
    }}
  ]
}}

Rules:
- Convert "383.29 Billion" → 383290000000 (i.e., apply billion/million multipliers)
- If a value is missing, use null
- Only include revenue-generating business segments (ignore "Total", "Consolidated", "Corporate" rows)
- If no segments found, return {{"segments": []}}

PDF TEXT:
---
{snippet}
---
"""

    try:
        response = ask_groq(prompt)
        cleaned = response.strip()
        if cleaned.startswith('```'):
            cleaned = cleaned.split('```')[1]
            if cleaned.startswith('json'):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)
        segments = data.get('segments', [])

        # Clean up numbers
        for seg in segments:
            for field in ['revenue', 'profit']:
                val = seg.get(field)
                if val is not None:
                    try:
                        seg[field] = float(val)
                    except (ValueError, TypeError):
                        seg[field] = None

        return {'success': True, 'segments': segments}

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON from Groq: {response}")
        return {'success': False, 'error': f'JSON parse failed: {e}', 'raw': response}
    except Exception as e:
        logger.error(f"AI segment extraction failed: {e}")
        return {'success': False, 'error': str(e)}