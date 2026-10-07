import plotly.graph_objects as go
from apps.core.models import AnnualReport, FinancialMetric, Company

# CPIP dark theme palette
CPIP_COLORS = {
    'accent': '#4FA8E8',
    'accent_soft': '#7FC4F0',
    'success': '#3DDC84',
    'danger': '#E8615D',
    'warning': '#E8B84F',
    'purple': '#8B5CF6',
    'pink': '#F472B6',
    'bg': '#11151F',
    'text': '#EDEFF4',
    'grid': '#232A38',
}

CHART_COLORS = ['#4FA8E8', '#3DDC84', '#F59E0B', '#8B5CF6', '#F472B6', '#5EEAD4', '#F87171']


def _base_layout(fig, title=''):
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=CPIP_COLORS['text'])),
        paper_bgcolor=CPIP_COLORS['bg'],
        plot_bgcolor=CPIP_COLORS['bg'],
        font=dict(family='JetBrains Mono, monospace', color=CPIP_COLORS['text'], size=11),
        xaxis=dict(gridcolor=CPIP_COLORS['grid'], showgrid=True, zerolinecolor=CPIP_COLORS['grid']),
        yaxis=dict(gridcolor=CPIP_COLORS['grid'], showgrid=True, zerolinecolor=CPIP_COLORS['grid']),
        margin=dict(l=50, r=30, t=50, b=50),
        height=340,
        hoverlabel=dict(bgcolor=CPIP_COLORS['bg'], font_size=12),
        showlegend=True,
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=10)),
    )
    return fig


def revenue_trend_chart(company_id):
    reports = AnnualReport.objects.filter(company_id=company_id).order_by('year')
    years, values = [], []
    for r in reports:
        m = FinancialMetric.objects.filter(report=r).first()
        if m and m.revenue is not None:
            years.append(r.year)
            values.append(float(m.revenue))
    if not years:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=values, mode='lines+markers',
        line=dict(color=CPIP_COLORS['accent'], width=3),
        marker=dict(size=10, color=CPIP_COLORS['accent_soft']),
        name='Revenue',
        hovertemplate='Year %{x}<br>Revenue: %{y:,.0f}<extra></extra>',
    ))
    return _base_layout(fig, 'Revenue Trend')


def profit_trend_chart(company_id):
    reports = AnnualReport.objects.filter(company_id=company_id).order_by('year')
    years, values = [], []
    for r in reports:
        m = FinancialMetric.objects.filter(report=r).first()
        if m and m.profit is not None:
            years.append(r.year)
            values.append(float(m.profit))
    if not years:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=values, mode='lines+markers',
        line=dict(color=CPIP_COLORS['success'], width=3),
        marker=dict(size=10),
        fill='tozeroy', fillcolor='rgba(61, 220, 132, 0.1)',
        name='Profit',
        hovertemplate='Year %{x}<br>Profit: %{y:,.0f}<extra></extra>',
    ))
    return _base_layout(fig, 'Profit Trend')


def revenue_vs_profit_chart(company_id):
    reports = AnnualReport.objects.filter(company_id=company_id).order_by('year')
    years, revenues, profits = [], [], []
    for r in reports:
        m = FinancialMetric.objects.filter(report=r).first()
        if m and (m.revenue is not None or m.profit is not None):
            years.append(str(r.year))
            revenues.append(float(m.revenue) if m.revenue else 0)
            profits.append(float(m.profit) if m.profit else 0)
    if not years:
        return None
    fig = go.Figure()
    fig.add_trace(go.Bar(x=years, y=revenues, name='Revenue', marker_color=CPIP_COLORS['accent']))
    fig.add_trace(go.Bar(x=years, y=profits, name='Profit', marker_color=CPIP_COLORS['success']))
    fig.update_layout(barmode='group')
    return _base_layout(fig, 'Revenue vs Profit')


def profitability_margin_chart(company_id):
    reports = AnnualReport.objects.filter(company_id=company_id).order_by('year')
    years, margins = [], []
    for r in reports:
        m = FinancialMetric.objects.filter(report=r).first()
        if m and m.profit_margin is not None:
            years.append(r.year)
            margins.append(float(m.profit_margin))
    if not years:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=margins, mode='lines+markers',
        line=dict(color=CPIP_COLORS['warning'], width=3),
        marker=dict(size=10),
        name='Profit Margin',
        hovertemplate='Year %{x}<br>Margin: %{y:.2f}%<extra></extra>',
    ))
    return _base_layout(fig, 'Profit Margin Trend')


def segment_comparison_chart(company_id):
    from apps.core.models import BusinessSegment
    latest = AnnualReport.objects.filter(company_id=company_id).order_by('-year').first()
    if not latest:
        return None
    segments = BusinessSegment.objects.filter(report=latest)
    labels, values = [], []
    for seg in segments:
        if seg.segment_revenue is not None:
            labels.append(seg.segment_name)
            values.append(float(seg.segment_revenue))
    if not values:
        return None
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.45,
        marker=dict(colors=CHART_COLORS),
        textinfo='label+percent', textfont=dict(size=11),
    )])
    return _base_layout(fig, f'Segment Distribution ({latest.year})')


def segment_bar_chart(company_id):
    from apps.core.models import BusinessSegment
    latest = AnnualReport.objects.filter(company_id=company_id).order_by('-year').first()
    if not latest:
        return None
    segments = BusinessSegment.objects.filter(report=latest)
    labels, values = [], []
    for seg in segments:
        if seg.segment_revenue is not None:
            labels.append(seg.segment_name)
            values.append(float(seg.segment_revenue))
    if not values:
        return None
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=values, y=labels, orientation='h',
        marker_color=CPIP_COLORS['purple'],
        hovertemplate='%{y}<br>Revenue: %{x:,.0f}<extra></extra>',
    ))
    return _base_layout(fig, f'Segment Revenue ({latest.year})')


def forecast_chart(company_id, metric='revenue'):
    """Line chart: historical + forecast with confidence band."""
    from apps.forecasting.forecaster import forecast_metric

    result = forecast_metric(company_id, metric, 3)
    if not result.get('success'):
        return None

    hist_years = [r['year'] for r in result['historical']]
    hist_vals = [r['value'] for r in result['historical']]
    fut_years = [r['year'] for r in result['forecast']]
    fut_vals = [r['predicted'] for r in result['forecast']]
    fut_lower = [r['lower'] for r in result['forecast']]
    fut_upper = [r['upper'] for r in result['forecast']]

    fig = go.Figure()

    # Historical line
    fig.add_trace(go.Scatter(
        x=hist_years, y=hist_vals, mode='lines+markers',
        name='Historical',
        line=dict(color=CPIP_COLORS['accent'], width=3),
        marker=dict(size=10),
    ))

    # Forecast line (dashed)
    fig.add_trace(go.Scatter(
        x=fut_years, y=fut_vals, mode='lines+markers',
        name='Forecast',
        line=dict(color=CPIP_COLORS['success'], width=3, dash='dash'),
        marker=dict(size=10, symbol='diamond'),
    ))

    # Confidence band
    fig.add_trace(go.Scatter(
        x=fut_years + fut_years[::-1],
        y=fut_upper + fut_lower[::-1],
        fill='toself',
        fillcolor='rgba(61, 220, 132, 0.15)',
        line=dict(color='rgba(0,0,0,0)'),
        name='80% Confidence',
        hoverinfo='skip',
    ))

    return _base_layout(fig, f'{metric.title()} Forecast')