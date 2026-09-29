from getpass import getpass
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text

password = quote_plus(getpass("MySQL root password: "))

# 1. Create the database if it doesn't exist
server = create_engine(f"mysql+pymysql://root:{password}@localhost")
with server.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS fitbit_analysis"))
    conn.commit()

# 2. Load every cleaned CSV as a table
engine = create_engine(f"mysql+pymysql://root:{password}@localhost/fitbit_analysis")
NAMES = {
    "daily_activity_clean": "daily_activity",
    "hourly_activity_clean": "hourly_activity",
    "sleep_clean": "sleep_log",
    "weight_clean": "weight_log",
}

for csv in Path("project/data/cleaned").glob("*.csv"):
    table = NAMES.get(csv.stem, csv.stem)
    df = pd.read_csv(csv)
    df.to_sql(table, engine, if_exists="replace", index=False)
    print(f"Loaded {table}: {len(df)} rows")
    # Build a "users" table from the distinct IDs in daily_activity
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users AS
        SELECT DISTINCT Id FROM daily_activity
    """))
    conn.commit()
print("Created users table")