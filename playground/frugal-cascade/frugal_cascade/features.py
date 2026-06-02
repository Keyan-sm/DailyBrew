"""Cheap, explainable request featurization.

We deliberately avoid an LLM "judge" call on the hot path: classifying the
request with a model would add the very cost/latency the router exists to save.
Instead we use fast heuristics (keywords + length + structure) to estimate the
task type and difficulty. This mirrors the "prefill / lightweight signal"
direction in recent routing papers, kept dependency-free for an MVP.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

CODE_HINTS = re.compile(
    r"```|def |class |import |function |const |async |SELECT |traceback|stack trace|"
    r"\bbug\b|refactor|compile|unit test|regex|\bAPI\b", re.IGNORECASE)
REASONING_HINTS = re.compile(
    r"prove|derive|step[- ]by[- ]step|why |reason|trade[- ]?off|analyze|strategy|"
    r"plan |design a|architect", re.IGNORECASE)
EXTRACTION_HINTS = re.compile(
    r"extract|parse|classify|label|return json|list all|find all|categorize", re.IGNORECASE)
SUMMARY_HINTS = re.compile(r"summar|tl;dr|recap|condense|key points|digest", re.IGNORECASE)
TRANSLATE_HINTS = re.compile(r"translate|in (french|spanish|german|japanese|chinese)", re.IGNORECASE)


@dataclass
class RequestFeatures:
    task_type: str
    difficulty: float          # 0 (trivial) .. 1 (hard)
    est_tokens_in: int
    est_tokens_out: int
    needs_long_context: bool
    rationale: str


def _estimate_tokens(text: str) -> int:
    # ~4 chars/token is a good rough proxy across modern tokenizers.
    return max(1, len(text) // 4)


def featurize(prompt: str, expected_output_tokens: int | None = None) -> RequestFeatures:
    tokens_in = _estimate_tokens(prompt)

    if CODE_HINTS.search(prompt):
        task = "code"
    elif TRANSLATE_HINTS.search(prompt):
        task = "translation"
    elif EXTRACTION_HINTS.search(prompt):
        task = "extraction"
    elif SUMMARY_HINTS.search(prompt):
        task = "summarization"
    elif REASONING_HINTS.search(prompt):
        task = "reasoning"
    else:
        task = "chat"

    # Difficulty: blend of length and the presence of reasoning/code signals.
    length_component = min(1.0, tokens_in / 1500)
    signal_component = 0.0
    if task in ("reasoning", "code"):
        signal_component += 0.45
    if REASONING_HINTS.search(prompt):
        signal_component += 0.2
    if "?" in prompt and len(prompt) > 400:
        signal_component += 0.1
    difficulty = round(min(1.0, 0.5 * length_component + signal_component), 3)

    out = expected_output_tokens if expected_output_tokens is not None else \
        int(min(2000, max(64, tokens_in * (1.5 if task in ("code", "reasoning") else 0.5))))

    return RequestFeatures(
        task_type=task,
        difficulty=difficulty,
        est_tokens_in=tokens_in,
        est_tokens_out=out,
        needs_long_context=tokens_in > 30_000,
        rationale=f"task={task} via heuristics; len~{tokens_in}tok; difficulty={difficulty}",
    )
