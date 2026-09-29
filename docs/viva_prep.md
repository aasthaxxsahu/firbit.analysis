# Viva / Interview Preparation

Short, natural answers you can actually say out loud - not textbook definitions.

## Basic Questions

1. **What is this project about?**
   Analyzing a month of Fitbit tracker data from 33 users to find
   activity, sleep and engagement patterns, using SQL for analysis,
   Power BI for a dashboard, and Streamlit for an interactive app.

2. **Where did the data come from?**
   A public Fitabase export used in the well-known Bellabeat case
   study - anonymized Fitbit data from 33 users over April 12 to
   May 12, 2016.

3. **Why did you pick this dataset?**
   It's real device data with enough tables (activity, sleep,
   weight, hourly, minute-level) to demonstrate a full pipeline -
   cleaning, SQL, dashboarding and an app - without needing to fake
   or supplement anything.

4. **What was the biggest data quality issue you found?**
   Coverage drops sharply by feature - all 33 users have activity
   data, but only 24 ever logged sleep and only 8 ever logged
   weight. That's a real limitation I had to design around, not
   ignore.

5. **Did you use all the files in the dataset?**
   No. Several files were redundant (dailyCalories/Intensities/Steps
   are just column subsets of dailyActivity), and the minute/second-
   level files (over a million rows each) were kept out of the
   database since the project's scope is daily/hourly analysis.

6. **What tools did you use end-to-end?**
   Python and Pandas for cleaning, MySQL for the database and SQL
   analysis, Power BI for the dashboard, and Streamlit with Plotly
   for the interactive app.

7. **What's the main business question you're answering?**
   How active are these users really, how consistently do they use
   the device, and how do activity, sleep and (for a smaller group)
   weight relate to each other.

8. **How long is the study period?**
   31 days, April 12 to May 12, 2016 - long enough to see daily and
   weekly patterns, too short for long-term trend claims.

9. **What would you do differently with more time?**
   Bring in the minute-level data to look at activity in finer time
   windows, and try to get a bigger weight-tracking sample before
   drawing conclusions there.

10. **What's the single most interesting finding?**
    That weekday and weekend step counts are almost identical
    (8,328 vs 8,295) - I expected a bigger gap, and it says these
    users' routines are pretty fixed day-to-day.

## SQL Questions

1. **Why MySQL and not just Pandas for everything?**
   SQL is the required deliverable, and it's also genuinely a better
   fit for repeatable, filterable queries that the Streamlit app can
   call on demand instead of reloading CSVs each time.

2. **Why is `Id` a foreign key across your tables?**
   Every fact table (daily_activity, sleep_log, etc.) references a
   user, so `Id` ties them back to the `users` table and keeps
   referential integrity - no orphan rows for a user that doesn't exist.

3. **Why composite primary keys like (Id, Date)?**
   Because the natural uniqueness in this data is one row per user
   per day (or per hour) - no single column is unique on its own,
   but the combination is.

4. **Walk me through your CASE WHEN activity bucket query.**
   It classifies each day's TotalSteps into Sedentary, Low Active,
   Somewhat Active or Active using step thresholds, then GROUP BY
   counts how many days fall in each bucket.

5. **Where did you use a window function, and why?**
   RANK() to leaderboard users by total calories, and a running
   SUM() OVER (PARTITION BY Id ORDER BY Date) to show cumulative
   steps over time for one user - GROUP BY alone can't show a
   running trend like that.

6. **Why a CTE instead of a subquery in Q12?**
   It's more readable - naming the bucketed CTE once and then
   grouping on it is clearer than nesting the CASE WHEN logic
   inside the outer query.

7. **How did you handle the fact that not every table has every user?**
   Used INNER JOIN style logic (via IN and WHERE Id IN subqueries)
   deliberately, so results reflect only the users who actually have
   data in both tables being compared, instead of introducing NULLs.

8. **What's the difference between WHERE and HAVING in your queries?**
   WHERE filters rows before grouping (like DeviceWorn = 1), HAVING
   filters after grouping (like keeping only users with more than 5
   sleep records).

9. **How would you find the median step count in MySQL?**
   MySQL has no built-in MEDIAN(), so I used PERCENT_RANK() as a
   window function and pulled the value where the percentile crosses
   0.5.

10. **How do you load the CSVs into MySQL?**
    A small Python script (`sql/load_data.py`) using SQLAlchemy and
    pandas' `to_sql()` - simpler and more portable than LOAD DATA
    INFILE, which needs file-path permissions that vary by OS.

## Power BI Questions

1. **Why didn't you build a strict star schema?**
   There's no separate dimension table with real attributes to
   split out - no age, gender, or name fields exist in the raw
   data - so forcing a star schema would just add an empty-looking
   `users` table for no analytical benefit.

2. **How are your tables related?**
   Mostly kept independent and cross-filtered by shared slicers
   (Id, Date) rather than forced relationships, since not every
   user-day exists in every table.

3. **What DAX measures did you create and why only those?**
   Avg Daily Steps, Avg Calories, Total Users, Pct Days Over 10k
   Steps, Avg Sleep Hours, Avg Sedentary Minutes - each one maps
   directly to a KPI card on the dashboard, nothing extra just to
   pad the measure list.

4. **Explain your Pct Days Over 10k Steps measure.**
   It uses CALCULATE with a filter for TotalSteps >= 10000 to count
   qualifying rows, divided by total rows, via DIVIDE() to avoid a
   divide-by-zero error.

5. **Why a scatter chart for steps vs calories?**
   It's the clearest way to show the relationship between two
   continuous numeric variables at the day level, without pre-
   aggregating and hiding the spread.

6. **How many visuals did you use and why that many?**
   Seven - five charts, one KPI card row, one table - kept
   deliberately close to the 7-10 range so the dashboard reads
   cleanly instead of feeling crammed.

7. **What slicers did you add?**
   Date range and user Id, placed at the top so they apply across
   every visual on the page.

8. **Why one accent color instead of a different color per chart?**
   Consistency - using one primary color for emphasis reads as more
   intentional and professional than a different color per chart.

9. **What would you add if the dashboard needed a second page?**
   A sleep-focused page, since sleep has its own KPIs (avg minutes
   asleep, time awake in bed, nights under 6 hours) that don't fit
   naturally on the activity-focused main page.

10. **How does the Power BI dashboard differ from the Streamlit app?**
    Power BI is for visual, interactive exploration (slicers,
    cross-filtering); Streamlit is for SQL-driven analysis, raw data
    browsing, and displaying the written-up insights - they're not
    duplicating each other.

## Python / Pandas Questions

1. **Why convert date columns instead of leaving them as text?**
   Text dates can't be sorted correctly or used to extract day-of-
   week - converting to `datetime` unlocks all of that with one line.

2. **Why didn't you fill every missing value?**
   The only real missing-data problem was the `Fat` column (97%
   missing) in weight_log, and there was nothing reliable to impute
   it from, so I dropped the column instead of guessing values.

3. **Why keep the zero-step days instead of dropping them?**
   They represent real information - days the device wasn't worn -
   which matters for the adherence question. Dropping them would
   have hidden that finding instead of revealing it.

4. **What's the DeviceWorn flag for?**
   A boolean derived from TotalSteps > 0, so later analysis can
   choose to include or exclude non-wear days on purpose, instead of
   silently mixing them into averages.

5. **Why merge the three hourly CSVs into one table?**
   They share the same key (Id + ActivityHour) and represent one
   logical "hourly activity" record - keeping them as three
   separate files just adds unnecessary joins later.

6. **How did you check for duplicates?**
   `df.duplicated().sum()` on each table - found 3 exact duplicate
   rows in sleepDay and 543 in minuteSleep, both dropped with
   `drop_duplicates()`.

7. **Why drop TrackerDistance but keep TotalDistance?**
   They differ in only 15 of 940 rows by about 0.01 miles on
   average - functionally redundant, so I kept the more commonly
   used TotalDistance and removed the near-duplicate.

8. **What's TotalActiveMinutes and why add it?**
   Sum of Very + Fairly + Lightly active minutes - a single number
   for "how much active time" that several of the analysis
   questions needed, instead of manually adding three columns
   every time.

9. **How did you validate your correlation numbers?**
   Ran `.corr()` directly on the actual cleaned DataFrames and used
   those real values (like r ≈ 0.56 for steps/calories) - nothing
   in the insights section is a guessed number.

10. **What library did you use for plots and why?**
    Plotly, mainly because it renders interactively inside
    Streamlit out of the box and integrates cleanly with `st.plotly_chart`.

## Streamlit Questions

1. **How is your app structured?**
   A sidebar radio menu switching between five pages: Project
   Overview, Data Explorer, SQL Analysis, Insights, and About
   Project.

2. **How does Streamlit connect to MySQL?**
   Through SQLAlchemy's `create_engine` with a `mysql+pymysql`
   connection string, wrapped in a cached `get_engine()` function so
   it doesn't reconnect on every interaction.

3. **Where do your DB credentials come from?**
   Streamlit secrets (`.streamlit/secrets.toml`) when deployed, or
   environment variables locally - never hard-coded in the source.

4. **How do your filters affect the SQL, not just the display?**
   In Data Explorer, selected user Ids and date ranges are built
   into the WHERE clause of the actual query sent to MySQL, using
   bound parameters - so filtering happens in the database, not by
   loading everything and filtering in Pandas.

5. **Why use `st.cache_resource` for the DB engine?**
   To avoid creating a brand new database connection on every widget
   interaction, which would be slow and wasteful.

6. **How did you prevent SQL injection in the custom query box?**
   It only accepts queries starting with SELECT, rejects anything
   with a semicolon (blocking multiple statements), and doesn't use
   raw string formatting for the predefined queries' parameters.

7. **What's the difference between the SQL Analysis page and the Data Explorer page?**
   Data Explorer is for browsing/filtering raw tables; SQL Analysis
   runs the actual documented business-question queries (or a custom
   one) and shows the result plus, for a few, a matching chart.

8. **Why Plotly bar/line charts instead of st.bar_chart?**
   Plotly gives cleaner axis labels, hover tooltips, and more
   control over the look, which matters for something meant to look
   like a real analytics tool rather than a quick sketch.

9. **How would you deploy this app?**
   Streamlit Community Cloud or a small VM, pointing the secrets
   file at a hosted MySQL instance instead of localhost.

10. **What was the trickiest part of building the app?**
    Getting the Data Explorer filters to build a safe, dynamic SQL
    query with SQLAlchemy's bound `IN` parameter (`bindparam` with
    `expanding=True`) instead of string-concatenating user input.

## Project-Specific Questions

1. **Why only 4 core tables instead of importing every CSV?**
   The extra daily files were exact column subsets of dailyActivity,
   and the minute/second files were too granular for the project's
   scope (millions of rows) without adding new business questions
   the daily/hourly data couldn't already answer.

2. **Why is weight data so limited in your analysis?**
   Only 8 of 33 users ever logged weight, so I treat any weight-
   related finding as a small-sample observation, not a general
   conclusion, and say so explicitly.

3. **What does "DeviceWorn" actually solve?**
   It separates real zero-activity from device-not-worn days, so
   averages like "avg daily steps" aren't distorted by days with no
   data at all.

4. **How do you know your 10,000-step benchmark stat (35%) is correct?**
   It's computed directly with a SQL query (`SUM(CASE WHEN
   TotalSteps >= 10000...)`) validated against the same result in
   Pandas - both agree.

5. **Why did you pick 5,000/7,500/10,000 as bucket thresholds?**
   They're commonly used, recognizable step-count tiers (sedentary,
   low active, somewhat active, active) rather than something I
   invented for this project.

6. **What's the practical difference between your SQL queries and your Streamlit "Insights" page?**
   The SQL queries are the raw analysis; the Insights page is the
   write-up - the actual numbers on that page come directly from
   those queries and the Python correlation checks, not from a
   separate estimate.

7. **How did you decide what to drop vs keep during cleaning?**
   Anything with real information (like non-wear days) stayed;
   anything unusable or redundant (Fat column at 97% missing,
   TrackerDistance near-duplicate of TotalDistance) was dropped,
   each with a specific reason.

8. **What would break if you added a new year of data?**
   The composite primary keys (Id, Date) would still hold, but the
   hardcoded "31" used for adherence percentage calculations would
   need to become dynamic (days between min and max date) instead
   of a fixed number.

9. **Why is there no `users` dimension table with real attributes?**
   Because the raw dataset doesn't include any (no age, gender,
   etc.) - adding one anyway would misrepresent what the data
   actually contains.

10. **How did you make sure your insights aren't just guesses?**
    Every number in the Insights section traces back to either a
    SQL query in `analysis_queries.sql` or a `.corr()` / `.describe()`
    call in Pandas - I can point to exactly where each one comes from.

11. **What's the weakest part of this project?**
    The weight/BMI analysis - 8 users isn't enough to say anything
    reliable, and I say that directly instead of overstating it.

12. **Why Streamlit instead of just relying on Power BI?**
    Power BI is better for interactive visual exploration; Streamlit
    lets me expose the actual SQL queries, a custom query box, and a
    written insights page in one place - things Power BI isn't built
    for.

13. **If your manager asked "should we push people to hit 10,000 steps," what would you say from this data alone?**
    That it might help, but the bigger issue this data shows is how
    sedentary the day is overall (~16 hours) - a step goal alone
    doesn't fix that.

14. **What's one thing you'd fact-check before presenting this externally?**
    That the 33-user sample generalizes to a broader population -
    this is a small, specific group over one month, not necessarily
    representative of all Fitbit users.

15. **How would you extend this project for a real company?**
    Bring in a larger, longer-running dataset with demographic data,
    and connect it to actual business outcomes (e.g. subscription
    renewals) rather than just device-usage patterns.
