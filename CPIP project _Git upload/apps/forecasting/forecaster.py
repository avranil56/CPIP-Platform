import logging
from decimal import Decimal
from apps.core.models import AnnualReport, FinancialMetric, Company, Forecast

logger = logging.getLogger(__name__)


def linear_forecast(values, periods=3):
    """
    Forecast future values using linear regression.

    Args:
        values: List of (year, value) tuples
        periods: Number of future years to predict

    Returns:
        List of dicts with year, predicted, lower, upper
    """
    import numpy as np

    years = np.array([v[0] for v in values], dtype=float)
    vals = np.array([v[1] for v in values], dtype=float)

    # Fit line: y = mx + b
    m, b = np.polyfit(years, vals, 1)

    # Compute residual std for confidence interval
    predicted_hist = m * years + b
    residuals = vals - predicted_hist
    std = float(np.std(residuals)) if len(vals) > 2 else float(np.std(vals)) * 0.1

    last_year = int(years[-1])
    results = []

    for i in range(1, periods + 1):
        year = last_year + i
        predicted = m * year + b
        # 80% confidence interval (z ≈ 1.28)
        margin = 1.28 * std
        results.append({
            'year': year,
            'predicted': round(max(predicted, 0), 2),
            'lower': round(max(predicted - margin, 0), 2),
            'upper': round(predicted + margin, 2),
        })

    return results


def forecast_metric(company_id, metric_field='revenue', periods=3):
    """Forecast a financial metric for a company."""
    try:
        reports = AnnualReport.objects.filter(company_id=company_id).order_by('year')
        data = []
        for report in reports:
            metric = FinancialMetric.objects.filter(report=report).first()
            if metric:
                value = getattr(metric, metric_field, None)
                if value is not None:
                    data.append((report.year, float(value)))

        if len(data) < 2:
            return {
                'success': False,
                'error': f'Need at least 2 data points. Have {len(data)}.'
            }

        forecast = linear_forecast(data, periods)

        return {
            'success': True,
            'company': Company.objects.get(company_id=company_id).company_name,
            'metric': metric_field,
            'historical': [{'year': y, 'value': v} for y, v in data],
            'forecast': forecast,
        }

    except Company.DoesNotExist:
        return {'success': False, 'error': 'Company not found'}
    except Exception as e:
        logger.error(f"Forecast error: {str(e)}")
        return {'success': False, 'error': str(e)}


def save_forecast_to_db(company_id, metric_field, forecast_data):
    """Save forecast results to database."""
    try:
        company = Company.objects.get(company_id=company_id)
        Forecast.objects.filter(company=company, metric_type=metric_field).delete()

        for row in forecast_data:
            Forecast.objects.create(
                company=company,
                metric_type=metric_field,
                forecast_year=row['year'],
                projected_value=Decimal(str(row['predicted'])),
                confidence_interval_lower=Decimal(str(row['lower'])),
                confidence_interval_upper=Decimal(str(row['upper'])),
            )

        return {'success': True, 'saved': len(forecast_data)}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def forecast_all_metrics(company_id, periods=3):
    """Forecast revenue, profit, and assets."""
    return {m: forecast_metric(company_id, m, periods)
            for m in ['revenue', 'profit', 'assets']}


def forecast_segment(company_id, segment_name, periods=3):
    """Forecast revenue for a specific business segment."""
    try:
        from apps.core.models import BusinessSegment

        # Gather segment revenue across years
        reports = AnnualReport.objects.filter(company_id=company_id).order_by('year')
        data = []
        for report in reports:
            seg = BusinessSegment.objects.filter(report=report, segment_name=segment_name).first()
            if seg and seg.segment_revenue is not None:
                data.append((report.year, float(seg.segment_revenue)))

        if len(data) < 2:
            return {
                'success': False,
                'error': f'Need at least 2 data points for {segment_name}. Have {len(data)}.'
            }

        forecast = linear_forecast(data, periods)
        return {
            'success': True,
            'segment': segment_name,
            'historical': [{'year': y, 'value': v} for y, v in data],
            'forecast': forecast,
        }
    except Exception as e:
        logger.error(f"Segment forecast error: {str(e)}")
        return {'success': False, 'error': str(e)}


def get_available_segments(company_id):
    """Get list of segment names available for a company."""
    from apps.core.models import BusinessSegment
    return list(
        BusinessSegment.objects.filter(report__company_id=company_id)
        .values_list('segment_name', flat=True)
        .distinct()
    )