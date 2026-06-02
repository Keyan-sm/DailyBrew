"""Model registry: the catalog of models the router can choose from.

Each model carries the metadata the routing policy needs: price, latency tier,
context window, and a per-task-type quality profile (0-1). Costs are USD per
1M tokens, matching how providers publish pricing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

TASK_TYPES = ("code", "reasoning", "extraction", "summarization", "chat", "translation")


@dataclass(frozen=True)
class Model:
    name: str
    provider: str
    input_cost: float          # USD / 1M input tokens
    output_cost: float         # USD / 1M output tokens
    max_context: int
    latency_tier: int          # 1 = fast, 3 = slow
    quality: Dict[str, float] = field(default_factory=dict)  # task_type -> 0..1
    general_quality: float = 0.5
    tags: tuple = ()

    def quality_for(self, task_type: str) -> float:
        """Quality on a task, falling back to the model's general quality."""
        return self.quality.get(task_type, self.general_quality)

    def expected_cost(self, tokens_in: int, tokens_out: int) -> float:
        return (tokens_in * self.input_cost + tokens_out * self.output_cost) / 1_000_000


def default_registry() -> List[Model]:
    """A small, representative registry spanning the cost/quality spectrum.

    Numbers are illustrative defaults; override them with config/models.yaml.
    """
    return [
        Model("haiku", "anthropic", 0.80, 4.0, 200_000, 1,
              {"chat": 0.78, "extraction": 0.82, "summarization": 0.80, "code": 0.70,
               "reasoning": 0.62, "translation": 0.80}, 0.74, ("cheap", "fast")),
        Model("gpt-mini", "openai", 0.60, 2.4, 128_000, 1,
              {"chat": 0.76, "extraction": 0.80, "summarization": 0.78, "code": 0.72,
               "reasoning": 0.64, "translation": 0.78}, 0.73, ("cheap", "fast")),
        Model("sonnet", "anthropic", 3.0, 15.0, 200_000, 2,
              {"chat": 0.88, "extraction": 0.90, "summarization": 0.89, "code": 0.91,
               "reasoning": 0.86, "translation": 0.87}, 0.88, ("balanced",)),
        Model("opus", "anthropic", 15.0, 75.0, 200_000, 3,
              {"chat": 0.92, "extraction": 0.93, "summarization": 0.93, "code": 0.96,
               "reasoning": 0.95, "translation": 0.90}, 0.94, ("frontier",)),
    ]


def load_registry(path: str | Path) -> List[Model]:
    """Load a registry from a YAML file (falls back to default_registry()).

    PyYAML is optional; if it is missing we surface a clear error so the user
    can `pip install pyyaml` or just rely on the built-in default registry.
    """
    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover - exercised only without pyyaml
        raise RuntimeError("pyyaml is required to load a YAML registry: pip install pyyaml") from exc

    data = yaml.safe_load(Path(path).read_text())
    models = []
    for m in data["models"]:
        models.append(Model(
            name=m["name"], provider=m["provider"],
            input_cost=float(m["input_cost"]), output_cost=float(m["output_cost"]),
            max_context=int(m.get("max_context", 128_000)),
            latency_tier=int(m.get("latency_tier", 2)),
            quality=m.get("quality", {}),
            general_quality=float(m.get("general_quality", 0.5)),
            tags=tuple(m.get("tags", [])),
        ))
    return models
