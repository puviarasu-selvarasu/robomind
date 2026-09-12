"""Pure confidence and weight math. No I/O, no state."""
from __future__ import annotations

import math
from datetime import datetime, timezone


def laplace_weight(hits: int, wins: int) -> float:
    """Rule weight via Laplace smoothing. Bounded (0, 1)."""
    return (wins + 1.0) / (hits + 2.0)


def decay_weight(weight: float, factor: float = 0.99, floor: float = 0.05) -> float:
    """Multiplicative decay for unused rules."""
    return max(floor, weight * factor)


def update_confidence(old: float, observed: float, alpha: float = 0.3) -> float:
    """Exponential moving average. observed in [0, 1]."""
    observed = max(0.0, min(1.0, observed))
    new = old + alpha * (observed - old)
    return max(0.0, min(1.0, new))


def decay_by_age(
    confidence: float,
    updated_at: str | datetime | None,
    *,
    halflife_days: float = 90.0,
    floor: float = 0.1,
) -> float:
    """Halflife decay based on age. Never drops below floor."""
    if confidence <= floor:
        return confidence
    if updated_at is None:
        return confidence
    if isinstance(updated_at, str):
        try:
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        except ValueError:
            return confidence
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    age_days = (datetime.now(timezone.utc) - updated_at).total_seconds() / 86400.0
    if age_days <= 0:
        return confidence
    decayed = confidence * math.pow(0.5, age_days / halflife_days)
    return max(floor, decayed)