# Business Insights

All numbers below are computed directly from the cleaned dataset
(see `notebooks/01_data_cleaning.py` and `sql/analysis_queries.sql`).
Nothing here is estimated or invented.

## Facts (from data)

1. Steps and calories burned have a moderate positive correlation
   (r ≈ 0.56) across all device-worn days.
2. Only ~35% of logged days reach 10,000+ steps; the average is
   ~8,319 steps/day (median ~8,053).
3. Average sedentary time is ~956 minutes/day (~16 hours).
4. Weekday average steps (8,328) and weekend average steps (8,295)
   are nearly identical - less than 1% apart.
5. The highest average hourly step count occurs at 6-7 PM (~590-600
   steps/hour average); the lowest is 2-4 AM (~6-17 steps/hour).
6. Of 33 total users: 33 (100%) logged activity, 24 (73%) logged
   sleep at least once, 8 (24%) logged weight at least once.
7. Average sleep across all logged nights is ~419 minutes (~7 hours);
   ~24% of logged nights are under 6 hours.
8. Average time in bed but not asleep is ~39 minutes/night.
9. Days with 10,000+ steps average ~889 sedentary minutes vs. ~992
   for days under 10,000 steps - a ~100 minute difference.
10. Sedentary minutes and same-night sleep duration show a moderate
    negative correlation (r ≈ -0.60) among days with both records.
11. Device logging adherence varies widely: 3 of 33 users logged
    fewer than 20 of the 31 study days; one user logged only 4 days.
12. Among the 8 weight-logging users, average BMI is ~25.2 (range
    21.5-47.5); 41 of 67 weight entries were manually typed rather
    than synced from a smart scale.

## Patterns

1. Activity is a daily-routine behavior rather than a weekly one -
   the near-zero weekday/weekend gap suggests fixed routines (work,
   commute) drive activity more than free time does.
2. Feature adoption is layered: everyone tracks steps, most also
   track sleep, but weight logging is a minority behavior.
3. More daytime activity (lower sedentary time) co-occurs with less
   sleep the same night in this data - a correlation, not a proven
   cause.

## Possible problems

1. Roughly two-thirds of days fall short of the 10,000-step
   benchmark, and even "Active" days still average ~15 hours
   sedentary - hitting a step count doesn't mean the inactivity
   problem is solved.
2. Weight/BMI data is too sparse (8 users) to support any reliable
   claim about weight and activity - a real limitation of this
   dataset, not something more analysis can fix.

## Recommendations (interpretation, not data facts)

1. Target engagement nudges around time-of-day (the visible
   afternoon activity dip) rather than day-of-week, since weekday
   and weekend behavior don't meaningfully differ here.
2. Investigate easier weight-logging paths (e.g. smart-scale sync)
   given how few users log it manually - the gap looks like a
   friction problem, not a lack of interest, since sleep logging
   (also passive/automatic) has 3x the adoption.
