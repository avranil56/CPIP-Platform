from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('reports/', include('apps.reports.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('agents/', include('apps.agents.urls')),
    path('forecasting/', include('apps.forecasting.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)