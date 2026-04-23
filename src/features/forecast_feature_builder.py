from __future__ import annotations

import pandas as pd

from src.features._validation import validate_feature_input


def build_forecast_features(
    df: pd.DataFrame,
    customer_col: str = "Customer ID",
    date_col: str = "InvoiceDate",
    value_col: str = "TotalValue",
) -> pd.DataFrame:
    required_columns = (customer_col, date_col, value_col)
    validate_feature_input(df, required_columns, date_col=date_col, customer_col=customer_col)

    output_columns = [
        customer_col,
        "ds",
        "revenue",
        "lag_1",
        "lag_3",
        "rolling_mean_3",
        "month_index",
        "month_number",
        "purchase_trend",
    ]

    if df.empty:
        return pd.DataFrame(columns=output_columns)

    monthly = (
        df.assign(ds=lambda x: x[date_col].dt.to_period("M").dt.to_timestamp())
        .groupby([customer_col, "ds"], as_index=False)[value_col]
        .sum()
        .rename(columns={value_col: "revenue"})
        .sort_values([customer_col, "ds"])
    )

    rows: list[pd.DataFrame] = []
    for customer_id, group in monthly.groupby(customer_col):
        group = group.sort_values("ds").reset_index(drop=True)
        full_ds = pd.date_range(group["ds"].min(), group["ds"].max(), freq="MS")
        full = pd.DataFrame({customer_col: customer_id, "ds": full_ds})
        full = full.merge(group, on=[customer_col, "ds"], how="left")
        full["revenue"] = full["revenue"].fillna(0.0)
        rows.append(full)

    out = pd.concat(rows, ignore_index=True).sort_values([customer_col, "ds"]).reset_index(drop=True)

    out["lag_1"] = out.groupby(customer_col)["revenue"].shift(1)
    out["lag_3"] = out.groupby(customer_col)["revenue"].shift(3)
    out["rolling_mean_3"] = out.groupby(customer_col)["revenue"].transform(
        lambda s: s.shift(1).rolling(window=3, min_periods=1).mean()
    )
    out["month_index"] = out.groupby(customer_col).cumcount()
    out["month_number"] = out["ds"].dt.month

    # --- Temporal: purchase_trend ---
    out["purchase_trend"] = out.groupby(customer_col)["revenue"].pct_change(periods=1)

    return out[output_columns]
