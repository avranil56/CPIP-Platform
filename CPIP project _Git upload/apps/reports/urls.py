from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('upload/', views.upload_report, name='upload_report'),
    path('list/', views.report_list, name='report_list'),
    path('extract-financial/<int:report_id>/', views.extract_financial_data, name='extract_financial'),
    path('extract-segments/<int:report_id>/', views.extract_segments, name='extract_segments'),
]