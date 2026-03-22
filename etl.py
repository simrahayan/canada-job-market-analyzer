"""
etl.py
Cleans raw job data and produces analytics-ready summary tables.
Run after scraper.py: python etl.py
"""

import sqlite3
import pandas as pd
import json
import os
from collections import Counter

DB_PATH = "data/jobs.db"
EXPORT_DIR = "data/exports"


def load_raw():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM jobs", conn)
    conn.close()
    print(f"Loaded {len(df)} raw job records.")
    return df


def clean(df):
    df = df.copy()
    df["title"] = df["title"].str.strip().str.title()
    df["company"] = df["company"].str.strip().str.title()
    df["location"] = df["location"].str.strip()
    df.drop_duplicates(subset=["id"], inplace=True)
    df["salary_mid"] = df[["salary_min", "salary_max"]].mean(axis=1)
    df["created"] = pd.to_datetime(df["created"], errors="coerce")
    df["month"] = df["created"].dt.to_period("M").astype(str)
    print(f"After cleaning: {len(df)} records.")
    return df


def extract_skills_exploded(df):
    rows = []
    for _, row in df.iterrows():
        try:
            skills = json.loads(row["skills"]) if row["skills"] else []
        except Exception:
            skills = []
        for skill in skills:
            rows.append({"job_id": row["id"], "query": row["query"], "skill": skill})
    return pd.DataFrame(rows)


def run_etl():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    df = load_raw()

    if df.empty:
        print("No data found. Run scraper.py first.")
        return

    df = clean(df)

    # --- Top skills ---
    skills_df = extract_skills_exploded(df)
    skill_counts = skills_df.groupby("skill").size().reset_index(name="count")
    skill_counts.sort_values("count", ascending=False, inplace=True)
    skill_counts.to_csv(f"{EXPORT_DIR}/top_skills.csv", index=False)
    print(f"\nTop 10 in-demand skills:")
    print(skill_counts.head(10).to_string(index=False))

    # --- Jobs by query ---
    query_counts = df.groupby("query").size().reset_index(name="job_count")
    query_counts.to_csv(f"{EXPORT_DIR}/jobs_by_role.csv", index=False)

    # --- Jobs by location ---
    location_counts = df.groupby("location").size().reset_index(name="job_count")
    location_counts.sort_values("job_count", ascending=False, inplace=True)
    location_counts.to_csv(f"{EXPORT_DIR}/jobs_by_location.csv", index=False)

    # --- Salary summary ---
    salary_df = df[df["salary_mid"].notna()].copy()
    salary_summary = salary_df.groupby("query")["salary_mid"].agg(
        avg_salary="mean", min_salary="min", max_salary="max", count="count"
    ).reset_index()
    salary_summary["avg_salary"] = salary_summary["avg_salary"].round(0)
    salary_summary.to_csv(f"{EXPORT_DIR}/salary_by_role.csv", index=False)

    # --- Monthly trend ---
    monthly = df.groupby("month").size().reset_index(name="postings")
    monthly.to_csv(f"{EXPORT_DIR}/monthly_trend.csv", index=False)

    # --- Full clean export ---
    df[["id","title","company","location","salary_min","salary_max","salary_mid","query","month"]]\
        .to_csv(f"{EXPORT_DIR}/jobs_clean.csv", index=False)

    print(f"\nAll exports saved to: {EXPORT_DIR}/")
    print("Files: top_skills.csv, jobs_by_role.csv, jobs_by_location.csv,")
    print("       salary_by_role.csv, monthly_trend.csv, jobs_clean.csv")


if __name__ == "__main__":
    run_etl()
