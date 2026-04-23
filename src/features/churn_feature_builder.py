from __future__ import annotations

import pandas as pd

from src.features._validation import normalize_boolean_column, validate_feature_input


def build_churn_features(
    df: pd.DataFrame,
    snapshot_date: pd.Timestamp,
    inactivity_days: int = 60,
    customer_col: str = "Customer ID",
    date_col: str = "InvoiceDate",
    invoice_col: str = "Invoice",
    quantity_col: str = "Quantity",
    value_col: str = "TotalValue",
    return_col: str = "IsReturn",
) -> pd.DataFrame:
    required_columns = (
        customer_col,
        invoice_col,
        date_col,
        quantity_col,
        value_col,
        return_col,
    )
    validate_feature_input(df, required_columns, date_col=date_col, customer_col=customer_col)

    if inactivity_days <= 0:
        raise ValueError("inactivity_days must be > 0")

    snapshot = pd.Timestamp(snapshot_date)
    working = df.copy()
    working[return_col] = normalize_boolean_column(working[return_col], return_col)

    history = working.loc[working[date_col] <= snapshot].copy()

    if history.empty:
        return pd.DataFrame(
            columns=[
                customer_col,
                "snapshot_date",
                "recency_days",
                "frequency_90d",
                "monetary_90d",
                "avg_order_value_90d",
                "return_rate_90d",
                "tenure_days",
                "n_unique_days",
                "avg_days_between_orders",
                "day_of_week_mode",
                "recency_velocity",
                "churn_label",
            ]
        )

    per_customer = history.groupby(customer_col).agg(
        first_date=(date_col, "min"),
        last_date=(date_col, "max"),
    )

    window_start = snapshot - pd.Timedelta(days=89)
    recent = history.loc[(history[date_col] >= window_start) & (history[date_col] <= snapshot)].copy()

    recent_agg = recent.groupby(customer_col).agg(
        frequency_90d=(value_col, "size"),
        monetary_90d=(value_col, "sum"),
        return_count_90d=(return_col, "sum"),
    )

    features = per_customer.join(recent_agg, how="left")
    features[["frequency_90d", "monetary_90d", "return_count_90d"]] = features[
        ["frequency_90d", "monetary_90d", "return_count_90d"]
    ].fillna(0)

    safe_frequency = features["frequency_90d"].replace(0, pd.NA)
    features["avg_order_value_90d"] = (features["monetary_90d"] / safe_frequency).fillna(0.0)
    features["return_rate_90d"] = (features["return_count_90d"] / safe_frequency).fillna(0.0)

    features["recency_days"] = (snapshot - features["last_date"]).dt.days.astype(int)
    features["tenure_days"] = (snapshot - features["first_date"]).dt.days.astype(int)

    # --- Baseline: n_unique_days ---
    features["n_unique_days"] = history.groupby(customer_col)[date_col].apply(
        lambda s: s.dt.date.nunique()
    )

    # --- Baseline: avg_days_between_orders ---
    def _avg_gap(dates: pd.Series) -> float:
        sorted_dates = dates.sort_values()
        gaps = sorted_dates.diff().dt.days.dropna()
        return gaps.mean() if len(gaps) > 0 else 0.0

    features["avg_days_between_orders"] = history.groupby(customer_col)[date_col].apply(_avg_gap)

    # --- Temporal: day_of_week_mode ---
    features["day_of_week_mode"] = history.groupby(customer_col)[date_col].apply(
        lambda s: s.dt.dayofweek.mode().iloc[0] if len(s) > 0 else 0
    ).astype(int)

    # --- Temporal: recency_velocity ---
    safe_tenure = features["tenure_days"].replace(0, pd.NA)
    features["recency_velocity"] = (features["recency_days"] / safe_tenure).fillna(0.0)

    future_end = snapshot + pd.Timedelta(days=inactivity_days)
    future_activity = working.loc[(working[date_col] > snapshot) & (working[date_col] <= future_end)]
    active_customers = set(future_activity[customer_col].unique())

    features["churn_label"] = [0 if customer_id in active_customers else 1 for customer_id in features.index]
    features["snapshot_date"] = snapshot

    out = (
        features.reset_index()[
            [
                customer_col,
                "snapshot_date",
                "recency_days",
                "frequency_90d",
                "monetary_90d",
                "avg_order_value_90d",
                "return_rate_90d",
                "tenure_days",
                "n_unique_days",
                "avg_days_between_orders",
                "day_of_week_mode",
                "recency_velocity",
                "churn_label",
            ]
        ]
        .sort_values(customer_col)
        .reset_index(drop=True)
    )

    out["frequency_90d"] = out["frequency_90d"].astype(int)
    out["churn_label"] = out["churn_label"].astype(int)
    return out
