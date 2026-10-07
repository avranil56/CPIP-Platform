"""
CPIP Health Check — Run with: python health_check.py
Verifies all major components are working.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cpip.settings')
django.setup()

from apps.core.models import Company, AnnualReport, FinancialMetric, BusinessSegment, Risk, Forecast, ExecutiveReport

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'


def check(label, condition, detail=''):
    icon = f'{GREEN}✓{RESET}' if condition else f'{RED}✗{RESET}'
    print(f"  {icon} {label}" + (f' — {detail}' if detail else ''))
    return condition


def section(title):
    print(f"\n{CYAN}━━━ {title} ━━━{RESET}")


def main():
    print(f"\n{CYAN}CPIP Platform Health Check{RESET}")
    print(f"{CYAN}{'=' * 50}{RESET}")

    all_ok = True

    # Database
    section("Database")
    try:
        counts = {
            'Companies': Company.objects.count(),
            'Reports': AnnualReport.objects.count(),
            'Financial Metrics': FinancialMetric.objects.count(),
            'Business Segments': BusinessSegment.objects.count(),
            'Risks': Risk.objects.count(),
            'Forecasts': Forecast.objects.count(),
            'Executive Reports': ExecutiveReport.objects.count(),
        }
        for label, count in counts.items():
            print(f"  {GREEN}•{RESET} {label}: {count}")
        all_ok &= True
    except Exception as e:
        all_ok &= check("Database connection", False, str(e))

    # AI Service
    section("AI Service (Groq)")
    try:
        from apps.agents.groq_service import test_groq_connection
        result = test_groq_connection()
        all_ok &= check("Groq API connection", result.get('success'), result.get('response', result.get('error', '')))
    except Exception as e:
        all_ok &= check("Groq API connection", False, str(e))

    # PDF Extractor
    section("PDF Extractor")
    try:
        from apps.reports.pdf_extractor import extract_text_from_pdf
        all_ok &= check("pdfplumber imported", True)
    except Exception as e:
        all_ok &= check("pdfplumber imported", False, str(e))

    # Analytics
    section("Analytics")
    try:
        from apps.analytics.metrics_calculator import calculate_all_metrics_for_report
        from apps.analytics.cagr_calculator import calculate_cagr_for_company
        from apps.analytics.comparison_engine import calculate_comparison_for_company
        all_ok &= check("Analytics modules load", True)
    except Exception as e:
        all_ok &= check("Analytics modules load", False, str(e))

    # Forecasting
    section("Forecasting")
    try:
        from apps.forecasting.forecaster import forecast_metric
        all_ok &= check("Forecaster loads", True)
    except Exception as e:
        all_ok &= check("Forecaster loads", False, str(e))

    # Charts
    section("Charts (Plotly)")
    try:
        from apps.dashboard.chart_builder import revenue_trend_chart
        all_ok &= check("Chart builder loads", True)
    except Exception as e:
        all_ok &= check("Chart builder loads", False, str(e))

    # PDF Export
    section("PDF Export (ReportLab)")
    try:
        from apps.dashboard.pdf_generator import generate_executive_pdf
        from apps.dashboard.comparison_pdf import generate_comparison_pdf
        all_ok &= check("PDF generators load", True)
    except Exception as e:
        all_ok &= check("PDF generators load", False, str(e))

    # Summary
    print(f"\n{CYAN}{'=' * 50}{RESET}")
    if all_ok:
        print(f"{GREEN}✓ ALL SYSTEMS OPERATIONAL{RESET}\n")
    else:
        print(f"{YELLOW}⚠ Some checks failed — review above{RESET}\n")


if __name__ == '__main__':
    main()