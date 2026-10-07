from decimal import Decimal
from apps.core.models import FinancialMetric, AnnualReport, Company


def calculate_cagr(start_value, end_value, num_years):
    if start_value is None or end_value is None or start_value == 0 or num_years == 0:
        return None
    try:
        ratio = float(end_value) / float(start_value)
        return Decimal(str(((ratio ** (1 / num_years)) - 1) * 100))
    except Exception:
        return None


def get_company_data_for_cagr(company_id, metric_field='revenue'):
    reports = AnnualReport.objects.filter(company_id=company_id).order_by('year')
    data = []
    for report in reports:
        metric = FinancialMetric.objects.filter(report=report).first()
        if metric:
            value = getattr(metric, metric_field, None)
            if value is not None:
                data.append({'year': report.year, 'value': value})
    return data


def calculate_cagr_for_company(company_id):
    try:
        company = Company.objects.get(company_id=company_id)
        results = {'company': company.company_name, 'industry': company.industry, 'cagr': {}}

        for field in ['revenue', 'profit', 'assets', 'liabilities', 'debt', 'expenses']:
            data = get_company_data_for_cagr(company_id, field)
            if len(data) < 2:
                results['cagr'][field] = None
                continue
            results['cagr'][field] = calculate_cagr(
                data[0]['value'], data[-1]['value'],
                data[-1]['year'] - data[0]['year']
            )

        return results
    except Company.DoesNotExist:
        return {'error': 'Company not found'}
    except Exception as e:
        return {'error': str(e)}


def get_growth_summary(company_id):
    try:
        company = Company.objects.get(company_id=company_id)
        summary = {
            'company': company.company_name,
            'revenue_growth': {}, 'profit_growth': {},
            'asset_growth': {}, 'debt_growth': {},
            'overall_health': 'Neutral'
        }

        for label, field in [('revenue_growth', 'revenue'), ('profit_growth', 'profit'),
                             ('asset_growth', 'assets'), ('debt_growth', 'debt')]:
            data = get_company_data_for_cagr(company_id, field)
            if len(data) >= 2:
                if data[-1]['value'] > data[0]['value']:
                    summary[label]['trend'] = 'Increasing'
                elif data[-1]['value'] < data[0]['value']:
                    summary[label]['trend'] = 'Declining'
                else:
                    summary[label]['trend'] = 'Stable'

        rev = summary['revenue_growth'].get('trend')
        prof = summary['profit_growth'].get('trend')
        debt = summary['debt_growth'].get('trend')

        if rev == 'Increasing' and prof == 'Increasing' and debt != 'Increasing':
            summary['overall_health'] = 'Strong'
        elif rev == 'Declining' and prof == 'Declining':
            summary['overall_health'] = 'Concerning'
        elif rev == 'Declining':
            summary['overall_health'] = 'Cautious'

        return summary
    except Exception as e:
        return {'error': str(e)}