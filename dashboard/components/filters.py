"""Shared filter components for the dashboard."""
from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np


# ── Time-window helpers ───────────────────────────────────────────

_WINDOW_PRESETS = {
    "30 ngày": 30,
    "60 ngày": 60,
    "90 ngày (mặc định)": 90,
    "Tùy chỉnh": None,
}


def time_window_filter(key: str = "tw_filter") -> int:
    """Sidebar widget: chọn khoảng thời gian phân tích (ngày).

    Returns
    -------
    int
        Số ngày được chọn (30 / 60 / 90 / custom).
    """
    st.sidebar.subheader("Khoảng thời gian")
    preset = st.sidebar.radio(
        "Chọn khoảng",
        options=list(_WINDOW_PRESETS.keys()),
        index=2,
        key=f"{key}_preset",
    )
    if _WINDOW_PRESETS[preset] is not None:
        days = _WINDOW_PRESETS[preset]
    else:
        days = st.sidebar.number_input(
            "Nhập số ngày (7 – 365)",
            min_value=7,
            max_value=365,
            value=90,
            step=1,
            key=f"{key}_custom",
        )
    if days != 90:
        st.sidebar.caption(
            f"⚠ Khoảng {days}d: giá trị được ước tính từ dữ liệu 90d"
            if days not in (30, 90)
            else ""
        )
    return int(days)


def resolve_window_metrics(df: pd.DataFrame, window_days: int) -> pd.DataFrame:
    """Thêm các cột ``w_monetary``, ``w_frequency``, ``w_aov`` vào df
    tương ứng với ``window_days`` được chọn.

    Tất cả các khoảng đều dùng **distinct invoices** cho ``w_frequency``
    để nhất quán đơn vị (``frequency_90d`` đếm line-items, không phải invoices).

    Logic:
    - window <= 30d  → scale từ ``spend_last30d`` (chính xác với 30d, ước tính với <30d)
    - 30d < window < 90d → ``spend_last30d + spend_prev60d * ((window-30)/60)`` (nội suy)
    - 90d             → ``monetary_90d`` / ``distinct_invoices_90d``    (chính xác)
    - window > 90d    → scale tỷ lệ từ 90d × (window_days / 90)

    Ưu tiên dùng data bucket gần nhất để ``w_monetary > 0``
    phản ánh đúng khách hàng active trong window đó.

    Cột trả về: ``w_monetary`` (£), ``w_frequency`` (distinct invoices),
    ``w_aov`` (£/invoice).
    """
    out = df.copy()

    has_30d = "spend_last30d" in df.columns and "orders_last30d" in df.columns
    has_prev = "spend_prev60d" in df.columns and "orders_prev60d" in df.columns
    has_inv90 = "distinct_invoices_90d" in df.columns

    if window_days == 90:
        out["w_monetary"] = out["monetary_90d"]
        out["w_frequency"] = out["distinct_invoices_90d"] if has_inv90 else out["monetary_90d"] * 0

    elif window_days <= 30 and has_30d:
        scale = window_days / 30.0
        out["w_monetary"] = out["spend_last30d"] * scale
        out["w_frequency"] = out["orders_last30d"] * scale

    elif window_days < 90 and has_30d and has_prev:
        extra = (window_days - 30) / 60.0
        out["w_monetary"] = out["spend_last30d"] + out["spend_prev60d"] * extra
        out["w_frequency"] = out["orders_last30d"] + out["orders_prev60d"] * extra

    else:
        scale = window_days / 90.0
        out["w_monetary"] = out["monetary_90d"] * scale
        freq_base = out["distinct_invoices_90d"] if has_inv90 else out["monetary_90d"] * 0
        out["w_frequency"] = freq_base * scale

    out["w_monetary"] = out["w_monetary"].clip(lower=0)
    out["w_frequency"] = out["w_frequency"].clip(lower=0)
    out["w_aov"] = np.where(
        out["w_frequency"] > 0,
        out["w_monetary"] / out["w_frequency"],
        0.0,
    )
    return out


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


def business_model_filter(
    df: pd.DataFrame,
    column: str = "customer_model",
    key: str = "bm_filter",
) -> pd.DataFrame:
    """Add a selectbox filter for B2B / B2C customer model."""
    if column not in df.columns:
        return df
    options = sorted(df[column].dropna().unique().tolist())
    selected = st.selectbox(
        "Loại khách hàng (B2B / B2C)",
        options=["Tất cả"] + options,
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
