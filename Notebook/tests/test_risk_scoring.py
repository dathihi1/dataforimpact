
import pytest
from src.risk_scoring import CustomerProfile, safe_compute_risk_score


def test_compute_risk_score_normal_case():
    profile = CustomerProfile(customer_id=1, frequency=6, monetary=500.0, recency_days=30)
    score = safe_compute_risk_score(profile)
    assert 0.0 <= score <= 1.0


def test_compute_risk_score_edge_case_zero_activity():
    profile = CustomerProfile(customer_id=2, frequency=0, monetary=0.0, recency_days=180)
    score = safe_compute_risk_score(profile)
    assert score >= 0.8


def test_validation_failure_negative_frequency():
    profile = CustomerProfile(customer_id=3, frequency=-1, monetary=10.0, recency_days=5)
    with pytest.raises(ValueError):
        safe_compute_risk_score(profile)
