from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    path('test-gemini/', views.test_gemini, name='test_gemini'),
    path('financial-analysis/<int:company_id>/', views.financial_analysis, name='financial_analysis'),
    path('risk-analysis/<int:company_id>/', views.risk_analysis, name='risk_analysis'),
    path('segment-analysis/<int:company_id>/', views.segment_analysis, name='segment_analysis'),
    path('recommendations/<int:company_id>/', views.recommendations, name='recommendations'),
    path('executive-summary/<int:company_id>/', views.executive_summary, name='executive_summary'),
    path('full-analysis/<int:company_id>/', views.full_analysis, name='full_analysis'),
    path('history/<int:company_id>/', views.analysis_history, name='analysis_history'),
    path('result/<int:report_id>/', views.view_analysis_result, name='view_analysis_result'),
]