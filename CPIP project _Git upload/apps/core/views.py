from django.shortcuts import render
from .models import Company, AnnualReport, BusinessSegment, Risk, ExecutiveReport


def home(request):
    """Landing page shown when users open the platform."""
    stats = {
        'companies': Company.objects.count(),
        'reports': AnnualReport.objects.count(),
        'segments': BusinessSegment.objects.count(),
        'risks': Risk.objects.count(),
        'analyses': ExecutiveReport.objects.count(),
    }
    return render(request, 'home.html', {'stats': stats})