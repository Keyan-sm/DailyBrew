"""Temporal helpers.

Recent agent-memory benchmarks report the biggest gains on *temporal* queries
(+~29.6 pts) and *multi-hop* reasoning (+~23.1 pts) over older approaches — i.e.
handling facts that accumulate, change, and supersede one another over time.
These helpers give the store first-class recency weighting and time-travel.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone


def now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


def to_ts(value) -> float:
    """Accept a unix ts (int/float) or an ISO-8601 string."""
    if value is None:
        return now_ts()
    if isinstance(value, (int, float)):
        return float(value)
    return datetime.fromisoformat(str(value)).timestamp()


def recency_weight(created_at: float, now: float | None = None,
                   half_life_days: float = 30.0) -> float:
    """Exponential decay in [0, 1]: 1.0 when fresh, 0.5 at one half-life."""
    now = now if now is not None else now_ts()
    age_days = max(0.0, (now - created_at) / 86_400)
    return math.pow(0.5, age_days / half_life_days)
