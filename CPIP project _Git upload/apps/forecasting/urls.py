from django.urls import path
from . import views

app_name = 'forecasting'

urlpatterns = [
    path('company/<int:company_id>/', views.company_forecast, name='company_forecast'),
    path('save/<int:company_id>/', views.save_forecast, name='save_forecast'),
    path('investments/<int:company_id>/', views.investment_suggestions, name='investment_suggestions'),
]