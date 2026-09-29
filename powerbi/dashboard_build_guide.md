# Power BI Dashboard - Build Guide

I can't generate an actual `.pbix` binary file for you, but here's the
exact step-by-step to build it in Power BI Desktop using the cleaned
CSVs (or the MySQL database once it's loaded).

## 1. Data preparation

**Get Data** → either:
- Text/CSV: import the four files in `data/cleaned/` directly, or
- MySQL database: connect to `fitbit_analysis` once `sql/load_data.py` has run.

In Power Query (Transform Data), for each table:
- Confirm `Date` / `DateTime` columns are typed as Date / Date-Time (they should import correctly since the cleaning script already converted them).
- Confirm `Id` is typed as Whole Number, not Text, so relationships work correctly.
- No further cleaning needed - the heavy lifting was done in Part 1.

## 2. Data model

Four tables, all keyed by `Id`:

- `daily_activity_clean` (940 rows) - main fact table
- `hourly_activity_clean` (22,099 rows)
- `sleep_clean` (410 rows)
- `weight_clean` (67 rows)

This is **not** a clean star schema, because there's no separate `users`
dimension with attributes worth splitting out (no age/gender/name in the
raw data) - forcing one would just add a table with a single `Id` column
for no real benefit. Instead:

- Relationship: `daily_activity_clean[Id]` → `sleep_clean[Id]` (many-to-one is wrong here since both are daily grain; use **many-to-many** or just rely on cross-filtering by Id, since a user can have a day in one table but not the other)
- Simpler and more reliable in practice: keep the four tables independent (no relationships) and use **Id and Date as slicers** shared across visuals via Power BI's built-in slicer sync, rather than forcing relationships that don't cleanly hold (not every user-day exists in every table).
- If you want one true relationship for demonstration purposes, `daily_activity_clean[Id]` → `weight_clean[Id]` (many-to-one, single direction) is safe since weight_clean's Id list is a subset of daily_activity's.

## 3. DAX measures

Only the ones actually needed - don't add more just to fill a list.

```
Avg Daily Steps = AVERAGE(daily_activity_clean[TotalSteps])

Avg Calories = AVERAGE(daily_activity_clean[Calories])

Total Users = DISTINCTCOUNT(daily_activity_clean[Id])

Pct Days Over 10k Steps =
DIVIDE(
    CALCULATE(COUNTROWS(daily_activity_clean), daily_activity_clean[TotalSteps] >= 10000),
    COUNTROWS(daily_activity_clean)
)

Avg Sleep Hours = AVERAGE(sleep_clean[TotalMinutesAsleep]) / 60

Avg Sedentary Minutes = AVERAGE(daily_activity_clean[SedentaryMinutes])
```

Plain-language explanation of each:
- **Avg Daily Steps / Avg Calories**: the two headline KPIs.
- **Total Users**: how many distinct devices are represented in whatever's currently filtered.
- **Pct Days Over 10k Steps**: the step-goal-achievement KPI (~35% overall).
- **Avg Sleep Hours**: converts minutes to hours for a more readable KPI card.
- **Avg Sedentary Minutes**: supports the "users are mostly sedentary" finding.

## 4. Dashboard layout (one page, 16:9)

```
HEADER: "Fitbit User Activity Dashboard" + date range slicer + Id slicer
─────────────────────────────────────────────
KPI CARDS: Total Users | Avg Daily Steps | Avg Calories | Pct Days Over 10k | Avg Sleep Hours
─────────────────────────────────────────────
LEFT: Line chart - Avg Steps by Date (Axis: Date, Values: Avg Daily Steps)
RIGHT: Bar chart - Avg Steps by Hour of Day (Axis: Hour, Values: AvgSteps) [from hourly_activity_clean]
─────────────────────────────────────────────
LEFT: Bar chart - Day count by Activity Level bucket (needs a calculated column bucketing TotalSteps, same logic as SQL Q4)
RIGHT: Scatter chart - TotalSteps (X) vs Calories (Y), one point per day (Legend: none, too many points already)
─────────────────────────────────────────────
BOTTOM: Table - Top 10 users by Total Calories (Id, Sum of Calories, Avg Steps)
```

That's 7 visuals total (5 charts + 1 table + KPI card group), within your
7-10 target.

## 5. Styling

- **Title:** "Fitbit User Activity Dashboard"
- **Subtitle:** "33 users · April 12 - May 12, 2016"
- **Palette:** one accent color (e.g. a mid blue `#2E5EAA`) for primary bars/lines, neutral grey (`#595959`) for secondary elements, white background - avoid a multi-color rainbow palette across charts.
- **Font:** Segoe UI (Power BI default) - fine as-is, no need to change.
- **Background:** plain white or very light grey (`#F5F5F5`), no gradients.
- **Slicers:** top-right of the header row - Date range and Id.
- **Page size:** 16:9 (1280×720), Power BI's default.
- **Tooltips:** default tooltips are fine; for the scatter chart, add `Id` to the tooltip field so hovering shows which user a point belongs to.

Keep visuals to the 7 listed above - resist adding more just because there's empty space.
