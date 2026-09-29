"""
Data cleaning - Fitbit Fitness Tracker dataset
Raw files -> data/raw/, cleaned output -> data/cleaned/
"""

import pandas as pd

RAW = "../data/raw/"
CLEAN = "../data/cleaned/"

# ---------------------------------------------------------------
# 1. DAILY ACTIVITY (the main daily table)
# ---------------------------------------------------------------
daily = pd.read_csv(RAW + "dailyActivity_merged.csv")

# dates are stored as text ("4/12/2016") - convert to real dates so we can
# sort, filter and pull day-of-week later
daily["ActivityDate"] = pd.to_datetime(daily["ActivityDate"], format="%m/%d/%Y")
daily = daily.rename(columns={"ActivityDate": "Date"})

# TrackerDistance and TotalDistance are basically the same value (they only
# differ in 15 of 940 rows, by ~0.01 miles on average) - drop the tracker
# version and keep TotalDistance as the single distance figure
daily = daily.drop(columns=["TrackerDistance"])

# some days have TotalSteps == 0 and Calories == 0 (77 and 4 rows). These
# aren't real zero-activity days, they're days the device wasn't worn/synced.
# Rather than deleting the rows (that would hide the adherence problem),
# flag them so later analysis can choose to include/exclude them
daily["DeviceWorn"] = daily["TotalSteps"] > 0

# derived columns useful for the questions we're answering
daily["DayOfWeek"] = daily["Date"].dt.day_name()
daily["IsWeekend"] = daily["Date"].dt.dayofweek >= 5
daily["TotalActiveMinutes"] = (
    daily["VeryActiveMinutes"] + daily["FairlyActiveMinutes"] + daily["LightlyActiveMinutes"]
)

daily.to_csv(CLEAN + "daily_activity_clean.csv", index=False)

# ---------------------------------------------------------------
# 2. HOURLY ACTIVITY (three files, same key -> merge into one table)
# ---------------------------------------------------------------
h_cal = pd.read_csv(RAW + "hourlyCalories_merged.csv")
h_int = pd.read_csv(RAW + "hourlyIntensities_merged.csv")
h_step = pd.read_csv(RAW + "hourlySteps_merged.csv")

hourly = h_cal.merge(h_int, on=["Id", "ActivityHour"]).merge(h_step, on=["Id", "ActivityHour"])
hourly["ActivityHour"] = pd.to_datetime(hourly["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
hourly = hourly.rename(columns={"ActivityHour": "DateTime"})
hourly["Hour"] = hourly["DateTime"].dt.hour

hourly.to_csv(CLEAN + "hourly_activity_clean.csv", index=False)

# ---------------------------------------------------------------
# 3. SLEEP
# ---------------------------------------------------------------
sleep = pd.read_csv(RAW + "sleepDay_merged.csv")

# 3 fully duplicated rows (same Id, same date, same everything) - safe to drop
sleep = sleep.drop_duplicates()

sleep["SleepDay"] = pd.to_datetime(sleep["SleepDay"], format="%m/%d/%Y %I:%M:%S %p")
sleep = sleep.rename(columns={"SleepDay": "Date"})

# time spent in bed but not asleep (restless / awake) - not in the raw data,
# but a simple, honest derived column from two columns that already exist
sleep["MinutesInBedNotAsleep"] = sleep["TotalTimeInBed"] - sleep["TotalMinutesAsleep"]

sleep.to_csv(CLEAN + "sleep_clean.csv", index=False)

# ---------------------------------------------------------------
# 4. WEIGHT LOG
# ---------------------------------------------------------------
weight = pd.read_csv(RAW + "weightLogInfo_merged.csv")

# Fat is missing for 65 of 67 rows (97%) - there's nothing to impute this
# from, so the column is dropped rather than filled with guesses
weight = weight.drop(columns=["Fat"])

weight["Date"] = pd.to_datetime(weight["Date"], format="%m/%d/%Y %I:%M:%S %p")

weight.to_csv(CLEAN + "weight_clean.csv", index=False)

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
print("daily_activity_clean :", daily.shape)
print("hourly_activity_clean:", hourly.shape)
print("sleep_clean          :", sleep.shape)
print("weight_clean         :", weight.shape)
