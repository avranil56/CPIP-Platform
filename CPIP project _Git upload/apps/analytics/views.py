from django.shortcuts import render, redirect
from django.contrib import messages
from apps.core.models import AnnualReport, Company
from .metrics_calculator import calculate_all_metrics_for_report, calculate_metrics_for_company
from .comparison_engine import calculate_comparison_for_company, get_trend_analysis
from .cagr_calculator import calculate_cagr_for_company, get_growth_summary
from .profitability_analyzer import calculate_profitability_metrics, get_profitability_summary


def calculate_report_metrics(request, report_id):
    result = calculate_all_metrics_for_report(report_id)
    if result.get('success'):
        m = result['metrics']
        messages.success(request, f"Metrics calculated for {m['company']} ({m['year']})")
    else:
        messages.error(request, f"Error: {result.get('error')}")
    return redirect('reports:report_list')


def company_metrics_dashboard(request, company_id):
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')
    result = calculate_metrics_for_company(company_id)
    return render(request, 'analytics/company_metrics.html', {'company': company, 'metrics_data': result})


def company_comparison(request, company_id):
    try:
        company = Company.objects.get(company_id=company_id)
        return render(request, 'analytics/company_comparison.html', {
            'company': company,
            'comparison_data': calculate_comparison_for_company(company_id),
            'trend_data': get_trend_analysis(company_id),
        })
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')


def company_cagr(request, company_id):
    try:
        company = Company.objects.get(company_id=company_id)
        return render(request, 'analytics/company_cagr.html', {
            'company': company,
            'cagr_data': calculate_cagr_for_company(company_id),
            'growth_summary': get_growth_summary(company_id),
        })
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')


def company_profitability(request, company_id):
    try:
        company = Company.objects.get(company_id=company_id)
        return render(request, 'analytics/company_profitability.html', {
            'company': company,
            'profitability_data': calculate_profitability_metrics(company_id),
            'profitability_summary': get_profitability_summary(company_id),
        })
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')