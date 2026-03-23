# Canada Job Market Analyzer

An automated data pipeline and interactive dashboard that tracks in-demand skills, salary ranges, and hiring trends across Canadian data & analytics job postings.

Built with Python, SQLite, Plotly, and Streamlit. Automated weekly via GitHub Actions.

---

## Dashboard Preview

> Running the app locally will allow you to see the interactive dashboard (see Setup below).
> Includes: top skills chart, jobs by role, salary by role, location heatmap, monthly trend.

---

## Features

- **Automated scraper** — fetches live job postings from the Adzuna API across 5 role categories and 3 locations
- **ETL pipeline** — cleans, deduplicates, extracts skill keywords, and exports analytics-ready CSVs
- **Interactive dashboard** — Streamlit + Plotly app with filters by role and location
- **Weekly automation** — GitHub Actions cron job refreshes data every Monday
- **Sample data included** — dashboard works out of the box with no API key needed

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data Collection | Python, Requests, Adzuna API |
| Storage | SQLite |
| ETL & Analysis | Pandas |
| Visualization | Streamlit, Plotly |
| Automation | GitHub Actions |
| Environment | python-dotenv |

---

## Project Structure

```
canada-job-market-analyzer/
├── scraper.py              # Fetches job postings from Adzuna API
├── etl.py                  # Cleans data and exports CSVs
├── dashboard.py            # Streamlit interactive dashboard
├── requirements.txt
├── .env.example            # API key template
├── .github/
│   └── workflows/
│       └── scrape.yml      # GitHub Actions weekly automation
└── data/
    └── exports/            # Auto-generated CSVs after ETL
```

---

## Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/simrahayan/canada-job-market-analyzer.git
cd canada-job-market-analyzer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a free Adzuna API key
Sign up at [developer.adzuna.com](https://developer.adzuna.com/) — it's free and takes 2 minutes.

### 4. Configure your API key
```bash
cp .env.example .env
# Open .env and add your ADZUNA_APP_ID and ADZUNA_APP_KEY
```

### 5. Run the pipeline
```bash
python scraper.py      # Fetch jobs → saves to data/jobs.db
python etl.py          # Clean & export → saves to data/exports/
```

### 6. Launch the dashboard
```bash
streamlit run dashboard.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

> **No API key?** The dashboard displays sample data automatically — you can explore the full UI without any setup.

---

## GitHub Actions (Weekly Automation)

The workflow at `.github/workflows/scrape.yml` runs every Monday at 8am UTC.

To enable it:
1. Go to your repo → **Settings → Secrets → Actions**
2. Add `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` as secrets
3. The workflow runs automatically — or trigger it manually from the **Actions** tab

---

## Key Insights (Sample)

- **Python and SQL** are the top 2 skills across all data roles in Canada
- **Toronto** accounts for ~50% of all data-related postings in Ontario
- **Data Scientists** command the highest average salaries (~$95K CAD)
- Job postings peak in **Q1 and Q3** each year

---

## Author

**Simrah Ayan**
Durham College — Post-Graduate Diplomas in AI & Data Analytics (Honors)
Microsoft Azure Certified (AI-900 + AZ-900)

[LinkedIn](https://www.linkedin.com/in/simrah-ayan) · [GitHub](https://github.com/simrahayan)
