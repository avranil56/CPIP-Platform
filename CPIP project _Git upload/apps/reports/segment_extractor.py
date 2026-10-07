import re
from decimal import Decimal


def extract_segments(text):
    """Extract business segments and their financial data."""
    segments = []
    segment_keywords = [
        'segment', 'division', 'business unit', 'business line',
        'operating segment', 'reportable segment'
    ]

    segment_section = None
    for keyword in segment_keywords:
        pattern = rf'(?i)({keyword}s?[\s\S]*?)(?=(?:total|consolidated|adjusted|\n\n))'
        match = re.search(pattern, text)
        if match:
            segment_section = match.group(1)
            break
    if not segment_section:
        segment_section = text

    common_segments = [
        'automotive', 'electronics', 'entertainment', 'music', 'pictures',
        'game', 'network', 'financial services', 'insurance', 'banking',
        'technology', 'software', 'hardware', 'semiconductor', 'display',
        'industrial', 'consumer', 'energy', 'healthcare', 'pharmaceutical',
        'retail', 'e-commerce', 'media', 'telecommunications', 'cloud',
        'ai', 'robotics', 'mobility', 'transportation', 'aerospace',
        'defense', 'agriculture', 'food', 'beverage', 'apparel'
    ]

    segment_patterns = [
        r'(?i)(\w+[\s\w]*)\s*(?:segment|division)?\s*(?:revenue|sales|income)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)',
        r'(?i)(\w+[\s\w]*)\s*[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)\s*(?:revenue|sales)',
    ]

    for pattern in segment_patterns:
        for match in re.findall(pattern, segment_section):
            seg_name = match[0].strip()
            value_str = match[1].replace(',', '')
            is_segment = any(seg.lower() in seg_name.lower() for seg in common_segments)
            is_segment = is_segment or any(kw in seg_name.lower() for kw in segment_keywords)
            if is_segment:
                try:
                    segments.append({
                        'name': seg_name,
                        'revenue': Decimal(value_str),
                        'profit': None,
                        'growth': None,
                    })
                except Exception:
                    pass

    profit_patterns = [
        r'(?i)(\w+[\s\w]*)\s*(?:segment|division)?\s*(?:profit|operating income)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)',
    ]
    for pattern in profit_patterns:
        for match in re.findall(pattern, segment_section):
            seg_name = match[0].strip()
            value_str = match[1].replace(',', '')
            for seg in segments:
                if seg['name'].lower() in seg_name.lower() or seg_name.lower() in seg['name'].lower():
                    try:
                        seg['profit'] = Decimal(value_str)
                    except Exception:
                        pass
                    break

    seen, unique = set(), []
    for seg in segments:
        if seg['name'].lower() not in seen:
            seen.add(seg['name'].lower())
            unique.append(seg)

    for seg in unique:
        for suffix in [' segment', ' division', ' business', ' unit']:
            if seg['name'].lower().endswith(suffix):
                seg['name'] = seg['name'][:-len(suffix)]

    return unique


def extract_segment_growth(text, segments):
    """Extract growth rates for segments."""
    growth_patterns = [
        r'(?i)(\w+[\s\w]*)\s*(?:growth|increase|decrease)[\s:]*([\d,]+\.?\d*)%',
        r'(?i)(\w+[\s\w]*)\s*[\s:]*([\d,]+\.?\d*)%\s*(?:growth|increase)',
    ]
    for pattern in growth_patterns:
        for match in re.findall(pattern, text):
            seg_name, growth_str = match[0].strip(), match[1].replace(',', '')
            try:
                growth = Decimal(growth_str)
                for seg in segments:
                    if seg['name'].lower() in seg_name.lower() or seg_name.lower() in seg['name'].lower():
                        seg['growth'] = growth
                        break
            except Exception:
                pass
    return segments


def extract_all_segments_from_report(report):
    """Extract all segment data from a report."""
    from apps.reports.pdf_extractor import extract_text_from_pdf

    text = extract_text_from_pdf(report.file_path)
    segments = extract_segments(text)
    segments = extract_segment_growth(text, segments)

    return {
        'report_id': report.report_id,
        'company': report.company.company_name,
        'year': report.year,
        'segments': segments,
        'segment_count': len(segments),
    }