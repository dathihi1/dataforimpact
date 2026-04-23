from __future__ import annotations

import pandas as pd


def validate_feature_input(
    df: pd.DataFrame,
    required_columns: tuple[str, ...],
    date_col: str,
    customer_col: str,
) -> None:
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        raise TypeError(f"{date_col} must be datetime64 dtype")

    if df[customer_col].isna().any():
        raise ValueError(f"{customer_col} contains null values")

    if df[date_col].isna().any():
        raise ValueError(f"{date_col} contains null values")


def normalize_boolean_column(series: pd.Series, column_name: str) -> pd.Series:
    allowed_true = {True, 1, "1", "true", "True", "TRUE"}
    allowed_false = {False, 0, "0", "false", "False", "FALSE"}

    def _map_value(value: object) -> bool:
        if value in allowed_true:
            return True
        if value in allowed_false:
            return False
        raise ValueError(f"{column_name} contains unsupported boolean value: {value}")

    return series.map(_map_value)
