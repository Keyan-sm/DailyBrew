"""Routing evaluation: quantify savings vs an 'always use the frontier model'
baseline, the comparison every routing paper reports.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .providers import MockProvider
from .registry import Model
from .router import Router


@dataclass
class EvalReport:
    n: int
    routed_cost: float
    baseline_cost: float
    savings_pct: float
    escalations: int
    per_prompt: List[dict]


def most_expensive(models: Sequence[Model]) -> Model:
    return max(models, key=lambda m: m.output_cost)


def evaluate(prompts: Sequence[str], router: Router | None = None) -> EvalReport:
    router = router or Router()
    baseline_model = most_expensive(router.models)

    routed_cost = 0.0
    baseline_cost = 0.0
    escalations = 0
    rows: List[dict] = []
    for p in prompts:
        result = router.run(p)
        routed_cost += result.total_cost
        # Baseline: send everything to the frontier model, single shot.
        feat = result.decision.features
        baseline_cost += baseline_model.expected_cost(feat.est_tokens_in, feat.est_tokens_out)
        escalations += int(result.escalated)
        rows.append({
            "prompt": p[:50],
            "task": feat.task_type,
            "difficulty": feat.difficulty,
            "chose": result.decision.chosen.name,
            "attempts": result.attempts,
            "cost": round(result.total_cost, 6),
        })

    savings = 0.0 if baseline_cost == 0 else 100 * (baseline_cost - routed_cost) / baseline_cost
    return EvalReport(
        n=len(prompts), routed_cost=round(routed_cost, 6),
        baseline_cost=round(baseline_cost, 6), savings_pct=round(savings, 1),
        escalations=escalations, per_prompt=rows,
    )


SAMPLE_PROMPTS = [
    "What's the capital of France?",
    "Summarize this email thread in two sentences: ...",
    "Extract all dates and amounts from this invoice and return JSON.",
    "Translate 'good morning' to Japanese.",
    "Refactor this function and fix the off-by-one bug:\n```python\ndef f(x):\n  return x[len(x)]\n```",
    "Design a fault-tolerant, step-by-step architecture for a multi-region "
    "write-heavy database and justify every trade-off in depth. " * 6,
]
