"""
Loads the cleaned CSVs into the MySQL tables created by schema.sql.

Run schema.sql first (creates the empty tables), then run this script.

    python load_data.py

Configure your connection details as environment variables before running
(see the README for how to set these):
    DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
"""

import os
import pandas as pd
from sqlalchemy import create_engine

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "fitbit_analysis")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

CLEAN = "../data/cleaned/"

daily = pd.read_csv(CLEAN + "daily_activity_clean.csv")
hourly = pd.read_csv(CLEAN + "hourly_activity_clean.csv")
sleep = pd.read_csv(CLEAN + "sleep_clean.csv")
weight = pd.read_csv(CLEAN + "weight_clean.csv")

# users table first - every Id that shows up anywhere in the dataset,
# so the foreign keys on the other four tables don't fail
all_ids = pd.concat([daily["Id"], hourly["Id"], sleep["Id"], weight["Id"]]).unique()
users = pd.DataFrame({"Id": all_ids})

with engine.begin() as conn:
    users.to_sql("users", conn, if_exists="append", index=False)
    daily.to_sql("daily_activity", conn, if_exists="append", index=False)
    hourly.to_sql("hourly_activity", conn, if_exists="append", index=False)
    sleep.to_sql("sleep_log", conn, if_exists="append", index=False)
    weight.to_sql("weight_log", conn, if_exists="append", index=False)

print("Loaded:")
print(" users          :", len(users))
print(" daily_activity :", len(daily))
print(" hourly_activity:", len(hourly))
print(" sleep_log      :", len(sleep))
print(" weight_log     :", len(weight))
