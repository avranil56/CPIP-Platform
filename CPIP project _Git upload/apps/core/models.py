from django.db import models


class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        db_table = 'company'


class AnnualReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reports')
    year = models.IntegerField()
    file_path = models.CharField(max_length=500)
    upload_date = models.DateTimeField(auto_now_add=True)
    processing_status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return f"{self.company.company_name} - {self.year}"

    class Meta:
        db_table = 'annual_reports'


class FinancialMetric(models.Model):
    metric_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(AnnualReport, on_delete=models.CASCADE, related_name='financial_metrics')
    revenue = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    profit = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    debt = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    expenses = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    assets = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    liabilities = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    revenue_growth_yoy = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profit_growth_yoy = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profit_margin = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    debt_to_equity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_income = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    operating_income = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    gross_profit = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    ebitda = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    cash = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    equity = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'financial_metrics'


class BusinessSegment(models.Model):
    segment_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(AnnualReport, on_delete=models.CASCADE, related_name='segments')
    segment_name = models.CharField(max_length=255)
    segment_revenue = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    segment_profit = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    segment_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    segment_profit_margin = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.segment_name

    class Meta:
        db_table = 'business_segments'


class Risk(models.Model):
    risk_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(AnnualReport, on_delete=models.CASCADE, related_name='risks')
    risk_type = models.CharField(max_length=100)
    severity = models.IntegerField()
    description = models.TextField()
    risk_category = models.CharField(max_length=50, choices=[
        ('operational', 'Operational'),
        ('financial', 'Financial'),
        ('market', 'Market'),
        ('compliance', 'Compliance')
    ], default='financial')
    detected_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.risk_type} - {self.severity}/10"

    class Meta:
        db_table = 'risks'


class Recommendation(models.Model):
    recommendation_id = models.AutoField(primary_key=True)
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_text = models.TextField()
    mitigation_steps = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=20, choices=[
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], default='medium')
    expected_impact = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendations'


class Forecast(models.Model):
    forecast_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='forecasts')
    metric_type = models.CharField(max_length=50, choices=[
        ('revenue', 'Revenue'),
        ('profit', 'Profit'),
        ('segment', 'Segment')
    ])
    forecast_year = models.IntegerField()
    projected_value = models.DecimalField(max_digits=20, decimal_places=2)
    confidence_interval_lower = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    confidence_interval_upper = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'forecasts'


class ExecutiveReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='executive_reports')
    generation_date = models.DateTimeField(auto_now_add=True)
    report_content = models.JSONField(null=True, blank=True)
    pdf_file_path = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'executive_reports'