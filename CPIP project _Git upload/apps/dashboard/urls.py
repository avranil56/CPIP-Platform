from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('company/<int:company_id>/', views.company_dashboard, name='company_dashboard'),
    path('executive/<int:company_id>/', views.executive_dashboard, name='executive_dashboard'),
    path('export-pdf/<int:company_id>/', views.export_pdf, name='export_pdf'),
    path('select-comparison/', views.select_comparison, name='select_comparison'),
    path('comparison-pdf/', views.comparison_pdf, name='comparison_pdf'),
]