import logging
from datetime import datetime
from apps.core.models import Company, ExecutiveReport

logger = logging.getLogger(__name__)


def run_full_analysis(company_id):
    """
    Run the complete intelligence pipeline for a company:
    1. Financial Analysis
    2. Risk Detection
    3. Segment Analysis
    4. Recommendations
    5. Executive Summary
    6. Forecast
    7. Investment Suggestions

    Returns dict with each step's result + saved ExecutiveReport ID.
    """
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        return {'success': False, 'error': 'Company not found'}

    pipeline = {
        'success': True,
        'company': company.company_name,
        'started_at': datetime.now().isoformat(),
        'steps': {},
        'errors': [],
    }

    # Import all agents (lazy to avoid circular imports)
    from apps.agents.financial_agent import analyze_financials_with_gemini
    from apps.agents.risk_agent import detect_risks_with_gemini
    from apps.agents.segment_agent import analyze_segments_with_gemini
    from apps.agents.recommendation_agent import generate_recommendations_with_gemini
    from apps.agents.summary_agent import generate_executive_summary
    from apps.forecasting.forecaster import forecast_metric
    from apps.forecasting.investment_agent import generate_investment_suggestions

    # Step 1: Financial
    logger.info(f"[Orchestrator] Financial analysis: {company.company_name}")
    try:
        pipeline['steps']['financial'] = analyze_financials_with_gemini(company_id)
    except Exception as e:
        pipeline['steps']['financial'] = {'success': False, 'error': str(e)}
        pipeline['errors'].append(f"Financial: {str(e)}")

    # Step 2: Risk
    logger.info(f"[Orchestrator] Risk detection: {company.company_name}")
    try:
        pipeline['steps']['risk'] = detect_risks_with_gemini(company_id)
    except Exception as e:
        pipeline['steps']['risk'] = {'success': False, 'error': str(e)}
        pipeline['errors'].append(f"Risk: {str(e)}")

    # Step 3: Segments
    logger.info(f"[Orchestrator] Segment analysis: {company.company_name}")
    try:
        pipeline['steps']['segment'] = analyze_segments_with_gemini(company_id)
    except Exception as e:
        pipeline['steps']['segment'] = {'success': False, 'error': str(e)}
        pipeline['errors'].append(f"Segment: {str(e)}")

    # Step 4: Recommendations
    logger.info(f"[Orchestrator] Recommendations: {company.company_name}")
    try:
        pipeline['steps']['recommendation'] = generate_recommendations_with_gemini(company_id)
    except Exception as e:
        pipeline['steps']['recommendation'] = {'success': False, 'error': str(e)}
        pipeline['errors'].append(f"Recommendation: {str(e)}")

    # Step 5: Executive Summary
    logger.info(f"[Orchestrator] Executive summary: {company.company_name}")
    try:
        pipeline['steps']['executive_summary'] = generate_executive_summary(company_id)
    except Exception as e:
        pipeline['steps']['executive_summary'] = {'success': False, 'error': str(e)}
        pipeline['errors'].append(f"Summary: {str(e)}")

    # Step 6: Forecast (no AI — always works)
    logger.info(f"[Orchestrator] Forecast: {company.company_name}")
    try:
        pipeline['steps']['forecast_revenue'] = forecast_metric(company_id, 'revenue', 3)
    except Exception as e:
        pipeline['steps']['forecast_revenue'] = {'success': False, 'error': str(e)}
        pipeline['errors'].append(f"Forecast: {str(e)}")

    # Step 7: Investment
    logger.info(f"[Orchestrator] Investment suggestions: {company.company_name}")
    try:
        pipeline['steps']['investment'] = generate_investment_suggestions(company_id)
    except Exception as e:
        pipeline['steps']['investment'] = {'success': False, 'error': str(e)}
        pipeline['errors'].append(f"Investment: {str(e)}")

    pipeline['completed_at'] = datetime.now().isoformat()
    pipeline['success'] = len(pipeline['errors']) == 0

    # Save executive report to DB
    try:
        report = ExecutiveReport.objects.create(
            company=company,
            report_content=pipeline,
        )
        pipeline['report_id'] = report.report_id
    except Exception as e:
        logger.error(f"Failed to save ExecutiveReport: {e}")
        pipeline['report_id'] = None

    logger.info(f"[Orchestrator] Complete: {company.company_name} — {len(pipeline['errors'])} errors")
    return pipeline