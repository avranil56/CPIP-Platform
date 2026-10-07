from apps.core.models import FinancialMetric, AnnualReport, Company


def calculate_yoy_growth(current_value, previous_value):
    if previous_value and previous_value != 0 and current_value is not None:
        return ((current_value - previous_value) / previous_value) * 100
    return None


def get_company_reports_with_metrics(company_id):
    reports = AnnualReport.objects.filter(company_id=company_id).order_by('year')
    data = []
    for report in reports:
        metric = FinancialMetric.objects.filter(report=report).first()
        if metric:
            data.append({
                'report_id': report.report_id,
                'year': report.year,
                'revenue': metric.revenue,
                'profit': metric.profit,
                'assets': metric.assets,
                'liabilities': metric.liabilities,
                'debt': metric.debt,
                'expenses': metric.expenses,
                'profit_margin': metric.profit_margin,
                'debt_to_equity': metric.debt_to_equity,
            })
    return data


def calculate_comparison_for_company(company_id):
    try:
        company = Company.objects.get(company_id=company_id)
        report_data = get_company_reports_with_metrics(company_id)
        if len(report_data) < 2:
            return {'company': company.company_name, 'error': 'Need at least 2 years of data for comparison'}

        comparisons = []
        for i in range(1, len(report_data)):
            current, previous = report_data[i], report_data[i-1]
            comparisons.append({
                'current_year': current['year'],
                'previous_year': previous['year'],
                'revenue_growth': calculate_yoy_growth(current['revenue'], previous['revenue']),
                'profit_growth': calculate_yoy_growth(current['profit'], previous['profit']),
                'assets_growth': calculate_yoy_growth(current['assets'], previous['assets']),
                'debt_growth': calculate_yoy_growth(current['debt'], previous['debt']),
                'profit_margin_change': calculate_yoy_growth(current['profit_margin'], previous['profit_margin']),
            })

        return {
            'company': company.company_name,
            'industry': company.industry,
            'years': [d['year'] for d in report_data],
            'comparisons': comparisons,
            'total_years': len(report_data),
        }
    except Company.DoesNotExist:
        return {'error': 'Company not found'}
    except Exception as e:
        return {'error': str(e)}


def get_trend_analysis(company_id):
    try:
        company = Company.objects.get(company_id=company_id)
        report_data = get_company_reports_with_metrics(company_id)
        if len(report_data) < 2:
            return {'company': company.company_name, 'error': 'Need at least 2 years'}

        trends = {'company': company.company_name, 'overall_assessment': {}}

        revenues = [d['revenue'] for d in report_data if d['revenue'] is not None]
        if len(revenues) >= 2:
            trends['overall_assessment']['revenue'] = (
                'increasing' if revenues[-1] > revenues[0] else
                'decreasing' if revenues[-1] < revenues[0] else 'stable'
            )

        profits = [d['profit'] for d in report_data if d['profit'] is not None]
        if len(profits) >= 2:
            trends['overall_assessment']['profit'] = (
                'increasing' if profits[-1] > profits[0] else
                'decreasing' if profits[-1] < profits[0] else 'stable'
            )

        return trends
    except Exception as e:
        return {'error': str(e)}