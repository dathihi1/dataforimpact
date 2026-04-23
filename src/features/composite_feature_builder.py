from __future__ import annotations

import numpy as np
import pandas as pd


def _minmax(series: pd.Series) -> pd.Series:
    """Min-max normalize a series to [0, 1]. Returns 0 if constant."""
    smin, smax = series.min(), series.max()
    if smax == smin:
        return pd.Series(0.0, index=series.index)
    return (series - smin) / (smax - smin)


def _assign_rfm_segment(row: pd.Series) -> str:
    """Map R/F/M quartile scores to a customer segment label."""
    r, f, m = row["r_quartile"], row["f_quartile"], row["m_quartile"]

    if r >= 4 and f >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal"
    if r >= 3 and f <= 2:
        return "Potential Loyalist"
    if r == 2 and f >= 3:
        return "At Risk"
    if r <= 2 and f >= 4:
        return "Can't Lose Them"
    if r == 2 and f == 2:
        return "Need Attention"
    if r <= 1 and f <= 2:
        return "Lost"
    return "Hibernating"


def build_composite_features(
    churn_features_df: pd.DataFrame,
    customer_col: str = "Customer ID",
) -> pd.DataFrame:
    """Build synthetic/composite features from churn feature output.

    Expects a DataFrame produced by ``build_churn_features()`` containing at
    minimum the columns: frequency_90d, tenure_days, monetary_90d,
    avg_order_value_90d, recency_days, return_rate_90d, recency_velocity.
    """
    required = [
        customer_col,
        "frequency_90d",
        "tenure_days",
        "monetary_90d",
        "avg_order_value_90d",
        "recency_days",
        "return_rate_90d",
        "recency_velocity",
    ]
    missing = [c for c in required if c not in churn_features_df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = churn_features_df.copy()

    # --- purchase_intensity = frequency / max(tenure, 1) ---
    df["purchase_intensity"] = df["frequency_90d"] / df["tenure_days"].clip(lower=1)

    # --- loyalty_score (normalized weighted sum) ---
    norm_freq = _minmax(df["frequency_90d"].astype(float))
    norm_rec = 1.0 - _minmax(df["recency_days"].astype(float))
    norm_tenure = _minmax(df["tenure_days"].astype(float))
    df["loyalty_score"] = (0.4 * norm_freq + 0.3 * norm_rec + 0.3 * norm_tenure).round(4)

    # --- retention_score = (1 - return_rate) * (1 - recency_velocity) ---
    df["retention_score"] = (
        (1.0 - df["return_rate_90d"]) * (1.0 - df["recency_velocity"])
    ).round(4)

    # --- customer_value_score (normalized weighted sum) ---
    norm_monetary = _minmax(df["monetary_90d"].astype(float))
    norm_freq_v = _minmax(df["frequency_90d"].astype(float))
    norm_aov = _minmax(df["avg_order_value_90d"].astype(float))
    df["customer_value_score"] = (
        0.5 * norm_monetary + 0.3 * norm_freq_v + 0.2 * norm_aov
    ).round(4)

    # --- churn_risk_index (dựa vào logic risk_scoring) ---
    # Tần suất thấp, độ gần đây cao (mua từ lâu), chi tiêu thấp -> risk cao
    df["churn_risk_index"] = (
        0.4 * _minmax(df["recency_days"].astype(float)) + 
        0.4 * (1.0 - norm_freq_v) + 
        0.2 * (1.0 - norm_monetary)
    ).round(4)

    # --- rfm_segment (quartile-based categorical) ---
    df["r_quartile"] = pd.qcut(
        df["recency_days"].rank(method="first"), q=4, labels=[4, 3, 2, 1]
    ).astype(int)
    df["f_quartile"] = pd.qcut(
        df["frequency_90d"].rank(method="first"), q=4, labels=[1, 2, 3, 4]
    ).astype(int)
    df["m_quartile"] = pd.qcut(
        df["monetary_90d"].rank(method="first"), q=4, labels=[1, 2, 3, 4]
    ).astype(int)

    df["rfm_segment"] = df.apply(_assign_rfm_segment, axis=1)

    df.drop(columns=["r_quartile", "f_quartile", "m_quartile"], inplace=True)

    return df
