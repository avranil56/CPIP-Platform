from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('calculate/<int:report_id>/', views.calculate_report_metrics, name='calculate_metrics'),
    path('company/<int:company_id>/', views.company_metrics_dashboard, name='company_metrics'),
    path('comparison/<int:company_id>/', views.company_comparison, name='company_comparison'),
    path('cagr/<int:company_id>/', views.company_cagr, name='company_cagr'),
    path('profitability/<int:company_id>/', views.company_profitability, name='company_profitability'),
]