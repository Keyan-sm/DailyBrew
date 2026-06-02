"""Scoring policy with explicit anti-collapse pressure.

Recent work ("When Routing Collapses") shows naive routers drift toward always
picking the most capable/expensive model even when a cheaper one suffices. We
counter that two ways:

1. A cost term that scales with the request's *actual* token footprint.
2. A difficulty gate: when a request is easy, we add extra penalty proportional
   to a model's price, so frontier models must clear a higher bar to win.

score(model) = w_q * quality_fit
             - w_c * normalized_cost
             - w_l * normalized_latency
             - collapse_penalty(easy request, expensive model)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .features import RequestFeatures
from .registry import Model


@dataclass
class Weights:
    quality: float = 1.0
    cost: float = 0.6
    latency: float = 0.15
    anti_collapse: float = 0.5
    easy_threshold: float = 0.35   # difficulty below this is "easy"


@dataclass
class ScoredModel:
    model: Model
    score: float
    quality_fit: float
    est_cost: float
    rationale: str


def _normalize(values: Sequence[float]) -> List[float]:
    lo, hi = min(values), max(values)
    if hi - lo < 1e-12:
        return [0.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def score_models(models: Sequence[Model], feat: RequestFeatures,
                 weights: Weights | None = None) -> List[ScoredModel]:
    w = weights or Weights()
    costs = [m.expected_cost(feat.est_tokens_in, feat.est_tokens_out) for m in models]
    latencies = [float(m.latency_tier) for m in models]
    norm_cost = _normalize(costs)
    norm_lat = _normalize(latencies)

    scored: List[ScoredModel] = []
    for m, c, nc, nl in zip(models, costs, norm_cost, norm_lat):
        if feat.needs_long_context and m.max_context < feat.est_tokens_in:
            continue  # hard constraint: cannot fit the context
        q = m.quality_for(feat.task_type)
        penalty = 0.0
        if feat.difficulty < w.easy_threshold:
            # On easy requests, penalize models proportionally to their price rank.
            penalty = w.anti_collapse * nc
        score = w.quality * q - w.cost * nc - w.latency * nl - penalty
        scored.append(ScoredModel(
            model=m, score=round(score, 4), quality_fit=q, est_cost=c,
            rationale=(f"q={q:.2f} costN={nc:.2f} latN={nl:.2f} "
                       f"collapsePenalty={penalty:.2f}"),
        ))
    scored.sort(key=lambda s: s.score, reverse=True)
    return scored
