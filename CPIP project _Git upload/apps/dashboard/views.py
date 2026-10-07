from django.shortcuts import render, redirect
from django.contrib import messages
from apps.core.models import Company
from django.http import FileResponse
from .pdf_generator import generate_executive_pdf
from .chart_builder import (
    revenue_trend_chart, profit_trend_chart, revenue_vs_profit_chart,
    profitability_margin_chart, segment_comparison_chart, segment_bar_chart,
    forecast_chart,
)


def company_dashboard(request, company_id):
    """Full visualization dashboard for a company."""
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')

    charts = {
        'revenue_trend': revenue_trend_chart(company_id),
        'profit_trend': profit_trend_chart(company_id),
        'rev_vs_profit': revenue_vs_profit_chart(company_id),
        'margin': profitability_margin_chart(company_id),
        'segment_pie': segment_comparison_chart(company_id),
        'segment_bar': segment_bar_chart(company_id),
        'forecast_revenue': forecast_chart(company_id, 'revenue'),
    }

    # Convert to HTML
    charts_html = {}
    for key, fig in charts.items():
        if fig is not None:
            charts_html[key] = fig.to_html(full_html=False, include_plotlyjs=False)

    return render(request, 'dashboard/company_dashboard.html', {
        'company': company,
        'charts': charts_html,
        'has_charts': bool(charts_html),
    })



def executive_dashboard(request, company_id):
    """Master executive view combining all analyses."""
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')

    from apps.analytics.metrics_calculator import calculate_metrics_for_company
    from apps.analytics.cagr_calculator import calculate_cagr_for_company, get_growth_summary
    from apps.analytics.profitability_analyzer import calculate_profitability_metrics
    from apps.core.models import Risk, BusinessSegment

    # Aggregated data
    metrics_data = calculate_metrics_for_company(company_id)
    cagr_data = calculate_cagr_for_company(company_id)
    growth_summary = get_growth_summary(company_id)
    profitability = calculate_profitability_metrics(company_id)

    # Risks
    risks = Risk.objects.filter(
        report__company=company,
        risk_type__startswith='[AI]'
    ).order_by('-severity')[:6]

    # Segments
    segments = BusinessSegment.objects.filter(
        report__company=company
    ).order_by('-segment_revenue')[:6]

    # Charts (reuse from chart_builder)
    charts = {
        'revenue_trend': revenue_trend_chart(company_id),
        'profit_trend': profit_trend_chart(company_id),
        'rev_vs_profit': revenue_vs_profit_chart(company_id),
        'forecast_revenue': forecast_chart(company_id, 'revenue'),
    }
    charts_html = {
        k: v.to_html(full_html=False, include_plotlyjs=False)
        for k, v in charts.items() if v is not None
    }

    return render(request, 'dashboard/executive_dashboard.html', {
        'company': company,
        'metrics_data': metrics_data,
        'cagr_data': cagr_data,
        'growth_summary': growth_summary,
        'profitability': profitability,
        'risks': risks,
        'segments': segments,
        'charts': charts_html,
    })


def export_pdf(request, company_id):
    """Generate and download the executive PDF report."""
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')

    try:
        buffer = generate_executive_pdf(company_id)
    except Exception as e:
        messages.error(request, f'PDF generation failed: {str(e)}')
        return redirect('dashboard:executive_dashboard', company_id=company_id)

    filename = f"{company.company_name.replace(' ', '_')}_Executive_Report.pdf"
    return FileResponse(buffer, as_attachment=True, filename=filename)


def select_comparison(request):
    """Show form to pick 2 companies for comparison."""
    companies = Company.objects.all().order_by('company_name')
    return render(request, 'dashboard/select_comparison.html', {
        'companies': companies,
    })


def comparison_pdf(request):
    """Generate side-by-side comparison PDF."""
    from .comparison_pdf import generate_comparison_pdf

    a_id = request.GET.get('company_a')
    b_id = request.GET.get('company_b')

    if not a_id or not b_id or a_id == b_id:
        messages.error(request, 'Please select two different companies.')
        return redirect('dashboard:select_comparison')

    try:
        buffer = generate_comparison_pdf(int(a_id), int(b_id))
    except Exception as e:
        messages.error(request, f'Comparison failed: {str(e)}')
        return redirect('dashboard:select_comparison')

    a = Company.objects.get(company_id=a_id)
    b = Company.objects.get(company_id=b_id)
    filename = f"{a.company_name}_vs_{b.company_name}_Comparison.pdf"
    return FileResponse(buffer, as_attachment=True, filename=filename)