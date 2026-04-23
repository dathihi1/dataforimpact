
import pytest
from src.risk_scoring import CustomerProfile, safe_compute_risk_score


def test_compute_risk_score_normal_case():
    profile = CustomerProfile(customer_id=1, frequency=6, monetary=500.0, recency_days=30)
    score = safe_compute_risk_score(profile)
    assert score == pytest.approx(0.4167, abs=1e-4)


def test_compute_risk_score_edge_case_zero_activity():
    profile = CustomerProfile(customer_id=2, frequency=0, monetary=0.0, recency_days=180)
    score = safe_compute_risk_score(profile)
    assert score == pytest.approx(1.0, abs=1e-4)


def test_compute_risk_score_is_clamped_to_zero_for_best_profile():
    profile = CustomerProfile(customer_id=6, frequency=20, monetary=5000.0, recency_days=0)
    score = safe_compute_risk_score(profile)
    assert score == pytest.approx(0.0, abs=1e-4)


def test_validation_failure_negative_frequency():
    profile = CustomerProfile(customer_id=3, frequency=-1, monetary=10.0, recency_days=5)
    with pytest.raises(ValueError):
        safe_compute_risk_score(profile)


def test_validation_failure_negative_monetary():
    profile = CustomerProfile(customer_id=4, frequency=2, monetary=-1.0, recency_days=5)
    with pytest.raises(ValueError):
        safe_compute_risk_score(profile)


def test_validation_failure_negative_recency_days():
    profile = CustomerProfile(customer_id=5, frequency=2, monetary=10.0, recency_days=-1)
    with pytest.raises(ValueError):
        safe_compute_risk_score(profile)
