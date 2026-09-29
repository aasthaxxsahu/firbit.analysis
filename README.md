# Fitbit Fitness Tracker Analysis

Analysis of Fitbit tracker data from 33 users (April 12 - May 12,
2016), using SQL for analysis, Power BI for a dashboard, and
Streamlit for an interactive app.

## Overview

Fitness trackers collect a lot of data, but not all of it is actually
used to understand how people behave day-to-day. This project takes
one month of real Fitbit export data and looks at how active users
actually are, how consistently they use the device, and how activity,
sleep and (for a smaller subset) weight relate to each other.

## Problem statement

Given raw Fitabase exports across several files and granularities
(daily, hourly, minute, second), clean and organize the data into a
queryable form, then answer a set of realistic engagement and
activity questions through SQL analysis, a Power BI dashboard, and an
interactive Streamlit app.

## Objectives

- Clean and structure the raw CSV exports into analysis-ready tables
- Design a relational schema and write SQL queries that answer real
  business questions
- Build a Power BI dashboard for visual, interactive exploration
- Build a Streamlit app for SQL-driven exploration and a written
  insights summary

## Dataset

Source: Fitabase export (the same data used in the well-known
Bellabeat case study), 33 anonymized users, April 12 - May 12, 2016.

Core tables used (see `data/raw/` and `data/cleaned/`):

| Table | Rows | Users covered | Notes |
|---|---|---|---|
| daily_activity | 940 | 33/33 | steps, distance, active minutes, calories |
| hourly_activity | 22,099 | 33/33 | merged from 3 separate hourly files |
| sleep_log | 410 (after dedup) | 24/33 | not every user logs sleep |
| weight_log | 67 | 8/33 | mostly manual entries, Fat column dropped (97% missing) |

Several other files in the raw export (dailyCalories/Intensities/Steps,
and all minute/second-level files) were intentionally left out - see
`docs/viva_prep.md` Q1 under Project-Specific for why.

## Technologies used

Python (Pandas) · MySQL · Power BI · Streamlit · Plotly · SQLAlchemy

## Data cleaning

See `notebooks/01_data_cleaning.py`. Key decisions:
- Converted text dates to real date types
- Dropped `TrackerDistance` (near-duplicate of `TotalDistance`) and
  `Fat` (97% missing, unusable)
- Kept zero-activity days but flagged them with `DeviceWorn`, instead
  of deleting real adherence data
- Removed exact duplicate rows in sleep data
- Added a few derived columns (`DayOfWeek`, `IsWeekend`,
  `TotalActiveMinutes`, `MinutesInBedNotAsleep`)

## SQL analysis

See `sql/schema.sql` for the schema and `sql/analysis_queries.sql`
for 18 documented queries (business question → query → what it
tells us), covering SELECT/WHERE/GROUP BY/HAVING, JOINs, subqueries,
a CTE, and window functions (RANK, running SUM, PERCENT_RANK).

## Power BI dashboard

See `powerbi/dashboard_build_guide.md` for the full step-by-step
(data prep, DAX measures, layout, styling). One page, 7 visuals:
KPI cards, a steps-over-time trend, average steps by hour, activity-
level day counts, a steps-vs-calories scatter, and a top-10-users table.

## Streamlit application

See `streamlit_app/app.py`. Five pages: Project Overview, Data
Explorer (filterable table browser), SQL Analysis (predefined
queries + a safe custom SELECT box), Insights, and About Project.

## Key insights

See `insights/business_insights.md` for the full write-up. Headlines:
- Steps and calories correlate moderately (r ≈ 0.56)
- Only ~35% of days hit 10,000+ steps
- No meaningful weekday/weekend difference in activity
- Feature engagement drops sharply: 100% activity, 73% sleep, 24% weight

## Project structure

```
project/
├── data/
│   ├── raw/                  original Fitabase CSVs (subset used)
│   └── cleaned/               output of the cleaning script
├── sql/
│   ├── schema.sql
│   ├── load_data.py
│   └── analysis_queries.sql
├── notebooks/
│   └── 01_data_cleaning.py
├── streamlit_app/
│   ├── app.py
│   ├── db.py
│   ├── queries.py
│   └── .streamlit/secrets.toml.example
├── powerbi/
│   └── dashboard_build_guide.md
├── insights/
│   └── business_insights.md
├── docs/
│   └── viva_prep.md
├── requirements.txt
├── README.md
└── .gitignore
```

## How to run this project

1. **Set up MySQL**
   ```
   mysql -u root -p < sql/schema.sql
   ```

2. **Load the cleaned data**
   ```
   pip install -r requirements.txt
   export DB_HOST=localhost DB_USER=root DB_PASSWORD=yourpassword DB_NAME=fitbit_analysis
   cd sql
   python load_data.py
   ```

3. **Run the Streamlit app**
   ```
   cd streamlit_app
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # edit secrets.toml with your DB credentials
   streamlit run app.py
   ```

4. **Power BI**: open Power BI Desktop and follow
   `powerbi/dashboard_build_guide.md`, connecting either to the
   cleaned CSVs or the MySQL database.

## Screenshots

_Add screenshots of the Streamlit app pages and the Power BI
dashboard here once built._

## Future improvements

- Bring in the minute-level data for a finer-grained activity view
- Add a second Power BI page focused on sleep
- Extend the study period beyond one month to look at longer trends
