"""
scraper.py
Fetches job postings from the Adzuna API and stores them in SQLite.
Sign up free at: https://developer.adzuna.com/
"""

import requests
import sqlite3
import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID", "demo")
APP_KEY = os.getenv("ADZUNA_APP_KEY", "demo")
DB_PATH = "data/jobs.db"

SKILL_KEYWORDS = [
    "python", "sql", "excel", "tableau", "power bi", "r ", "java", "spark",
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
    "azure", "aws", "gcp", "docker", "kubernetes", "git", "airflow",
    "pandas", "numpy", "matplotlib", "seaborn", "jupyter", "streamlit",
    "etl", "data warehouse", "snowflake", "databricks", "looker",
    "communication", "agile", "scrum", "jira", "statistics"
]

SEARCH_QUERIES = [
    "data analyst",
    "business analyst",
    "data scientist",
    "business intelligence analyst",
    "machine learning engineer",
]

LOCATIONS = ["Toronto", "Ontario", "Canada"]


def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            salary_min REAL,
            salary_max REAL,
            description TEXT,
            skills TEXT,
            query TEXT,
            created DATE,
            scraped_at TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized.")


def extract_skills(description):
    desc_lower = description.lower()
    found = [skill for skill in SKILL_KEYWORDS if skill in desc_lower]
    return json.dumps(list(set(found)))


def fetch_jobs(query, location, page=1, results_per_page=50):
    url = (
        f"https://api.adzuna.com/v1/api/jobs/ca/search/{page}"
        f"?app_id={APP_ID}&app_key={APP_KEY}"
        f"&results_per_page={results_per_page}"
        f"&what={requests.utils.quote(query)}"
        f"&where={requests.utils.quote(location)}"
        f"&content-type=application/json"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"  API error for '{query}' in {location}: {e}")
        return []


def save_jobs(jobs, query):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    new_count = 0
    for job in jobs:
        job_id = job.get("id", "")
        description = job.get("description", "")
        skills = extract_skills(description)
        location_label = job.get("location", {}).get("display_name", "")
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")
        created = job.get("created", "")[:10] if job.get("created") else None
        try:
            c.execute("""
                INSERT OR IGNORE INTO jobs
                (id, title, company, location, salary_min, salary_max, description, skills, query, created, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id,
                job.get("title", ""),
                job.get("company", {}).get("display_name", ""),
                location_label,
                salary_min,
                salary_max,
                description[:1000],
                skills,
                query,
                created,
                datetime.now().isoformat()
            ))
            if c.rowcount:
                new_count += 1
        except sqlite3.Error as e:
            print(f"  DB error: {e}")
    conn.commit()
    conn.close()
    return new_count


def run_scraper():
    print("=" * 50)
    print("Canada Job Market Scraper")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    init_db()
    total_new = 0
    for query in SEARCH_QUERIES:
        for location in LOCATIONS:
            print(f"\nFetching: '{query}' in {location}...")
            jobs = fetch_jobs(query, location)
            if jobs:
                new = save_jobs(jobs, query)
                print(f"  Saved {new} new jobs ({len(jobs)} fetched)")
                total_new += new
            else:
                print(f"  No results (check API key or network)")
    print(f"\nDone. Total new jobs saved: {total_new}")
    print("=" * 50)


if __name__ == "__main__":
    run_scraper()
