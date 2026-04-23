from __future__ import annotations

from typing import Any

import pandas as pd

DEFAULT_REQUIRED_COLUMNS = (
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
    "TotalValue",
    "InvoiceType",
    "IsReturn",
)

DEFAULT_CRITICAL_COLUMNS = (
    "InvoiceDate",
    "Customer ID",
    "TotalValue",
)


def run_data_contract_checks(
    df: pd.DataFrame,
    required_columns: tuple[str, ...] = DEFAULT_REQUIRED_COLUMNS,
    critical_columns: tuple[str, ...] = DEFAULT_CRITICAL_COLUMNS,
) -> dict[str, Any]:
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    missing_critical_columns = [column for column in critical_columns if column not in df.columns]
    if missing_critical_columns:
        raise ValueError(f"Missing critical columns: {missing_critical_columns}")

    null_report = df.loc[:, list(critical_columns)].isna().sum()
    if (null_report > 0).any():
        raise ValueError(f"Critical null values detected:\n{null_report}")

    if not pd.api.types.is_datetime64_any_dtype(df["InvoiceDate"]):
        raise TypeError("InvoiceDate must be datetime64 dtype.")

    return {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "date_min": df["InvoiceDate"].min(),
        "date_max": df["InvoiceDate"].max(),
    }
