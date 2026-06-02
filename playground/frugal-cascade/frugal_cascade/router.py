"""The Router: turn a prompt into a model choice, optionally with a
confidence-based cascade (cheap-first, escalate on low confidence).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from .features import RequestFeatures, featurize
from .policy import ScoredModel, Weights, score_models
from .providers import MockProvider, Provider, Response
from .registry import Model, default_registry


@dataclass
class Decision:
    chosen: Model
    ranked: List[ScoredModel]
    features: RequestFeatures
    rationale: str


@dataclass
class RunResult:
    response: Response
    decision: Decision
    attempts: List[str]        # model names tried, in order
    total_cost: float
    escalated: bool


class Router:
    def __init__(self, models: Optional[Sequence[Model]] = None,
                 weights: Optional[Weights] = None):
        self.models = list(models or default_registry())
        self.weights = weights or Weights()

    def route(self, prompt: str, expected_output_tokens: int | None = None) -> Decision:
        feat = featurize(prompt, expected_output_tokens)
        ranked = score_models(self.models, feat, self.weights)
        if not ranked:
            raise ValueError("No model satisfies the request constraints "
                             "(e.g. context window too small).")
        return Decision(
            chosen=ranked[0].model, ranked=ranked, features=feat,
            rationale=f"{feat.rationale} -> picked {ranked[0].model.name} "
                      f"(score={ranked[0].score})",
        )

    def cascade_order(self, decision: Decision) -> List[Model]:
        """Cheap-first ordering of acceptable models for the cascade: sort the
        scored candidates by estimated cost ascending."""
        return [s.model for s in sorted(decision.ranked, key=lambda s: s.est_cost)]

    def run(self, prompt: str, provider: Provider | None = None,
            cascade: bool = True, confidence_threshold: float = 0.6) -> RunResult:
        """Execute the request. With cascade=True we try the cheapest acceptable
        model first and escalate to pricier ones until confidence clears the
        threshold — this is where most real-world savings come from."""
        decision = self.route(prompt)
        feat = decision.features
        provider = provider or MockProvider(difficulty=feat.difficulty,
                                            task_type=feat.task_type)

        order = self.cascade_order(decision) if cascade else [decision.chosen]
        attempts: List[str] = []
        total_cost = 0.0
        last: Response | None = None
        for model in order:
            resp = provider.complete(model, prompt, feat.est_tokens_out)
            attempts.append(model.name)
            total_cost += resp.cost
            last = resp
            if resp.confidence >= confidence_threshold:
                break
        assert last is not None
        return RunResult(
            response=last, decision=decision, attempts=attempts,
            total_cost=round(total_cost, 8), escalated=len(attempts) > 1,
        )
