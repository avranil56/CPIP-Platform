# CPIP — Portfolio Project Summary

## Project Name
**CPIP: Corporate Performance Intelligence Platform**

## One-Line Pitch
An AI-powered business intelligence platform that transforms corporate annual reports into actionable investment and strategy insights in under 60 seconds.

## The Problem It Solves
Financial analysts and corporate strategy teams spend hours manually reading multi-year annual reports to extract financial trends, identify risks, and forecast performance. CPIP automates this entirely — ingesting PDFs, extracting structured data, running 7 AI agents, and producing boardroom-ready reports with a single click.

---

## Tech Stack

**Backend:** Python 3.9, Django 4.2, MySQL 8
**AI Layer:** Groq API (LLaMA 3.3 / GPT-OSS) — 7 specialized agents
**Data Processing:** Pandas, NumPy, pdfplumber
**Visualization:** Plotly (interactive dashboards)
**PDF Generation:** ReportLab
**Forecasting:** Custom Linear Regression
**Frontend:** HTML5, Bootstrap 5, custom CSS theme
**DevOps:** Git, GitHub

---

## Key Features

### 1. AI-Powered Data Extraction
Upload any annual report PDF. The system auto-extracts:
- Financial metrics (revenue, profit, margins, assets, debt)
- Business segments with revenue and profitability
- Multi-year trends

### 2. Seven-Agent AI Pipeline
1. **Financial Analysis Agent** — interprets multi-year performance
2. **Risk Detection Agent** — identifies 3-6 major risks with severity scoring and mitigation strategies
3. **Segment Insight Agent** — ranks business segments by profitability
4. **Recommendation Agent** — generates short/medium/long-term strategic actions
5. **Executive Summary Agent** — produces board-level briefing
6. **Forecast Agent** — projects revenue 3/5/7 years ahead
7. **Investment Advisor Agent** — capital allocation guidance

### 3. Executive Dashboard
Consolidated view with KPIs, trend charts, risk matrix, segment performance, and forecasts.

### 4. Multi-Company Comparison
Select any two companies and generate a side-by-side PDF comparison.

### 5. One-Click PDF Export
Download a print-ready, boardroom-quality report of the full analysis.

### 6. Full Analysis Pipeline
Single button triggers all 7 agents in sequence and saves the run to history.

---

## Architecture Highlights

- **Modular Django apps:** `core`, `reports`, `analytics`, `agents`, `forecasting`, `dashboard`
- **11 database tables** with proper foreign-key cascade deletion
- **Agent orchestration pattern** — sequential AI calls with per-step error isolation (one agent's failure doesn't break the pipeline)
- **Provider-agnostic AI layer** — code designed to swap between Gemini and Groq with minimal changes
- **Theme-consistent UI** — every page follows a dark corporate theme with accent colors

---

## What Makes This Project Stand Out

✅ **Full-stack AI integration** — not just "call an API" but a **7-agent orchestrated pipeline**
✅ **Real-world business value** — automates a real analyst workflow
✅ **Production-grade code** — proper error handling, logging, database design
✅ **Professional UI/UX** — dark corporate theme, interactive Plotly dashboards, PDF export
✅ **End-to-end ownership** — from PDF ingestion to boardroom PDF output

---

## Sample Use Cases

- **Investors** — compare peer companies and validate theses
- **Financial Analysts** — extract structured data from filings in seconds
- **Corporate Strategy** — identify risks and prioritize capital allocation
- **Business Consultants** — rapid multi-year benchmarking

---

## Impact Metrics

- **7 AI agents** in a single workflow
- **Full analysis** delivered in **under 60 seconds**
- **11 database tables** with clean cascade deletion
- **12 interactive pages** (dashboard, analytics, AI agents, forecasting)
- **Zero-install AI** (Groq free tier)

---

## What I Learned / Built

- Multi-agent orchestration pattern
- Provider-agnostic AI abstraction (swapped Gemini → Groq mid-project)
- Financial data extraction from unstructured PDFs
- Interactive chart rendering with Plotly
- Professional PDF generation with ReportLab (tables, layouts, theme)
- Django ORM with complex relationships and cascade behavior

---

## Links

- **GitHub:** [your-repo-url]
- **Live Demo:** [if deployed]
- **Contact:** [your-email]