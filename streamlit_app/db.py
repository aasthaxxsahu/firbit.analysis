import os
from pathlib import Path
import streamlit as st
from sqlalchemy import create_engine, text

@st.cache_resource
def get_engine():
    db_path = Path(__file__).parent.parent / "data" / "fitbit.db"
    return create_engine(f"sqlite:///{db_path}")

def run_query(sql: str) -> "pd.DataFrame":
    import pandas as pd
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)