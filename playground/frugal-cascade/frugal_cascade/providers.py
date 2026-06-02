"""Provider adapters behind one tiny interface.

The router never talks to a vendor SDK directly; it talks to a Provider. The
default MockProvider is fully deterministic and offline, so the whole project
(and its tests/eval) runs with zero API keys. Real OpenAI/Anthropic adapters
are imported lazily and used only if you set the keys and pass live=True.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Protocol

from .registry import Model


@dataclass
class Response:
    text: str
    confidence: float          # 0..1 self-reported / estimated
    tokens_in: int
    tokens_out: int
    cost: float
    model: str


class Provider(Protocol):
    def complete(self, model: Model, prompt: str, tokens_out: int) -> Response: ...


class MockProvider:
    """Deterministic stand-in. Confidence correlates with the model's quality
    for the prompt, so the cascade logic is testable without network calls."""

    def __init__(self, difficulty: float = 0.5, task_type: str = "chat"):
        self.difficulty = difficulty
        self.task_type = task_type

    def complete(self, model: Model, prompt: str, tokens_out: int) -> Response:
        tokens_in = max(1, len(prompt) // 4)
        q = model.quality_for(self.task_type)
        # A capable model on an easy task is confident; a weak model on a hard
        # task is not. Deterministic, bounded to [0,1].
        confidence = max(0.0, min(1.0, q - 0.6 * self.difficulty + 0.1))
        digest = hashlib.sha1(f"{model.name}:{prompt}".encode()).hexdigest()[:8]
        return Response(
            text=f"[{model.name} mock answer {digest}]",
            confidence=round(confidence, 3),
            tokens_in=tokens_in, tokens_out=tokens_out,
            cost=model.expected_cost(tokens_in, tokens_out),
            model=model.name,
        )


class OpenAIProvider:  # pragma: no cover - requires network + key
    def __init__(self):
        from openai import OpenAI  # lazy import
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def complete(self, model: Model, prompt: str, tokens_out: int) -> Response:
        resp = self.client.chat.completions.create(
            model=model.name, messages=[{"role": "user", "content": prompt}],
            max_tokens=tokens_out)
        usage = resp.usage
        return Response(
            text=resp.choices[0].message.content or "",
            confidence=0.85,  # vendors don't expose calibrated confidence; use a prior
            tokens_in=usage.prompt_tokens, tokens_out=usage.completion_tokens,
            cost=model.expected_cost(usage.prompt_tokens, usage.completion_tokens),
            model=model.name,
        )


class AnthropicProvider:  # pragma: no cover - requires network + key
    def __init__(self):
        import anthropic  # lazy import
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def complete(self, model: Model, prompt: str, tokens_out: int) -> Response:
        msg = self.client.messages.create(
            model=model.name, max_tokens=tokens_out,
            messages=[{"role": "user", "content": prompt}])
        usage = msg.usage
        return Response(
            text="".join(b.text for b in msg.content if hasattr(b, "text")),
            confidence=0.85,
            tokens_in=usage.input_tokens, tokens_out=usage.output_tokens,
            cost=model.expected_cost(usage.input_tokens, usage.output_tokens),
            model=model.name,
        )
