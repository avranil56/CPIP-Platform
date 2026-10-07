from django.shortcuts import render, redirect
from django.contrib import messages
from apps.core.models import Company, Risk, Recommendation
from .groq_service import test_groq_connection as test_gemini_connection
from .financial_agent import analyze_financials_with_gemini
from .risk_agent import detect_risks_with_gemini
from .orchestrator import run_full_analysis
from .segment_agent import analyze_segments_with_gemini
from .recommendation_agent import generate_recommendations_with_gemini
from .summary_agent import generate_executive_summary
import logging


def test_gemini(request):
    result = test_gemini_connection()
    if result.get('success'):
        messages.success(request, f"Gemini connected! Response: {result['response']}")
    else:
        messages.error(request, f"Gemini error: {result.get('error')}")
    return redirect('reports:report_list')


def financial_analysis(request, company_id):
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')

    result = analyze_financials_with_gemini(company_id)
    if not result.get('success'):
        messages.error(request, f"Analysis failed: {result.get('error')}")
        return redirect('reports:report_list')

    return render(request, 'agents/financial_analysis.html', {
        'company': company,
        'analysis': result,
    })


def risk_analysis(request, company_id):
    """Run Gemini risk detection for a company."""
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')

    result = detect_risks_with_gemini(company_id)
    if not result.get('success'):
        messages.error(request, f"Risk analysis failed: {result.get('error')}")
        return redirect('reports:report_list')

    # Store risks in database
    risks = result.get('risks', [])
    saved_count = 0

    # Get most recent report as anchor
    latest_report = company.reports.order_by('-year').first()

    if latest_report and risks:
        # Clear old AI-detected risks for this company
        Risk.objects.filter(report__company=company, risk_type__startswith='[AI]').delete()

        for r in risks:
            try:
                risk = Risk.objects.create(
                    report=latest_report,
                    risk_type=f"[AI] {r.get('risk_type', 'Unknown')}",
                    severity=int(r.get('severity', 5)),
                    description=r.get('description', ''),
                    risk_category=r.get('risk_category', 'financial'),
                )
                Recommendation.objects.create(
                    risk=risk,
                    recommendation_text=r.get('mitigation', ''),
                    mitigation_steps=r.get('mitigation', ''),
                    priority=r.get('priority', 'medium'),
                )
                saved_count += 1
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Error saving risk: {e}")

    return render(request, 'agents/risk_analysis.html', {
        'company': company,
        'risks': risks,
        'saved_count': saved_count,
    })



def segment_analysis(request, company_id):
    """Run Gemini segment insight analysis for a company."""
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')

    result = analyze_segments_with_gemini(company_id)
    if not result.get('success'):
        messages.error(request, f"Segment analysis failed: {result.get('error')}")
        return redirect('reports:report_list')

    return render(request, 'agents/segment_analysis.html', {
        'company': company,
        'analysis': result,
    })



def recommendations(request, company_id):
    """Run Gemini strategic recommendation generation for a company."""
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')

    result = generate_recommendations_with_gemini(company_id)
    if not result.get('success'):
        messages.error(request, f"Recommendation failed: {result.get('error')}")
        return redirect('reports:report_list')

    return render(request, 'agents/recommendations.html', {
        'company': company,
        'recs': result,
    })


def executive_summary(request, company_id):
    """Generate boardroom-ready executive summary."""
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')

    result = generate_executive_summary(company_id)
    if not result.get('success'):
        messages.error(request, f"Summary failed: {result.get('error')}")
        return redirect('reports:report_list')

    return render(request, 'agents/executive_summary.html', {
        'company': company,
        'summary': result,
    })


def full_analysis(request, company_id):
    """Run the full multi-agent analysis pipeline."""
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')

    pipeline = run_full_analysis(company_id)

    if pipeline.get('success'):
        messages.success(request, f"Full analysis complete for {company.company_name}")
    else:
        messages.warning(request, f"Analysis completed with {len(pipeline.get('errors', []))} error(s)")

    return render(request, 'agents/full_analysis.html', {
        'company': company,
        'pipeline': pipeline,
    })


def analysis_history(request, company_id):
    """Show history of past full-analysis runs."""
    from apps.core.models import ExecutiveReport
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found')
        return redirect('reports:report_list')

    history = ExecutiveReport.objects.filter(company=company).order_by('-generation_date')[:20]

    return render(request, 'agents/analysis_history.html', {
        'company': company,
        'history': history,
    })


def view_analysis_result(request, report_id):
    """View a specific past analysis result."""
    from apps.core.models import ExecutiveReport
    try:
        report = ExecutiveReport.objects.get(report_id=report_id)
    except ExecutiveReport.DoesNotExist:
        messages.error(request, 'Analysis not found')
        return redirect('reports:report_list')

    return render(request, 'agents/full_analysis.html', {
        'company': report.company,
        'pipeline': report.report_content,
    })