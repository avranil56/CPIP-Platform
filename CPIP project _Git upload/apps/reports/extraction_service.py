from apps.reports.pdf_extractor import (
    extract_text_from_pdf, extract_tables_from_pdf, extract_metadata_from_pdf
)
from apps.reports.financial_extractor import (
    extract_financial_metrics, detect_currency
)
from apps.reports.segment_extractor import extract_segments
from apps.core.models import AnnualReport, FinancialMetric, BusinessSegment
import logging

logger = logging.getLogger(__name__)


def process_report_extraction(report_id):
    """Extract text, tables, financial data, and segments from a PDF."""
    try:
        report = AnnualReport.objects.get(report_id=report_id)
        logger.info(f"Starting extraction: {report.company.company_name} - {report.year}")

        report.processing_status = 'processing'
        report.save()

        text = extract_text_from_pdf(report.file_path)
        tables = extract_tables_from_pdf(report.file_path)
        metadata = extract_metadata_from_pdf(report.file_path)

        # Financial metrics
        raw_metrics = extract_financial_metrics(text)
        currency = detect_currency(text)

        if any([raw_metrics.get('revenue'), raw_metrics.get('profit'), raw_metrics.get('assets')]):
            existing = FinancialMetric.objects.filter(report=report).first()
            if existing:
                existing.revenue = raw_metrics.get('revenue')
                existing.profit = raw_metrics.get('profit')
                existing.net_income = raw_metrics.get('net_income')
                existing.operating_income = raw_metrics.get('operating_income')
                existing.gross_profit = raw_metrics.get('gross_profit')
                existing.ebitda = raw_metrics.get('ebitda')
                existing.assets = raw_metrics.get('assets')
                existing.liabilities = raw_metrics.get('liabilities')
                existing.debt = raw_metrics.get('debt')
                existing.expenses = raw_metrics.get('expenses')
                existing.cash = raw_metrics.get('cash')
                existing.equity = raw_metrics.get('equity')
                existing.save()
            else:
                FinancialMetric.objects.create(
                    report=report,
                    revenue=raw_metrics.get('revenue'),
                    profit=raw_metrics.get('profit'),
                    net_income=raw_metrics.get('net_income'),
                    operating_income=raw_metrics.get('operating_income'),
                    gross_profit=raw_metrics.get('gross_profit'),
                    ebitda=raw_metrics.get('ebitda'),
                    assets=raw_metrics.get('assets'),
                    liabilities=raw_metrics.get('liabilities'),
                    debt=raw_metrics.get('debt'),
                    expenses=raw_metrics.get('expenses'),
                    cash=raw_metrics.get('cash'),
                    equity=raw_metrics.get('equity'),
                )

        # Segments
        raw_segments = extract_segments(text)
        if raw_segments:
            BusinessSegment.objects.filter(report=report).delete()
            for seg in raw_segments:
                BusinessSegment.objects.create(
                    report=report,
                    segment_name=seg.get('name', 'Unknown'),
                    segment_revenue=seg.get('revenue'),
                    segment_profit=seg.get('profit'),
                    segment_growth_rate=seg.get('growth'),
                )

        report.processing_status = 'completed'
        report.save()

        return {
            'success': True,
            'report_id': report_id,
            'company': report.company.company_name,
            'year': report.year,
            'text_length': len(text),
            'tables_count': len(tables),
            'pages': metadata.get('pages', 0),
            'currency': currency,
            'segments_found': len(raw_segments),
        }

    except AnnualReport.DoesNotExist:
        return {'success': False, 'error': f'Report {report_id} not found'}
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}")
        try:
            report = AnnualReport.objects.get(report_id=report_id)
            report.processing_status = 'error'
            report.save()
        except Exception:
            pass
        return {'success': False, 'error': str(e)}


def process_all_pending_reports():
    """Process all pending reports."""
    pending = AnnualReport.objects.filter(processing_status='pending')
    results = [process_report_extraction(r.report_id) for r in pending]
    return {
        'total_processed': len(results),
        'successful': sum(1 for r in results if r.get('success')),
        'failed': sum(1 for r in results if not r.get('success')),
    }