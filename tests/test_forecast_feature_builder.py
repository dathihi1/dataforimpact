import pandas as pd
import pytest

from src.features.forecast_feature_builder import build_forecast_features


def _forecast_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Customer ID": [1001, 1001, 1001, 1002, 1002],
            "InvoiceDate": pd.to_datetime(
                [
                    "2020-01-05",
                    "2020-03-10",
                    "2020-04-12",
                    "2020-01-10",
                    "2020-02-10",
                ]
            ),
            "TotalValue": [100.0, 300.0, 400.0, 50.0, 70.0],
        }
    )


def test_forecast_builder_happy_path_returns_expected_columns():
    out = build_forecast_features(_forecast_df())
    expected = {
        "Customer ID",
        "ds",
        "revenue",
        "lag_1",
        "lag_3",
        "rolling_mean_3",
        "month_index",
        "month_number",
        "purchase_trend",
    }
    assert expected.issubset(set(out.columns))


def test_forecast_builder_sorts_by_customer_and_date():
    out = build_forecast_features(_forecast_df())
    sorted_out = out.sort_values(["Customer ID", "ds"]).reset_index(drop=True)
    pd.testing.assert_frame_equal(out.reset_index(drop=True), sorted_out)


def test_forecast_builder_reindexes_missing_months_and_builds_lags_without_future_leakage():
    out = build_forecast_features(_forecast_df())
    c1001 = out.loc[out["Customer ID"] == 1001].reset_index(drop=True)

    # Expected months for c1001: Jan, Feb (filled 0), Mar, Apr
    assert c1001["ds"].dt.strftime("%Y-%m").tolist() == ["2020-01", "2020-02", "2020-03", "2020-04"]
    assert c1001["revenue"].tolist() == [100.0, 0.0, 300.0, 400.0]

    # lag_1 at Apr must be Mar revenue, not future value
    assert c1001.loc[3, "lag_1"] == 300.0
    # lag_3 at Apr should be Jan revenue
    assert c1001.loc[3, "lag_3"] == 100.0


def test_forecast_builder_rolling_mean_3_uses_past_values_only():
    out = build_forecast_features(_forecast_df())
    c1001 = out.loc[out["Customer ID"] == 1001].reset_index(drop=True)

    # Apr rolling mean 3 should average Jan, Feb, Mar revenues = (100 + 0 + 300)/3
    assert c1001.loc[3, "rolling_mean_3"] == pytest.approx(133.3333, abs=1e-4)


def test_forecast_builder_month_index_and_month_number():
    out = build_forecast_features(_forecast_df())
    c1002 = out.loc[out["Customer ID"] == 1002].reset_index(drop=True)

    assert c1002["month_index"].tolist() == [0, 1]
    assert c1002["month_number"].tolist() == [1, 2]


def test_forecast_builder_raises_when_required_columns_missing():
    df = _forecast_df().drop(columns=["TotalValue"])

    with pytest.raises(ValueError, match="Missing required columns"):
        build_forecast_features(df)


def test_forecast_builder_raises_when_date_not_datetime():
    df = _forecast_df()
    df["InvoiceDate"] = df["InvoiceDate"].dt.strftime("%Y-%m-%d")

    with pytest.raises(TypeError, match="must be datetime64"):
        build_forecast_features(df)


def test_forecast_builder_supports_custom_column_names():
    df = _forecast_df().rename(
        columns={
            "Customer ID": "customer_id",
            "InvoiceDate": "event_time",
            "TotalValue": "amount",
        }
    )

    out = build_forecast_features(
        df,
        customer_col="customer_id",
        date_col="event_time",
        value_col="amount",
    )
    assert "customer_id" in out.columns
    assert len(out) > 0


def test_forecast_builder_returns_empty_dataframe_with_expected_columns_for_empty_input():
    df = pd.DataFrame(
        {
            "Customer ID": pd.Series(dtype="int64"),
            "InvoiceDate": pd.Series(dtype="datetime64[ns]"),
            "TotalValue": pd.Series(dtype="float64"),
        }
    )

    out = build_forecast_features(df)
    assert out.empty
    assert out.columns.tolist() == [
        "Customer ID",
        "ds",
        "revenue",
        "lag_1",
        "lag_3",
        "rolling_mean_3",
        "month_index",
        "month_number",
        "purchase_trend",
    ]


def test_forecast_builder_purchase_trend():
    out = build_forecast_features(_forecast_df())
    c1001 = out.loc[out["Customer ID"] == 1001].reset_index(drop=True)
    # revenue: 100, 0, 300, 400
    # pct_change: NaN, -1.0, inf, 0.333...
    import math
    assert math.isnan(c1001.loc[0, "purchase_trend"])
    assert c1001.loc[1, "purchase_trend"] == pytest.approx(-1.0, abs=1e-4)
