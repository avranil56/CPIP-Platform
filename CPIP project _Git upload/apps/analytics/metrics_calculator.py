from apps.core.models import FinancialMetric, AnnualReport, Company
import logging

logger = logging.getLogger(__name__)


def calculate_profit_margin(profit, revenue):
    if revenue and revenue != 0 and profit is not None:
        return (profit / revenue) * 100
    return None


def calculate_gross_margin(gross_profit, revenue):
    if revenue and revenue != 0 and gross_profit is not None:
        return (gross_profit / revenue) * 100
    return None


def calculate_debt_to_equity(debt, equity):
    if equity and equity != 0 and debt is not None:
        return debt / equity
    return None


def calculate_current_ratio(assets, liabilities):
    if liabilities and liabilities != 0 and assets is not None:
        return assets / liabilities
    return None


def calculate_roa(profit, assets):
    if assets and assets != 0 and profit is not None:
        return (profit / assets) * 100
    return None


def calculate_roe(profit, equity):
    if equity and equity != 0 and profit is not None:
        return (profit / equity) * 100
    return None


def calculate_operating_margin(operating_income, revenue):
    if revenue and revenue != 0 and operating_income is not None:
        return (operating_income / revenue) * 100
    return None


def calculate_ebitda_margin(ebitda, revenue):
    if revenue and revenue != 0 and ebitda is not None:
        return (ebitda / revenue) * 100
    return None


def calculate_asset_turnover(revenue, assets):
    if assets and assets != 0 and revenue is not None:
        return revenue / assets
    return None


def calculate_all_metrics_for_report(report_id):
    """Calculate all financial metrics for a specific report."""
    try:
        report = AnnualReport.objects.get(report_id=report_id)
        metric = FinancialMetric.objects.filter(report=report).first()

        if not metric:
            return {'success': False, 'error': f'No financial data for report {report_id}'}

        metrics = {
            'report_id': report_id,
            'company': report.company.company_name,
            'year': report.year,
            'revenue': metric.revenue,
            'profit': metric.profit,
            'profit_margin': calculate_profit_margin(metric.profit, metric.revenue),
            'gross_margin': calculate_gross_margin(metric.gross_profit, metric.revenue),
            'operating_margin': calculate_operating_margin(metric.operating_income, metric.revenue),
            'ebitda_margin': calculate_ebitda_margin(metric.ebitda, metric.revenue),
            'debt_to_equity': calculate_debt_to_equity(metric.debt, metric.equity),
            'current_ratio': calculate_current_ratio(metric.assets, metric.liabilities),
            'roa': calculate_roa(metric.profit, metric.assets),
            'roe': calculate_roe(metric.profit, metric.equity),
            'asset_turnover': calculate_asset_turnover(metric.revenue, metric.assets),
        }

        metric.profit_margin = metrics['profit_margin']
        metric.debt_to_equity = metrics['debt_to_equity']
        metric.save()

        return {'success': True, 'metrics': metrics}

    except AnnualReport.DoesNotExist:
        return {'success': False, 'error': f'Report {report_id} not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def calculate_metrics_for_company(company_id):
    """Calculate metrics for all reports of a company."""
    try:
        company = Company.objects.get(company_id=company_id)
        reports = AnnualReport.objects.filter(company=company)

        results = {'company': company.company_name, 'reports': []}
        for report in reports:
            result = calculate_all_metrics_for_report(report.report_id)
            if result.get('success'):
                results['reports'].append(result['metrics'])

        return results
    except Company.DoesNotExist:
        return {'error': 'Company not found'}