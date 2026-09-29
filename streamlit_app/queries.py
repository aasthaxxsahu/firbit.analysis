"""
Same queries as sql/analysis_queries.sql, kept here as plain strings so
the Streamlit app can run them directly. Each key is shown as a dropdown
label in the SQL Analysis page.
"""

QUERIES = {
    "Q1. Users tracked per feature (activity / sleep / weight)": """
        SELECT
            (SELECT COUNT(DISTINCT Id) FROM daily_activity) AS ActivityUsers,
            (SELECT COUNT(DISTINCT Id) FROM sleep_log)      AS SleepUsers,
            (SELECT COUNT(DISTINCT Id) FROM weight_log)     AS WeightUsers
    """,

    "Q3. % of days that hit 10,000+ steps": """
        SELECT ROUND(SUM(CASE WHEN TotalSteps >= 10000 THEN 1 ELSE 0 END) * 100.0
                     / COUNT(*), 1) AS PctDaysOver10k
        FROM daily_activity
        WHERE DeviceWorn = 1
    """,

    "Q4. Day count by activity level bucket": """
        SELECT
            CASE
                WHEN TotalSteps < 5000  THEN 'Sedentary'
                WHEN TotalSteps < 7500  THEN 'Low Active'
                WHEN TotalSteps < 10000 THEN 'Somewhat Active'
                ELSE 'Active'
            END AS ActivityLevel,
            COUNT(*) AS DayCount
        FROM daily_activity
        WHERE DeviceWorn = 1
        GROUP BY ActivityLevel
        ORDER BY DayCount DESC
    """,

    "Q5. Weekday vs weekend average steps": """
        SELECT
            CASE WHEN IsWeekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS DayType,
            ROUND(AVG(TotalSteps), 0) AS AvgSteps,
            COUNT(*) AS NumDays
        FROM daily_activity
        WHERE DeviceWorn = 1
        GROUP BY DayType
    """,

    "Q6. Average steps and calories by hour of day": """
        SELECT Hour,
               ROUND(AVG(StepTotal), 1) AS AvgSteps,
               ROUND(AVG(Calories), 1) AS AvgCalories
        FROM hourly_activity
        GROUP BY Hour
        ORDER BY Hour
    """,

    "Q7. Users who never hit 10,000 steps": """
        SELECT Id
        FROM daily_activity
        GROUP BY Id
        HAVING MAX(TotalSteps) < 10000
    """,

    "Q8. Top 5 users by total calories burned": """
        SELECT Id, SUM(Calories) AS TotalCalories
        FROM daily_activity
        GROUP BY Id
        ORDER BY TotalCalories DESC
        LIMIT 5
    """,

    "Q9. Device adherence per user (days logged out of 31)": """
        SELECT Id, COUNT(*) AS DaysLogged,
               ROUND(COUNT(*) * 100.0 / 31, 1) AS PctOfStudyPeriod
        FROM daily_activity
        GROUP BY Id
        ORDER BY DaysLogged ASC
    """,

    "Q10. Average sleep for regular sleep-trackers (>5 nights logged)": """
        SELECT Id, COUNT(*) AS NightsLogged,
               ROUND(AVG(TotalMinutesAsleep), 0) AS AvgMinutesAsleep,
               ROUND(AVG(MinutesInBedNotAsleep), 0) AS AvgMinutesAwakeInBed
        FROM sleep_log
        GROUP BY Id
        HAVING COUNT(*) > 5
        ORDER BY AvgMinutesAsleep DESC
    """,

    "Q11. Nights with under 6 hours of sleep": """
        SELECT Id, Date, TotalMinutesAsleep
        FROM sleep_log
        WHERE TotalMinutesAsleep < 360
        ORDER BY TotalMinutesAsleep ASC
    """,

    "Q12. Sedentary minutes: Active days vs Not Active days": """
        WITH bucketed AS (
            SELECT Id, Date, SedentaryMinutes,
                   CASE WHEN TotalSteps >= 10000 THEN 'Active' ELSE 'Not Active' END AS Bucket
            FROM daily_activity
            WHERE DeviceWorn = 1
        )
        SELECT Bucket, ROUND(AVG(SedentaryMinutes), 0) AS AvgSedentaryMinutes,
               COUNT(*) AS NumDays
        FROM bucketed
        GROUP BY Bucket
    """,

    "Q13. Users who logged both sleep and weight": """
        SELECT DISTINCT d.Id
        FROM daily_activity d
        WHERE d.Id IN (SELECT Id FROM sleep_log)
          AND d.Id IN (SELECT Id FROM weight_log)
    """,

    "Q14. Weight range per user (users with 2+ weigh-ins)": """
        SELECT Id, COUNT(*) AS NumLogs,
               MIN(WeightKg) AS MinWeightKg, MAX(WeightKg) AS MaxWeightKg,
               ROUND(MAX(WeightKg) - MIN(WeightKg), 2) AS WeightRangeKg
        FROM weight_log
        GROUP BY Id
        HAVING COUNT(*) > 1
        ORDER BY WeightRangeKg DESC
    """,

    "Q16. Users ranked by total calories burned": """
        SELECT Id, SUM(Calories) AS TotalCalories,
               RANK() OVER (ORDER BY SUM(Calories) DESC) AS CalorieRank
        FROM daily_activity
        GROUP BY Id
    """,

    "Q18. Steps vs calories, per logged day (for the scatter plot)": """
        SELECT Id, Date, TotalSteps, Calories
        FROM daily_activity
        WHERE DeviceWorn = 1
        ORDER BY Date
    """,
}
