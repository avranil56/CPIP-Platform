from django.shortcuts import render, redirect
from django.contrib import messages
from apps.core.models import Company
from .investment_agent import generate_investment_suggestions
from .forecaster import (
    forecast_metric, forecast_segment,
    save_forecast_to_db, get_available_segments
)


def company_forecast(request, company_id):
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')

    metric = request.GET.get('metric', 'revenue')
    periods = int(request.GET.get('periods', 3))
    segment = request.GET.get('segment', '')

    available_segments = get_available_segments(company_id)

    # Segment forecast path
    if metric == 'segment' and segment:
        result = forecast_segment(company_id, segment, periods)
    else:
        result = forecast_metric(company_id, metric, periods)

    return render(request, 'forecasting/company_forecast.html', {
        'company': company,
        'metric': metric,
        'periods': periods,
        'segment': segment,
        'available_segments': available_segments,
        'result': result,
    })


def save_forecast(request, company_id):
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')

    metric = request.GET.get('metric', 'revenue')
    segment = request.GET.get('segment', '')

    if metric == 'segment' and segment:
        result = forecast_segment(company_id, segment, 3)
        metric_key = f'segment_{segment}'
    else:
        result = forecast_metric(company_id, metric, 3)
        metric_key = metric

    if result.get('success'):
        save_result = save_forecast_to_db(company_id, metric_key, result['forecast'])
        if save_result.get('success'):
            messages.success(request, f"Saved {save_result['saved']} forecast points.")
        else:
            messages.error(request, f"Save failed: {save_result.get('error')}")
    else:
        messages.error(request, f"Forecast failed: {result.get('error')}")

    return redirect('forecasting:company_forecast', company_id=company_id)


def investment_suggestions(request, company_id):
    """Display AI-generated investment suggestions."""
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')

    result = generate_investment_suggestions(company_id)
    if not result.get('success'):
        messages.error(request, f"Investment analysis failed: {result.get('error')}")
        return redirect('reports:report_list')

    return render(request, 'forecasting/investment_suggestions.html', {
        'company': company,
        'result': result,
    })