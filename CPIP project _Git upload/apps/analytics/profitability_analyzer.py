from apps.core.models import FinancialMetric, AnnualReport, BusinessSegment, Company


def calculate_profitability_metrics(company_id):
    try:
        company = Company.objects.get(company_id=company_id)
        reports = AnnualReport.objects.filter(company=company).order_by('year')

        results = {
            'company': company.company_name,
            'industry': company.industry,
            'yearly_profitability': [],
            'average_profitability': {},
            'trends': {},
            'segment_profitability': {},
            'overall_assessment': {}
        }

        yearly_data = []
        for report in reports:
            metric = FinancialMetric.objects.filter(report=report).first()
            if not metric:
                continue
            year_data = {
                'year': report.year,
                'revenue': metric.revenue,
                'profit': metric.profit,
                'profit_margin': metric.profit_margin,
            }

            segments = BusinessSegment.objects.filter(report=report)
            if segments:
                seg_list = []
                for seg in segments:
                    margin = None
                    if seg.segment_revenue and seg.segment_revenue != 0 and seg.segment_profit is not None:
                        margin = (seg.segment_profit / seg.segment_revenue) * 100
                    seg_list.append({
                        'name': seg.segment_name,
                        'revenue': seg.segment_revenue,
                        'profit': seg.segment_profit,
                        'margin': margin,
                    })
                year_data['segments'] = seg_list

            yearly_data.append(year_data)
            results['yearly_profitability'].append(year_data)

        margins = [d['profit_margin'] for d in yearly_data if d['profit_margin'] is not None]
        if margins:
            results['average_profitability'] = {
                'avg_profit_margin': sum(margins) / len(margins),
                'years_analyzed': len(yearly_data),
            }

            if len(margins) >= 2:
                if margins[-1] > margins[0]:
                    results['trends']['profit_margin'] = 'Improving'
                elif margins[-1] < margins[0]:
                    results['trends']['profit_margin'] = 'Declining'
                else:
                    results['trends']['profit_margin'] = 'Stable'

            last = margins[-1]
            if last > 15:
                results['overall_assessment']['profitability_level'] = 'Strong'
            elif last > 10:
                results['overall_assessment']['profitability_level'] = 'Moderate'
            elif last > 5:
                results['overall_assessment']['profitability_level'] = 'Average'
            else:
                results['overall_assessment']['profitability_level'] = 'Weak'

            results['overall_assessment']['outlook'] = 'Neutral'
            if results['trends'].get('profit_margin') == 'Improving':
                results['overall_assessment']['outlook'] = 'Positive'
            elif results['trends'].get('profit_margin') == 'Declining':
                results['overall_assessment']['outlook'] = 'Concerning'

        return results
    except Company.DoesNotExist:
        return {'error': 'Company not found'}
    except Exception as e:
        return {'error': str(e)}


def get_profitability_summary(company_id):
    data = calculate_profitability_metrics(company_id)
    if 'error' in data:
        return data
    return {
        'company': data.get('company'),
        'current_profit_margin': data['yearly_profitability'][-1].get('profit_margin') if data.get('yearly_profitability') else None,
        'average_profitability': data.get('average_profitability', {}).get('avg_profit_margin'),
        'trend': data.get('trends', {}).get('profit_margin'),
        'profitability_level': data.get('overall_assessment', {}).get('profitability_level'),
        'outlook': data.get('overall_assessment', {}).get('outlook'),
    }