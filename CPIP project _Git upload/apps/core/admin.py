from django.contrib import admin
from .models import (
    Company, AnnualReport, FinancialMetric, BusinessSegment,
    Risk, Recommendation, Forecast, ExecutiveReport
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company_id', 'company_name', 'industry', 'created_at']
    search_fields = ['company_name', 'industry']


@admin.register(AnnualReport)
class AnnualReportAdmin(admin.ModelAdmin):
    list_display = ['report_id', 'company', 'year', 'upload_date', 'processing_status']
    list_filter = ['company', 'year', 'processing_status']


@admin.register(FinancialMetric)
class FinancialMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_id', 'report', 'revenue', 'profit', 'profit_margin']


@admin.register(BusinessSegment)
class BusinessSegmentAdmin(admin.ModelAdmin):
    list_display = ['segment_id', 'report', 'segment_name', 'segment_revenue', 'segment_profit']


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ['risk_id', 'report', 'risk_type', 'severity', 'risk_category']


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['recommendation_id', 'risk', 'priority']


@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ['forecast_id', 'company', 'metric_type', 'forecast_year', 'projected_value']


@admin.register(ExecutiveReport)
class ExecutiveReportAdmin(admin.ModelAdmin):
    list_display = ['report_id', 'company', 'generation_date']