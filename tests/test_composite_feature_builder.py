import pandas as pd
import pytest

from src.features.composite_feature_builder import build_composite_features


def _sample_churn_features() -> pd.DataFrame:
    """Minimal churn features DataFrame mimicking build_churn_features output."""
    return pd.DataFrame(
        {
            "Customer ID": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008],
            "snapshot_date": pd.Timestamp("2020-04-15"),
            "recency_days": [5, 90, 150, 10, 30, 60, 120, 3],
            "frequency_90d": [8, 2, 0, 12, 5, 1, 0, 15],
            "monetary_90d": [1200.0, 200.0, 0.0, 2500.0, 600.0, 50.0, 0.0, 3000.0],
            "avg_order_value_90d": [150.0, 100.0, 0.0, 208.3, 120.0, 50.0, 0.0, 200.0],
            "return_rate_90d": [0.0, 0.1, 0.0, 0.05, 0.0, 0.5, 0.0, 0.02],
            "tenure_days": [365, 180, 400, 100, 200, 50, 10, 500],
            "recency_velocity": [0.014, 0.5, 0.375, 0.1, 0.15, 1.0, 0.0, 0.006],
            "churn_label": [0, 1, 1, 0, 0, 1, 1, 0],
        }
    )


def test_composite_builder_happy_path_returns_all_composite_columns():
    out = build_composite_features(_sample_churn_features())
    for col in [
        "purchase_intensity",
        "loyalty_score",
        "retention_score",
        "customer_value_score",
        "rfm_segment",
    ]:
        assert col in out.columns, f"Missing column: {col}"


def test_composite_builder_preserves_original_columns():
    original = _sample_churn_features()
    out = build_composite_features(original)
    for col in original.columns:
        assert col in out.columns


def test_composite_builder_purchase_intensity():
    out = build_composite_features(_sample_churn_features())
    row = out.loc[out["Customer ID"] == 1001].iloc[0]
    # frequency=8, tenure=365 -> 8/365 ≈ 0.0219
    assert row["purchase_intensity"] == pytest.approx(8.0 / 365.0, abs=1e-3)


def test_composite_builder_loyalty_score_range():
    out = build_composite_features(_sample_churn_features())
    assert (out["loyalty_score"] >= 0.0).all()
    assert (out["loyalty_score"] <= 1.0).all()


def test_composite_builder_retention_score_range():
    out = build_composite_features(_sample_churn_features())
    assert (out["retention_score"] >= 0.0).all()
    assert (out["retention_score"] <= 1.0).all()


def test_composite_builder_customer_value_score_range():
    out = build_composite_features(_sample_churn_features())
    assert (out["customer_value_score"] >= 0.0).all()
    assert (out["customer_value_score"] <= 1.0).all()


def test_composite_builder_rfm_segment_valid_labels():
    out = build_composite_features(_sample_churn_features())
    valid_segments = {
        "Champions",
        "Loyal",
        "Potential Loyalist",
        "At Risk",
        "Can't Lose Them",
        "Need Attention",
        "Lost",
        "Hibernating",
    }
    assert set(out["rfm_segment"]).issubset(valid_segments)


def test_composite_builder_raises_when_columns_missing():
    df = _sample_churn_features().drop(columns=["tenure_days"])
    with pytest.raises(ValueError, match="Missing required columns"):
        build_composite_features(df)


def test_composite_builder_retention_score_with_high_return_rate():
    out = build_composite_features(_sample_churn_features())
    # Customer 1006 has return_rate=0.5, recency_velocity=1.0 -> retention = 0.5 * 0.0 = 0.0
    row = out.loc[out["Customer ID"] == 1006].iloc[0]
    assert row["retention_score"] == pytest.approx(0.0, abs=1e-4)


def test_composite_builder_no_intermediate_quartile_columns():
    """r_quartile, f_quartile, m_quartile should be dropped after RFM segmentation."""
    out = build_composite_features(_sample_churn_features())
    assert "r_quartile" not in out.columns
    assert "f_quartile" not in out.columns
    assert "m_quartile" not in out.columns
