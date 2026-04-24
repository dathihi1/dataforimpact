"""Shared filter components for the dashboard."""
from __future__ import annotations

import streamlit as st
import pandas as pd


def segment_filter(
    df: pd.DataFrame,
    column: str = "rfm_segment",
    key: str = "seg_filter",
) -> pd.DataFrame:
    """Add a multiselect filter for customer segments."""
    segments = sorted(df[column].dropna().unique().tolist())
    selected = st.multiselect(
        "Lọc theo phân khúc (RFM Segment)",
        options=segments,
        default=segments,
        key=key,
    )
    if selected:
        return df[df[column].isin(selected)]
    return df


def country_filter(
    df: pd.DataFrame,
    column: str = "latest_country",
    key: str = "country_filter",
) -> pd.DataFrame:
    """Add a selectbox filter for country."""
    if column not in df.columns:
        return df
    countries = sorted(df[column].dropna().unique().tolist())
    selected = st.selectbox(
        "Lọc theo quốc gia",
        options=["Tất cả"] + countries,
        key=key,
    )
    if selected != "Tất cả":
        return df[df[column] == selected]
    return df


def priority_filter(
    df: pd.DataFrame,
    column: str = "intervention_priority",
    key: str = "priority_filter",
) -> pd.DataFrame:
    """Add a multiselect filter for intervention priorities."""
    priorities = sorted(df[column].dropna().unique().tolist())
    selected = st.multiselect(
        "Lọc theo mức ưu tiên",
        options=priorities,
        default=priorities,
        key=key,
    )
    if selected:
        return df[df[column].isin(selected)]
    return df
