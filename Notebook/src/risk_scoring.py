
from dataclasses import dataclass


@dataclass(frozen=True)
class CustomerProfile:
    customer_id: int
    frequency: int
    monetary: float
    recency_days: int


def compute_risk_score(profile: CustomerProfile) -> float:
    frequency_factor = max(0.0, 1.0 - min(profile.frequency, 12) / 12.0)
    recency_factor = min(profile.recency_days, 180) / 180.0
    monetary_factor = max(0.0, 1.0 - min(profile.monetary, 2000.0) / 2000.0)
    score = 0.4 * recency_factor + 0.4 * frequency_factor + 0.2 * monetary_factor
    return float(round(min(max(score, 0.0), 1.0), 4))


def validate_profile(profile: CustomerProfile) -> None:
    if profile.frequency < 0:
        raise ValueError("frequency must be >= 0")
    if profile.monetary < 0:
        raise ValueError("monetary must be >= 0")
    if profile.recency_days < 0:
        raise ValueError("recency_days must be >= 0")


def safe_compute_risk_score(profile: CustomerProfile) -> float:
    validate_profile(profile)
    return compute_risk_score(profile)
