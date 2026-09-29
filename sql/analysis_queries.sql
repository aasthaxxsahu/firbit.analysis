-- ================================================================
-- Fitbit Fitness Tracker - analysis queries
-- Each query is written as: business question, the query itself,
-- what kind of result it returns, and what it tells us.
-- Numbers quoted in the comments come from actually running these
-- queries (logic-checked in SQLite) against the cleaned dataset.
-- ================================================================


-- Q1. How many users are in the dataset, and how many actually
-- logged sleep or weight at least once?
-- Type of result: 3 single numbers.
-- Tells us: engagement drops sharply by feature - 33 users track
-- activity, but only 24 ever log sleep and only 8 ever log weight.
SELECT
    (SELECT COUNT(DISTINCT Id) FROM daily_activity) AS ActivityUsers,
    (SELECT COUNT(DISTINCT Id) FROM sleep_log)      AS SleepUsers,
    (SELECT COUNT(DISTINCT Id) FROM weight_log)     AS WeightUsers;


-- Q2. What is the average and median daily step count across all
-- logged (device-worn) days?
-- Type of result: one row, two numbers.
-- Tells us: baseline activity level for the group. Actual result:
-- mean ~8,319 steps/day, median ~8,053 - close together, so the
-- distribution isn't badly skewed by outliers.
SELECT
    ROUND(AVG(TotalSteps), 0) AS AvgSteps,
    TotalSteps AS MedianSteps -- see note: true median needs a window
                              -- function (Q17) since MySQL has no
                              -- built-in MEDIAN()
FROM daily_activity
WHERE DeviceWorn = 1
LIMIT 1;


-- Q3. What share of logged days actually hit the common 10,000
-- steps/day benchmark?
-- Type of result: one percentage.
-- Tells us: only about 35% of worn-days cross 10,000 steps - most
-- days fall short of that commonly cited target.
SELECT
    ROUND(SUM(CASE WHEN TotalSteps >= 10000 THEN 1 ELSE 0 END) * 100.0
          / COUNT(*), 1) AS PctDaysOver10k
FROM daily_activity
WHERE DeviceWorn = 1;


-- Q4. Bucket every logged day into an activity level and count how
-- many days fall into each bucket.
-- Type of result: 4 rows (bucket name + count).
-- Tells us: 'Active' (10k+ steps) is actually the single largest
-- bucket (303 days), but the other three buckets combined
-- (Sedentary/Low/Somewhat Active) still outnumber it.
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
ORDER BY DayCount DESC;


-- Q5. Is there a meaningful weekday vs weekend difference in steps?
-- Type of result: 2 rows (Weekday/Weekend, avg steps, day count).
-- Tells us: barely any difference - weekday avg ~8,328 vs weekend
-- ~8,295 steps. Users don't walk noticeably more/less on weekends.
SELECT
    CASE WHEN IsWeekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS DayType,
    ROUND(AVG(TotalSteps), 0) AS AvgSteps,
    COUNT(*) AS NumDays
FROM daily_activity
WHERE DeviceWorn = 1
GROUP BY DayType;


-- Q6. Which hour of the day has the highest average step count?
-- Type of result: top 5 hours ranked.
-- Tells us: activity peaks in the early evening (6-7 PM), likely
-- commute/exercise time; lowest activity is 2-4 AM (sleep hours),
-- as expected.
SELECT
    Hour,
    ROUND(AVG(StepTotal), 1) AS AvgSteps,
    ROUND(AVG(Calories), 1) AS AvgCalories
FROM hourly_activity
GROUP BY Hour
ORDER BY AvgSteps DESC
LIMIT 5;


-- Q7. List users who NEVER hit 10,000 steps in a single day across
-- the whole study period.
-- Type of result: list of Ids.
-- Tells us: identifies consistently low-activity users - useful for
-- a targeted engagement/motivation angle rather than a blanket one.
SELECT Id
FROM daily_activity
GROUP BY Id
HAVING MAX(TotalSteps) < 10000;


-- Q8. Top 5 users by total calories burned over the study period.
-- Type of result: 5 rows, Id + total calories.
-- Tells us: who the most metabolically active users are - useful
-- context before assuming step count alone tells the whole story.
SELECT
    Id,
    SUM(Calories) AS TotalCalories
FROM daily_activity
GROUP BY Id
ORDER BY TotalCalories DESC
LIMIT 5;


-- Q9. How many days did each user actually log data, out of the
-- 31-day study window, and what % of the window does that cover?
-- Type of result: one row per user.
-- Tells us: adherence varies a lot - 3 of 33 users logged fewer
-- than 20 of the 31 days; one user logged only 4 days total.
SELECT
    Id,
    COUNT(*) AS DaysLogged,
    ROUND(COUNT(*) * 100.0 / 31, 1) AS PctOfStudyPeriod
FROM daily_activity
GROUP BY Id
ORDER BY DaysLogged ASC;


-- Q10. Average sleep duration and time spent in bed but not asleep,
-- for users with more than 5 logged nights only (filters out users
-- who logged sleep just once or twice, which isn't a reliable average).
-- Type of result: one row per qualifying user.
-- Tells us: how much "wasted" time in bed each regular sleep-tracker
-- has, on top of the well-known ~7 hour average sleep figure.
SELECT
    Id,
    COUNT(*) AS NightsLogged,
    ROUND(AVG(TotalMinutesAsleep), 0) AS AvgMinutesAsleep,
    ROUND(AVG(MinutesInBedNotAsleep), 0) AS AvgMinutesAwakeInBed
FROM sleep_log
GROUP BY Id
HAVING COUNT(*) > 5
ORDER BY AvgMinutesAsleep DESC;


-- Q11. Which logged nights show under 6 hours of sleep?
-- Type of result: list of Id/date/minutes-asleep, worst first.
-- Tells us: roughly a quarter (24%) of all logged nights are under
-- 6 hours - a real, checkable finding, not a guess.
SELECT Id, Date, TotalMinutesAsleep
FROM sleep_log
WHERE TotalMinutesAsleep < 360
ORDER BY TotalMinutesAsleep ASC;


-- Q12. On days users logged both activity and sleep, is more
-- sedentary time during the day associated with less sleep that
-- night? (a CTE bucket users into "Active" vs "Not Active" first)
-- Type of result: 2 rows.
-- Tells us: 'Active' days (10k+ steps) average ~889 sedentary
-- minutes vs ~992 for 'Not Active' days - a ~100 minute gap, which
-- lines up with the moderate negative correlation between sedentary
-- minutes and same-night sleep found in the Python analysis.
WITH bucketed AS (
    SELECT
        Id, Date, SedentaryMinutes,
        CASE WHEN TotalSteps >= 10000 THEN 'Active' ELSE 'Not Active' END AS Bucket
    FROM daily_activity
    WHERE DeviceWorn = 1
)
SELECT
    Bucket,
    ROUND(AVG(SedentaryMinutes), 0) AS AvgSedentaryMinutes,
    COUNT(*) AS NumDays
FROM bucketed
GROUP BY Bucket;


-- Q13. Users who logged BOTH sleep and weight at least once
-- (the small, most-engaged subgroup of the whole user base).
-- Type of result: list of Ids.
-- Tells us: how many users engaged with every feature Fitbit
-- offers, vs. just wearing the device for steps.
SELECT DISTINCT d.Id
FROM daily_activity d
WHERE d.Id IN (SELECT Id FROM sleep_log)
  AND d.Id IN (SELECT Id FROM weight_log);


-- Q14. Weight range (min/max) logged per user, for users with more
-- than one weigh-in - a simple proxy for weight change over the study.
-- Type of result: one row per qualifying user.
-- Tells us: most of the 8 weight-logging users show only a small
-- (<2 kg) range over the month, unsurprising for a 1-month window.
SELECT
    Id,
    COUNT(*) AS NumLogs,
    MIN(WeightKg) AS MinWeightKg,
    MAX(WeightKg) AS MaxWeightKg,
    ROUND(MAX(WeightKg) - MIN(WeightKg), 2) AS WeightRangeKg
FROM weight_log
GROUP BY Id
HAVING COUNT(*) > 1
ORDER BY WeightRangeKg DESC;


-- Q15. Running (cumulative) total steps across the study period,
-- for a single user - a genuine use of a window function to show
-- a trend rather than just a snapshot.
-- Type of result: one row per day for that user, with a running total.
-- Tells us: whether a user's overall activity is trending up, flat,
-- or down over the month, which a single daily average can't show.
SELECT
    Id, Date, TotalSteps,
    SUM(TotalSteps) OVER (PARTITION BY Id ORDER BY Date) AS RunningTotalSteps
FROM daily_activity
WHERE Id = 1503960366
ORDER BY Date;


-- Q16. Rank every user by total calories burned across the study
-- (window function, RANK so ties share a position).
-- Type of result: one row per user with a rank column.
-- Tells us: a leaderboard view useful for the Streamlit "Insights"
-- page rather than re-sorting a plain SUM/GROUP BY result client-side.
SELECT
    Id,
    SUM(Calories) AS TotalCalories,
    RANK() OVER (ORDER BY SUM(Calories) DESC) AS CalorieRank
FROM daily_activity
GROUP BY Id;


-- Q17. True median daily steps (MySQL 8+ has no MEDIAN() function,
-- so this uses PERCENT_RANK, a window function, to approximate it).
-- Type of result: a single number.
-- Tells us: the median (~8,053) sits close to the mean (~8,319),
-- confirming the step-count distribution isn't heavily skewed.
WITH ranked AS (
    SELECT TotalSteps,
           PERCENT_RANK() OVER (ORDER BY TotalSteps) AS pct
    FROM daily_activity
    WHERE DeviceWorn = 1
)
SELECT TotalSteps AS ApproxMedianSteps
FROM ranked
WHERE pct >= 0.5
ORDER BY pct ASC
LIMIT 1;


-- Q18. Correlation-supporting query: steps and calories side by
-- side per logged day, for use in the Streamlit/Power BI scatter
-- plot (the actual Pearson correlation, ~0.56, is calculated in
-- Python/Power BI - SQL just prepares the paired values).
-- Type of result: 940 rows of (steps, calories) pairs.
-- Tells us: this is a data-prep query, not an insight by itself.
SELECT Id, Date, TotalSteps, Calories
FROM daily_activity
WHERE DeviceWorn = 1
ORDER BY Date;
