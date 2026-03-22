"""
dashboard.py
Interactive Streamlit dashboard for Canada Job Market Analyzer.
Run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import sqlite3
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

DB_PATH = "data/jobs.db"
EXPORT_DIR = "data/exports"

st.set_page_config(
    page_title="Canada Job Market Analyzer",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    .metric-label { font-size: 0.85rem; }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame(), pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM jobs", conn)
    conn.close()
    if df.empty:
        return df, pd.DataFrame()
    df["salary_mid"] = df[["salary_min", "salary_max"]].mean(axis=1)
    df["created"] = pd.to_datetime(df["created"], errors="coerce")
    df["month"] = df["created"].dt.to_period("M").astype(str)
    skill_rows = []
    for _, row in df.iterrows():
        try:
            skills = json.loads(row["skills"]) if row["skills"] else []
        except Exception:
            skills = []
        for s in skills:
            skill_rows.append({"query": row["query"], "skill": s, "location": row["location"]})
    skills_df = pd.DataFrame(skill_rows)
    return df, skills_df


def load_sample():
    """Return sample data so the dashboard looks good even without API keys."""
    jobs = pd.DataFrame({
        "id": range(120),
        "title": (["Data Analyst"]*40 + ["Business Analyst"]*30 +
                  ["Data Scientist"]*25 + ["BI Analyst"]*15 + ["ML Engineer"]*10),
        "company": ["Accenture","CIBC","RBC","TD Bank","Shopify","Google","Amazon",
                    "Deloitte","KPMG","Bell"] * 12,
        "location": ["Toronto, ON"]*60 + ["Mississauga, ON"]*20 +
                    ["Ottawa, ON"]*20 + ["Vancouver, BC"]*20,
        "salary_min": [55000,60000,70000,80000,90000]*24,
        "salary_max": [75000,85000,95000,110000,130000]*24,
        "query": (["data analyst"]*40 + ["business analyst"]*30 +
                  ["data scientist"]*25 + ["business intelligence analyst"]*15 +
                  ["machine learning engineer"]*10),
        "month": ["2024-10"]*30 + ["2024-11"]*30 + ["2024-12"]*30 + ["2025-01"]*30,
    })
    jobs["salary_mid"] = (jobs["salary_min"] + jobs["salary_max"]) / 2
    skills_data = [
        "python","sql","excel","tableau","power bi","azure","machine learning",
        "pandas","git","communication","agile","statistics","r ","spark","etl"
    ]
    skill_rows = []
    for i, row in jobs.iterrows():
        count = (i % 5) + 2
        for s in skills_data[:count]:
            skill_rows.append({"query": row["query"], "skill": s, "location": row["location"]})
    return jobs, pd.DataFrame(skill_rows)


# --- LOAD ---
df, skills_df = load_data()
if df.empty:
    st.info("No live data found — showing sample data. Run `python scraper.py` then `python etl.py` to load real jobs.")
    df, skills_df = load_sample()

# --- HEADER ---
st.title("🇨🇦 Canada Job Market Analyzer")
st.caption("Live analytics on data & analytics job postings across Canada")

# --- FILTERS ---
col1, col2 = st.columns(2)
with col1:
    roles = ["All Roles"] + sorted(df["query"].unique().tolist())
    selected_role = st.selectbox("Filter by role", roles)
with col2:
    locations = ["All Locations"] + sorted(df["location"].dropna().unique().tolist())
    selected_location = st.selectbox("Filter by location", locations)

filtered = df.copy()
if selected_role != "All Roles":
    filtered = filtered[filtered["query"] == selected_role]
if selected_location != "All Locations":
    filtered = filtered[filtered["location"] == selected_location]

filtered_skills = skills_df.copy()
if selected_role != "All Roles":
    filtered_skills = filtered_skills[filtered_skills["query"] == selected_role]

# --- METRICS ---
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Postings", f"{len(filtered):,}")
m2.metric("Unique Companies", f"{filtered['company'].nunique():,}")
m3.metric("Avg Salary (CAD)", f"${filtered['salary_mid'].mean():,.0f}" if filtered['salary_mid'].notna().any() else "N/A")
m4.metric("Cities Covered", f"{filtered['location'].nunique()}")
st.markdown("---")

# --- CHARTS ---
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Top In-Demand Skills")
    if not filtered_skills.empty:
        top_skills = filtered_skills.groupby("skill").size().reset_index(name="count")
        top_skills = top_skills.sort_values("count", ascending=False).head(15)
        fig = px.bar(
            top_skills, x="count", y="skill", orientation="h",
            color="count", color_continuous_scale="Teal",
            labels={"count": "Job Postings", "skill": "Skill"}
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False,
                          yaxis={"categoryorder": "total ascending"},
                          margin=dict(l=0, r=0, t=10, b=0), height=380)
        st.plotly_chart(fig, use_container_width=True)

with row1_col2:
    st.subheader("Job Postings by Role")
    role_counts = filtered.groupby("query").size().reset_index(name="count")
    fig2 = px.pie(
        role_counts, values="count", names="query",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig2.update_traces(textposition="inside", textinfo="percent+label")
    fig2.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0), height=380)
    st.plotly_chart(fig2, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Top Hiring Locations")
    loc_counts = filtered.groupby("location").size().reset_index(name="count")
    loc_counts = loc_counts.sort_values("count", ascending=False).head(10)
    fig3 = px.bar(
        loc_counts, x="location", y="count",
        color="count", color_continuous_scale="Blues",
        labels={"count": "Postings", "location": "City"}
    )
    fig3.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30,
                       margin=dict(l=0, r=0, t=10, b=60), height=340)
    st.plotly_chart(fig3, use_container_width=True)

with row2_col2:
    st.subheader("Salary Range by Role (CAD)")
    sal_df = filtered[filtered["salary_mid"].notna()].copy()
    if not sal_df.empty:
        sal_summary = sal_df.groupby("query")["salary_mid"].agg(
            ["mean", "min", "max"]
        ).reset_index()
        sal_summary.columns = ["Role", "Avg", "Min", "Max"]
        sal_summary["Avg"] = sal_summary["Avg"].round(0)
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=sal_summary["Role"], y=sal_summary["Avg"],
            error_y=dict(type="data",
                         array=(sal_summary["Max"] - sal_summary["Avg"]).tolist(),
                         arrayminus=(sal_summary["Avg"] - sal_summary["Min"]).tolist()),
            marker_color="#1D9E75"
        ))
        fig4.update_layout(xaxis_tickangle=-20, yaxis_title="Salary (CAD)",
                           margin=dict(l=0, r=0, t=10, b=60), height=340)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No salary data available for this filter.")

# --- TREND ---
st.subheader("Monthly Posting Trend")
monthly = filtered.groupby("month").size().reset_index(name="postings")
monthly = monthly[monthly["month"].notna() & (monthly["month"] != "NaT")]
if not monthly.empty:
    fig5 = px.line(monthly, x="month", y="postings", markers=True,
                   labels={"month": "Month", "postings": "Job Postings"},
                   color_discrete_sequence=["#0F6E56"])
    fig5.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280)
    st.plotly_chart(fig5, use_container_width=True)

# --- RAW TABLE ---
with st.expander("View raw job data"):
    cols = ["title", "company", "location", "query", "salary_min", "salary_max", "month"]
    show_cols = [c for c in cols if c in filtered.columns]
    st.dataframe(filtered[show_cols].head(200), use_container_width=True)

st.caption("Built by Simrah Ayan · Data sourced from Adzuna API · github.com/simrahayan")
