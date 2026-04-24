"""Load & cache dashboard data files."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
import streamlit as st

from .config import (
    CUSTOMER_360_FILE,
    TIME_SERIES_FILE,
    PRODUCT_STATS_FILE,
    MODEL_METRICS_FILE,
    WINBACK_FILE,
)


@st.cache_data(ttl=3600)
def load_customer_360() -> pd.DataFrame:
    return pd.read_csv(CUSTOMER_360_FILE)


@st.cache_data(ttl=3600)
def load_time_series() -> pd.DataFrame:
    df = pd.read_csv(TIME_SERIES_FILE, parse_dates=["month"])
    return df


@st.cache_data(ttl=3600)
def load_product_stats() -> pd.DataFrame:
    return pd.read_csv(PRODUCT_STATS_FILE)


@st.cache_data(ttl=3600)
def load_model_metrics() -> dict:
    with open(MODEL_METRICS_FILE) as f:
        return json.load(f)


@st.cache_data(ttl=3600)
def load_winback() -> pd.DataFrame:
    return pd.read_csv(WINBACK_FILE)
