import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text, bindparam

from db import run_query, get_engine
from queries import QUERIES

st.set_page_config(page_title="Fitbit Activity Analysis", layout="wide")
st.markdown("""
<style>
    .main { background-color: #0E1117; }
    h1 { color: #00C2A8; font-weight: 800; }
    h2, h3 { color: #E0E0E0; }
    [data-testid="stMetricValue"] { color: #00C2A8; font-size: 28px; }
    [data-testid="stMetricLabel"] { color: #AAAAAA; }
    .stAlert { border-radius: 10px; }
    section[data-testid="stSidebar"] {
        background-color: #1C2333;
        border-right: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

PAGES = ["Project Overview", "Data Explorer", "SQL Analysis", "Insights", "About Project"]
page = st.sidebar.radio("Navigate", PAGES)

st.sidebar.markdown("---")
st.sidebar.caption("Fitbit Fitness Tracker Data | 33 users | Apr 12 - May 12, 2016")


# ------------------------------------------------------------------
# PROJECT OVERVIEW
# ------------------------------------------------------------------
if page == "Project Overview":
    st.title("Fitbit Activity Analysis")
    st.caption("Daily activity, sleep and weight patterns across 33 Fitbit users")

    try:
        activity = run_query("SELECT * FROM daily_activity WHERE DeviceWorn = 1")
        sleep = run_query("SELECT * FROM sleep_log")
        

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Users tracked", activity["Id"].nunique())
        col2.metric("Avg daily steps", f"{activity['TotalSteps'].mean():,.0f}")
        col3.metric("Avg calories/day", f"{activity['Calories'].mean():,.0f}")
        col4.metric("Avg sleep (hrs)", f"{sleep['TotalMinutesAsleep'].mean() / 60:.1f}")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Users Tracked", "33")
        col2.metric("Days Logged", "31")
        col3.metric("Avg Daily Steps", "7,638")
        col4.metric("Avg Sleep", "6h 59m")  

        st.markdown("### Daily steps trend (all users, averaged)")
        trend = activity.groupby("Date", as_index=False)["TotalSteps"].mean()
        fig = px.line(trend, x="Date", y="TotalSteps")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Days by activity level")
        bucket_df = run_query(QUERIES["Q4. Day count by activity level bucket"])
        fig2 = px.bar(bucket_df, x="ActivityLevel", y="DayCount")
        st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Could not load data from the database. Check your DB connection settings.\n\n{e}")


# ------------------------------------------------------------------
# DATA EXPLORER
# ------------------------------------------------------------------
elif page == "Data Explorer":
    st.title("Data Explorer")

    table_choice = st.sidebar.selectbox(
        "Table", ["daily_activity", "hourly_activity", "sleep_log", "weight_log"]
    )

    try:
        engine = get_engine()
        with engine.connect() as conn:
            all_ids = pd.read_sql(text("SELECT DISTINCT Id FROM users ORDER BY Id"), conn)["Id"].tolist()

        selected_ids = st.sidebar.multiselect("User Id (leave empty for all)", all_ids)

        date_col = "DateTime" if table_choice == "hourly_activity" else "Date"
        date_range = st.sidebar.date_input("Date range", [])

        conditions = []
        params = {}
        if selected_ids:
            conditions.append("Id IN :ids")
            params["ids"] = tuple(selected_ids)
        if len(date_range) == 2:
            conditions.append(f"{date_col} BETWEEN :start AND :end")
            params["start"], params["end"] = date_range

        query = f"SELECT * FROM {table_choice} WHERE 1=1"
        if conditions:
            query += " AND " + " AND ".join(conditions)

        stmt = text(query)
        if selected_ids:
            stmt = stmt.bindparams(bindparam("ids", expanding=True))

        with engine.connect() as conn:
            df = pd.read_sql(stmt, conn, params=params)

        st.write(f"{len(df):,} rows")
        st.dataframe(df, use_container_width=True)
        st.download_button("Download as CSV", df.to_csv(index=False), f"{table_choice}.csv")

    except Exception as e:
        st.error(f"Could not query the database.\n\n{e}")


# ------------------------------------------------------------------
# SQL ANALYSIS
# ------------------------------------------------------------------
elif page == "SQL Analysis":
    st.title("SQL Analysis")
    st.caption("Pick one of the project's analysis queries, or write your own SELECT query below.")

    tab1, tab2 = st.tabs(["Predefined queries", "Custom query"])

    with tab1:
        choice = st.selectbox("Query", list(QUERIES.keys()))
        with st.expander("View SQL"):
            st.code(QUERIES[choice], language="sql")

        try:
            result = run_query(QUERIES[choice])
            st.dataframe(result, use_container_width=True)

            # a couple of these read naturally as a chart too
            if choice.startswith("Q4") or choice.startswith("Q5"):
                fig = px.bar(result, x=result.columns[0], y=result.columns[1])
                st.plotly_chart(fig, use_container_width=True)
            elif choice.startswith("Q6"):
                fig = px.line(result, x="Hour", y="AvgSteps")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Query failed.\n\n{e}")

    with tab2:
        custom_sql = st.text_area("Write a SELECT query", height=120,
                                   placeholder="SELECT Id, AVG(TotalSteps) FROM daily_activity GROUP BY Id")
        if st.button("Run query"):
            cleaned = custom_sql.strip().rstrip(";")
            if not cleaned.lower().startswith("select"):
                st.error("Only SELECT queries are allowed here.")
            elif ";" in cleaned:
                st.error("Only a single statement is allowed.")
            else:
                try:
                    st.dataframe(run_query(cleaned), use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed.\n\n{e}")


# ------------------------------------------------------------------
# INSIGHTS
# ------------------------------------------------------------------
elif page == "Insights":
    st.title("Business Insights")

    st.markdown("""
    ### What the data shows

    - Steps and calories burned move together with a moderate positive
      correlation (r ≈ 0.56) - steps are a reasonable but not perfect
      proxy for how many calories a user burns in a day.
    - Only about **35% of logged days** reach the commonly cited
      10,000-step benchmark; the average day sits at ~8,300 steps.
    - Users spend roughly **16 hours a day sedentary** on average -
      far more than active time, even on days classed as "Active" by
      step count.
    - There is **no meaningful weekday vs weekend difference** in
      step count (8,328 vs 8,295 average steps) - activity habits look
      consistent across the week for this group.
    - Activity **peaks in the early evening (6-7 PM)** and is lowest
      overnight (2-4 AM), matching a typical after-work routine.
    - Device **engagement drops sharply by feature**: all 33 users
      log activity, only 24 (73%) ever log sleep, and only 8 (24%)
      ever log weight.
    - Average sleep across all logged nights is about **7 hours**,
      and about **24% of logged nights are under 6 hours**.
    - Days with 10,000+ steps show noticeably lower sedentary time
      (~889 min) than days under that mark (~992 min) - about a
      100-minute gap.
    - Adherence to daily logging varies a lot: most users logged
      close to all 31 days, but 3 of 33 logged fewer than 20 days,
      including one user with only 4 days of data.

    ### Patterns

    1. Activity is a daily-routine habit, not a weekly one - the lack
       of a weekday/weekend gap suggests these users' routines (job,
       commute, etc.) drive activity more than free time does.
    2. Feature engagement is layered: everyone tracks steps, a
       majority also tracks sleep, but weight logging is a
       minority behavior - likely because it requires manual entry
       or a separate smart scale.
    3. Higher daily activity is associated with less sedentary time
       *and* (per the sleep/sedentary correlation) with worse sleep
       that same night - the data doesn't say why, only that they move
       together.

    ### Possible problems

    1. A large majority of days (65%) fall short of the 10,000-step
       benchmark, and sedentary time dominates the day even for
       "Active" users - the underlying inactivity problem isn't
       solved just by hitting a step goal.
    2. Weight tracking is barely used (8/33 users) and BMI data has
       too small a sample (n=8) to draw reliable conclusions about
       weight and activity - a real gap in what this dataset can tell
       a health-focused business.

    ### Recommendations

    1. Since weekday/weekend patterns don't differ, engagement
       nudges (reminders, challenges) are better timed around
       time-of-day (the 2-5 PM activity dip visible in the hourly
       data) rather than day-of-week.
    2. Given how few users log weight, product efforts aimed at
       "closing the loop" between activity and body metrics should
       focus on making weight logging easier (e.g. smart-scale sync)
       rather than assuming users will type it in manually.

    *Note: recommendations above are interpretation, not directly
    computed from the data - they're included as reasoning built on
    top of the measured facts, not as additional facts.*
    """)


# ------------------------------------------------------------------
# ABOUT PROJECT
# ------------------------------------------------------------------
elif page == "About Project":
    st.title("About This Project")
    st.markdown("""
    **Dataset:** Fitabase export of Fitbit tracker data, 33 anonymized
    users, April 12 - May 12, 2016. Includes daily activity, hourly
    activity, sleep logs and weight logs.

    **Tech stack:** Python (Pandas) for cleaning, MySQL for storage and
    analysis queries, Streamlit + Plotly for this app, Power BI for the
    dashboard.

    **Limitations:**
    - The dataset has no demographic fields (age, gender, etc.), so
      insights are limited to behavior, not who the users are.
    - Sleep and weight data only cover a subset of users (24 and 8 of
      33 respectively), so those findings apply to a smaller,
      more-engaged group, not the full user base.
    - The study window is one month, which is enough to spot daily/
      hourly patterns but too short for long-term trend claims (e.g.
      weight change over time).
    """)
