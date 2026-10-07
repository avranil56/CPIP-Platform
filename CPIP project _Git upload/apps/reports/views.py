from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from apps.core.models import Company, AnnualReport
from datetime import datetime


def upload_report(request):
    """View for uploading annual report PDFs"""
    companies = Company.objects.all()

    if request.method == 'POST':
        company_id = request.POST.get('company')
        year = request.POST.get('year')
        report_file = request.FILES.get('report_file')

        if not company_id:
            messages.error(request, 'Please select a company.')
            return redirect('reports:upload_report')

        if not year:
            messages.error(request, 'Please enter the report year.')
            return redirect('reports:upload_report')

        if not report_file:
            messages.error(request, 'Please select a PDF file.')
            return redirect('reports:upload_report')

        if not report_file.name.endswith('.pdf'):
            messages.error(request, 'Only PDF files are allowed.')
            return redirect('reports:upload_report')

        try:
            company = Company.objects.get(company_id=company_id)

            if AnnualReport.objects.filter(company=company, year=year).exists():
                messages.warning(request, f'Report for {company.company_name} ({year}) already exists.')
                return redirect('reports:upload_report')

            fs = FileSystemStorage()
            filename = f"{company.company_name}_{year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            saved_path = fs.save(f'reports/{filename}', report_file)

            AnnualReport.objects.create(
                company=company,
                year=year,
                file_path=saved_path,
                processing_status='pending'
            )

            messages.success(request, f'Report for {company.company_name} ({year}) uploaded successfully!')
            return redirect('reports:upload_report')

        except Company.DoesNotExist:
            messages.error(request, 'Selected company does not exist.')
        except Exception as e:
            messages.error(request, f'Error uploading report: {str(e)}')

    context = {
        'companies': companies,
        'company_count': companies.count(),
        'title': 'Upload Annual Report'
    }
    return render(request, 'reports/upload.html', context)


def report_list(request):
    """View to list all uploaded reports"""
    reports = AnnualReport.objects.select_related('company').all().order_by('-upload_date')

    context = {
        'reports': reports,
        'title': 'All Reports'
    }
    return render(request, 'reports/list.html', context)


def extract_financial_data(request, report_id):
    """Extract financial data from a report."""
    from .financial_extractor import extract_all_metrics_from_report
    from apps.core.models import AnnualReport, FinancialMetric

    try:
        report = AnnualReport.objects.get(report_id=report_id)
        result = extract_all_metrics_from_report(report)
        metrics = result.get('metrics', {})

        existing = FinancialMetric.objects.filter(report=report).first()
        if existing:
            existing.revenue = metrics.get('revenue')
            existing.profit = metrics.get('profit')
            existing.assets = metrics.get('assets')
            existing.liabilities = metrics.get('liabilities')
            existing.debt = metrics.get('debt')
            existing.expenses = metrics.get('expenses')
            existing.save()
            messages.success(request, f"Updated financial data for {report.company.company_name} ({report.year})")
        else:
            FinancialMetric.objects.create(
                report=report,
                revenue=metrics.get('revenue'),
                profit=metrics.get('profit'),
                assets=metrics.get('assets'),
                liabilities=metrics.get('liabilities'),
                debt=metrics.get('debt'),
                expenses=metrics.get('expenses'),
            )
            messages.success(request, f"Extracted financial data for {report.company.company_name} ({report.year})")

        return redirect('reports:report_list')
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('reports:report_list')


def extract_segments(request, report_id):
    """Extract business segments from a report using AI (Groq)."""
    from .ai_segment_extractor import extract_segments_via_ai
    from apps.core.models import AnnualReport, BusinessSegment

    try:
        report = AnnualReport.objects.get(report_id=report_id)
    except AnnualReport.DoesNotExist:
        messages.error(request, f"Report {report_id} not found")
        return redirect('reports:report_list')

    result = extract_segments_via_ai(report)

    if not result.get('success'):
        messages.error(request, f"AI segment extraction failed: {result.get('error')}")
        return redirect('reports:report_list')

    segments = result.get('segments', [])

    if not segments:
        messages.warning(request, f"AI found no segments in {report.company.company_name} ({report.year})")
        return redirect('reports:report_list')

    # Delete old segments for this report
    BusinessSegment.objects.filter(report=report).delete()

    saved = 0
    for seg in segments:
        name = seg.get('name')
        if not name:
            continue
        BusinessSegment.objects.create(
            report=report,
            segment_name=name,
            segment_revenue=seg.get('revenue'),
            segment_profit=seg.get('profit'),
            segment_growth_rate=None,
        )
        saved += 1

    messages.success(
        request,
        f"✓ AI extracted {saved} segments for {report.company.company_name} ({report.year})"
    )
    return redirect('reports:report_list')



def report_list(request):
    """View to list all companies with grouped reports"""
    from apps.core.models import Company
    companies = Company.objects.prefetch_related('reports').all().order_by('company_name')

    context = {
        'companies': companies,
        'title': 'All Reports'
    }
    return render(request, 'reports/list.html', context)