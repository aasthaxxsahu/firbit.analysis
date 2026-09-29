from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

db_path = Path("data/fitbit.db")
db_path.parent.mkdir(exist_ok=True)
engine = create_engine(f"sqlite:///{db_path}")

NAMES = {
    "daily_activity_clean": "daily_activity",
    "hourly_activity_clean": "hourly_activity",
    "sleep_clean": "sleep_log",
    "weight_clean": "weight_log",
}

for csv in Path("data/cleaned").glob("*.csv"):
    table = NAMES.get(csv.stem, csv.stem)
    df = pd.read_csv(csv)
    df.to_sql(table, engine, if_exists="replace", index=False)
    print(f"Loaded {table}: {len(df)} rows")

with engine.connect() as conn:
    conn.execute(text("CREATE TABLE IF NOT EXISTS users AS SELECT DISTINCT Id FROM daily_activity"))
    conn.commit()
print("Created users table")
