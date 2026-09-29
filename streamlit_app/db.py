"""
MySQL connection helper. Credentials come from Streamlit secrets
(.streamlit/secrets.toml) when deployed, or environment variables when
running locally - never hard-coded here.
"""

import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text


def _get_setting(key, default=None):
    # st.secrets works once secrets.toml exists; fall back to env vars
    # so the app still runs for someone who just exports variables.
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)


@st.cache_resource
def get_engine():
    host = _get_setting("DB_HOST", "localhost")
    user = _get_setting("DB_USER", "root")
    password = _get_setting("DB_PASSWORD", "root123")
    name = _get_setting("DB_NAME", "fitbit_analysis")

    url = f"mysql+pymysql://{user}:{password}@{host}/{name}"
    return create_engine(url, pool_pre_ping=True)


def run_query(sql: str) -> pd.DataFrame:
    """Runs a read-only query and returns a DataFrame. Raises on error
    so the caller can show a clean message instead of a stack trace."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)
