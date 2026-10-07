import re
from decimal import Decimal


def extract_financial_metrics(text):
    """Extract financial metrics from PDF text."""
    metrics = {k: None for k in [
        'revenue', 'profit', 'net_income', 'operating_income', 'gross_profit',
        'ebitda', 'assets', 'liabilities', 'debt', 'expenses', 'cash', 'equity', 'year'
    ]}

    patterns = {
        'revenue': [
            r'(?:revenue|sales|turnover|net sales)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)',
            r'(?:total revenue|total sales)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)',
        ],
        'profit': [
            r'(?:profit|net profit|net income)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)',
            r'(?:net income|net earnings)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)',
        ],
        'net_income': [r'(?:net income|net earnings)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)'],
        'operating_income': [r'(?:operating income|operating profit)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)'],
        'gross_profit': [r'(?:gross profit|gross margin)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)'],
        'ebitda': [r'(?:ebitda)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)'],
        'assets': [r'(?:total assets|assets)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)'],
        'liabilities': [r'(?:total liabilities|liabilities)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)'],
        'debt': [r'(?:total debt|debt)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)'],
        'expenses': [
            r'(?:total expenses|expenses)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)',
            r'(?:operating expenses)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)',
        ],
        'cash': [r'(?:cash and cash equivalents|cash)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)'],
        'equity': [r'(?:total equity|shareholder equity|stockholders equity)[\s:]*[$€£¥]?\s*([\d,]+\.?\d*)'],
    }

    for key, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    metrics[key] = Decimal(match.group(1).replace(',', ''))
                    break
                except Exception:
                    pass

    year_patterns = [
        r'(?:fiscal year|year ended|for the year)[\s:]*(\d{4})',
        r'\b(20\d{2})\b', r'\b(19\d{2})\b',
    ]
    years = []
    for pattern in year_patterns:
        years.extend(re.findall(pattern, text))
    if years:
        metrics['year'] = max([int(y) for y in years if 1900 <= int(y) <= 2100])

    return metrics


def detect_currency(text):
    """Detect the currency used in financial data."""
    symbols = {'$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY', '₹': 'INR'}
    for symbol, code in symbols.items():
        if symbol in text:
            return symbol
    for code in ['USD', 'EUR', 'GBP', 'JPY', 'INR']:
        if code in text:
            return code
    return None


def extract_all_metrics_from_report(report):
    """Extract all financial metrics from a report object."""
    from apps.reports.pdf_extractor import extract_text_from_pdf

    text = extract_text_from_pdf(report.file_path)
    metrics = extract_financial_metrics(text)
    currency = detect_currency(text)

    return {
        'report_id': report.report_id,
        'company': report.company.company_name,
        'year': report.year,
        'currency': currency,
        'metrics': metrics,
        'text_preview': text[:500] + '...' if len(text) > 500 else text,
    }