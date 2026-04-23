import pandas as pd
import pytest

from src.data_contract import run_data_contract_checks


def _valid_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Invoice": ["1", "2"],
            "StockCode": ["A", "B"],
            "Description": ["d1", "d2"],
            "Quantity": [1, 2],
            "InvoiceDate": pd.to_datetime(["2010-01-01", "2010-01-02"]),
            "Price": [10.0, 12.0],
            "Customer ID": [1001, 1002],
            "Country": ["UK", "UK"],
            "TotalValue": [10.0, 24.0],
            "InvoiceType": ["Sale", "Sale"],
            "IsReturn": [False, False],
        }
    )


def test_contract_fails_when_required_column_missing():
    df = _valid_df().drop(columns=["StockCode"])

    with pytest.raises(ValueError, match="Missing required columns"):
        run_data_contract_checks(df)


def test_contract_fails_when_critical_column_has_null():
    df = _valid_df()
    df.loc[0, "TotalValue"] = None

    with pytest.raises(ValueError, match="Critical null values"):
        run_data_contract_checks(df)


def test_contract_fails_when_invoice_date_not_datetime():
    df = _valid_df()
    df["InvoiceDate"] = ["2010-01-01", "2010-01-02"]

    with pytest.raises(TypeError, match="must be datetime64"):
        run_data_contract_checks(df)


def test_contract_fails_when_custom_critical_column_is_missing():
    df = _valid_df()

    with pytest.raises(ValueError, match="Missing critical columns"):
        run_data_contract_checks(df, critical_columns=("InvoiceDate", "MissingField"))


def test_contract_passes_and_returns_summary():
    df = _valid_df()

    summary = run_data_contract_checks(df)

    assert summary["rows"] == 2
    assert summary["columns"] >= 11
    assert str(summary["date_min"]).startswith("2010-01-01")
    assert str(summary["date_max"]).startswith("2010-01-02")
