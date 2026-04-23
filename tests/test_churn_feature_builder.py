import pandas as pd
import pytest

from src.features.churn_feature_builder import build_churn_features


def _base_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Customer ID": [1001, 1001, 1001, 1002, 1002, 1001],
            "Invoice": ["A1", "A2", "A3", "B1", "B2", "A4"],
            "InvoiceDate": pd.to_datetime(
                [
                    "2020-01-10",
                    "2020-03-15",
                    "2020-04-10",
                    "2020-02-01",
                    "2020-03-20",
                    "2020-05-10",  # post-snapshot event for leakage checks
                ]
            ),
            "Quantity": [1, 1, -1, 1, 1, 1],
            "TotalValue": [100.0, 200.0, -50.0, 80.0, 120.0, 500.0],
            "IsReturn": [False, False, True, False, False, False],
        }
    )


def test_churn_builder_happy_path_returns_expected_columns_and_sorted_rows():
    out = build_churn_features(_base_df(), snapshot_date=pd.Timestamp("2020-04-15"), inactivity_days=30)

    expected_columns = {
        "Customer ID",
        "snapshot_date",
        "recency_days",
        "frequency_90d",
        "monetary_90d",
        "avg_order_value_90d",
        "return_rate_90d",
        "tenure_days",
        "churn_label",
    }
    assert expected_columns.issubset(set(out.columns))
    assert out["Customer ID"].tolist() == sorted(out["Customer ID"].tolist())


def test_churn_builder_prevents_leakage_by_ignoring_post_snapshot_in_features():
    out = build_churn_features(_base_df(), snapshot_date=pd.Timestamp("2020-04-15"), inactivity_days=30)
    c1001 = out.loc[out["Customer ID"] == 1001].iloc[0]

    # Only events in 90-day window up to snapshot: 2020-03-15 and 2020-04-10
    assert c1001["frequency_90d"] == 2
    assert c1001["monetary_90d"] == 150.0


def test_churn_label_uses_future_window_after_snapshot_only():
    out = build_churn_features(_base_df(), snapshot_date=pd.Timestamp("2020-04-15"), inactivity_days=30)

    c1001 = out.loc[out["Customer ID"] == 1001].iloc[0]
    c1002 = out.loc[out["Customer ID"] == 1002].iloc[0]

    # customer 1001 has activity on 2020-05-10 in future window => not churn
    assert c1001["churn_label"] == 0
    # customer 1002 has no future activity after snapshot => churn
    assert c1002["churn_label"] == 1


def test_churn_builder_handles_zero_orders_window_without_divide_errors():
    df = pd.DataFrame(
        {
            "Customer ID": [2001],
            "Invoice": ["C1"],
            "InvoiceDate": pd.to_datetime(["2019-01-01"]),
            "Quantity": [1],
            "TotalValue": [100.0],
            "IsReturn": [False],
        }
    )
    out = build_churn_features(df, snapshot_date=pd.Timestamp("2020-04-15"), inactivity_days=30)
    row = out.iloc[0]

    assert row["frequency_90d"] == 0
    assert row["avg_order_value_90d"] == 0.0
    assert row["return_rate_90d"] == 0.0


def test_churn_builder_raises_when_required_columns_missing():
    df = _base_df().drop(columns=["Invoice"])

    with pytest.raises(ValueError, match="Missing required columns"):
        build_churn_features(df, snapshot_date=pd.Timestamp("2020-04-15"), inactivity_days=30)


def test_churn_builder_raises_when_date_not_datetime():
    df = _base_df()
    df["InvoiceDate"] = df["InvoiceDate"].dt.strftime("%Y-%m-%d")

    with pytest.raises(TypeError, match="must be datetime64"):
        build_churn_features(df, snapshot_date=pd.Timestamp("2020-04-15"), inactivity_days=30)


def test_churn_builder_supports_custom_column_names():
    df = _base_df().rename(
        columns={
            "Customer ID": "customer_id",
            "Invoice": "invoice_id",
            "InvoiceDate": "event_time",
            "Quantity": "qty",
            "TotalValue": "amount",
            "IsReturn": "is_return",
        }
    )

    out = build_churn_features(
        df,
        snapshot_date=pd.Timestamp("2020-04-15"),
        inactivity_days=30,
        customer_col="customer_id",
        invoice_col="invoice_id",
        date_col="event_time",
        quantity_col="qty",
        value_col="amount",
        return_col="is_return",
    )

    assert "customer_id" in out.columns
    assert len(out) == 2


def test_churn_builder_raises_for_unsupported_return_values():
    df = _base_df()
    df["IsReturn"] = df["IsReturn"].astype("object")
    df.loc[0, "IsReturn"] = "not-bool"

    with pytest.raises(ValueError, match="unsupported boolean value"):
        build_churn_features(df, snapshot_date=pd.Timestamp("2020-04-15"), inactivity_days=30)


def test_churn_builder_n_unique_days():
    out = build_churn_features(_base_df(), snapshot_date=pd.Timestamp("2020-04-15"), inactivity_days=30)
    c1001 = out.loc[out["Customer ID"] == 1001].iloc[0]
    # c1001 has events on 2020-01-10, 2020-03-15, 2020-04-10 (before snapshot) = 3 unique days
    assert c1001["n_unique_days"] == 3


def test_churn_builder_avg_days_between_orders():
    out = build_churn_features(_base_df(), snapshot_date=pd.Timestamp("2020-04-15"), inactivity_days=30)
    c1001 = out.loc[out["Customer ID"] == 1001].iloc[0]
    # c1001 dates: Jan 10, Mar 15, Apr 10 -> gaps: 65 days, 26 days -> mean = 45.5
    assert c1001["avg_days_between_orders"] == pytest.approx(45.5, abs=1.0)


def test_churn_builder_avg_days_between_orders_single_order():
    df = pd.DataFrame({
        "Customer ID": [3001],
        "Invoice": ["X1"],
        "InvoiceDate": pd.to_datetime(["2020-02-01"]),
        "Quantity": [1],
        "TotalValue": [50.0],
        "IsReturn": [False],
    })
    out = build_churn_features(df, snapshot_date=pd.Timestamp("2020-04-15"), inactivity_days=30)
    assert out.iloc[0]["avg_days_between_orders"] == 0.0


def test_churn_builder_day_of_week_mode():
    out = build_churn_features(_base_df(), snapshot_date=pd.Timestamp("2020-04-15"), inactivity_days=30)
    c1001 = out.loc[out["Customer ID"] == 1001].iloc[0]
    # Jan 10 2020 = Friday (4), Mar 15 = Sunday (6), Apr 10 = Friday (4) -> mode = 4
    assert c1001["day_of_week_mode"] == 4


def test_churn_builder_recency_velocity():
    out = build_churn_features(_base_df(), snapshot_date=pd.Timestamp("2020-04-15"), inactivity_days=30)
    c1001 = out.loc[out["Customer ID"] == 1001].iloc[0]
    # recency = 5 days, tenure = 96 days -> velocity = 5/96 ≈ 0.052
    assert 0.0 <= c1001["recency_velocity"] <= 1.0
    assert c1001["recency_velocity"] == pytest.approx(5.0 / 96.0, abs=1e-3)


def test_churn_builder_recency_velocity_zero_tenure():
    """Customer with only one purchase on snapshot date -> tenure=0 -> velocity=0."""
    df = pd.DataFrame({
        "Customer ID": [4001],
        "Invoice": ["Y1"],
        "InvoiceDate": pd.to_datetime(["2020-04-15"]),
        "Quantity": [1],
        "TotalValue": [100.0],
        "IsReturn": [False],
    })
    out = build_churn_features(df, snapshot_date=pd.Timestamp("2020-04-15"), inactivity_days=30)
    assert out.iloc[0]["recency_velocity"] == 0.0
