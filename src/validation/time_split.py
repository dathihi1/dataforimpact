from __future__ import annotations

import pandas as pd


def _validate_date_column(df: pd.DataFrame, date_col: str) -> None:
    if date_col not in df.columns:
        raise ValueError(f"Missing date column: {date_col}")
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        raise TypeError(f"{date_col} must be datetime64 dtype")


def split_time_holdout(
    df: pd.DataFrame,
    date_col: str,
    val_size: int,
    test_size: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if val_size <= 0 or test_size <= 0:
        raise ValueError("val_size and test_size must be > 0")

    _validate_date_column(df, date_col)

    ordered = df.sort_values(date_col).reset_index(drop=True)
    unique_periods = ordered[date_col].drop_duplicates().tolist()
    minimum_periods = val_size + test_size + 1
    if len(unique_periods) < minimum_periods:
        raise ValueError("Not enough rows for requested train/val/test split")

    train_periods = unique_periods[: -(val_size + test_size)]
    val_periods = unique_periods[-(val_size + test_size) : -test_size]
    test_periods = unique_periods[-test_size:]

    train_df = ordered[ordered[date_col].isin(train_periods)].copy()
    val_df = ordered[ordered[date_col].isin(val_periods)].copy()
    test_df = ordered[ordered[date_col].isin(test_periods)].copy()
    return train_df, val_df, test_df


def rolling_origin_splits(
    df: pd.DataFrame,
    date_col: str,
    initial_train_size: int,
    horizon: int,
    step: int = 1,
) -> list[dict[str, pd.DataFrame]]:
    if initial_train_size <= 0:
        raise ValueError("initial_train_size must be > 0")
    if horizon <= 0:
        raise ValueError("horizon must be > 0")
    if step <= 0:
        raise ValueError("step must be > 0")

    _validate_date_column(df, date_col)

    ordered = df.sort_values(date_col).reset_index(drop=True)
    unique_periods = ordered[date_col].drop_duplicates().tolist()

    splits: list[dict[str, pd.DataFrame]] = []
    train_end = initial_train_size

    while train_end + horizon <= len(unique_periods):
        train_periods = unique_periods[:train_end]
        val_periods = unique_periods[train_end : train_end + horizon]

        train_df = ordered[ordered[date_col].isin(train_periods)].copy()
        val_df = ordered[ordered[date_col].isin(val_periods)].copy()
        splits.append({"train": train_df, "val": val_df})
        train_end += step

    if not splits:
        raise ValueError("No rolling windows could be created with given parameters")

    return splits
