# CPIP — Corporate Performance Intelligence Platform

An AI-powered business intelligence platform that transforms multi-year annual reports into actionable insights — financial trends, strategic risks, forecasts, and boardroom-ready executive summaries.

![Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Django](https://img.shields.io/badge/django-4.2-darkgreen)

---

##  What It Does

CPIP analyzes corporate annual reports (PDF) and produces:

- **Financial Analysis** — revenue, profit, margins, multi-year trends
- **Risk Detection** — AI-identified risks with severity scoring and mitigation strategies
- **Business Segment Breakdown** — automatic extraction of segment revenues and profitability
- **Forecasting** — 3/5/7-year projections with confidence intervals
- **Executive Summaries** — boardroom-ready PDF reports
- **Company Comparison** — side-by-side analysis of any two companies
- **Strategic Recommendations** — actionable investment and strategy guidance

---

##  Multi-Agent Architecture

The platform runs **7 AI agents in sequence**:

1. **Financial Analysis Agent** — interprets revenue, profit, and margin trends
2. **Risk Detection Agent** — identifies 3-6 major risks with mitigations
3. **Segment Insight Agent** — ranks business segments by performance
4. **Recommendation Agent** — generates strategic actions
5. **Executive Summary Agent** — produces board-level briefing
6. **Forecast Agent** — linear regression projections
7. **Investment Advisor Agent** — capital allocation suggestions

---

##  Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.9, Django 4.2 |
| **Database** | MySQL 8 |
| **AI** | Groq (LLaMA 3.3 / GPT-OSS) |
| **PDF Processing** | pdfplumber |
| **PDF Generation** | ReportLab |
| **Data** | Pandas, NumPy |
| **Charts** | Plotly |
| **Forecasting** | Custom Linear Regression |
| **Frontend** | Bootstrap 5, HTML/CSS |
| **Version Control** | Git, GitHub |

---

##  Quick Start

### Prerequisites
- Python 3.9+
- MySQL 8
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/cpip.git
cd cpip

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MySQL password and Groq API key

# Create database
mysql -u root -p -e "CREATE DATABASE cpip_db;"

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver