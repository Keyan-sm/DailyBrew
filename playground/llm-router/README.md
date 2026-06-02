# llm-router

**A small, explainable, cost-aware router that picks the best-fit LLM for each
request — and cascades from cheap to capable only when it needs to.**

Frontier models are wonderful and expensive. Most requests in a real agent
workspace ("what's the capital of France?", "extract these dates as JSON") do
not need a frontier model. `llm-router` decides *per request* which model to
use, balancing **quality, cost, and latency**, with explicit pressure against
the failure mode where routers quietly default to the most expensive model.

```text
prompt ──► featurize (task type, difficulty, size)
       ──► score every model: w_q·quality − w_c·cost − w_l·latency − collapse_penalty
       ──► cascade: try cheapest acceptable model, escalate on low confidence
       ──► answer + full rationale + cost
```

On the built-in sample suite it routes for **~32% less cost** than always
calling the frontier model, while still escalating the genuinely hard prompts.

## Why this exists / research grounding

Designed by reading recent LLM-routing work and pulling the ideas that transfer
to an agent dev harness:

- **Anti-collapse.** *When Routing Collapses* documents routers drifting to the
  biggest model even when small ones suffice. We add an explicit cost penalty on
  easy requests so frontier models must clear a higher bar
  ([arxiv 2602.03478](https://arxiv.org/pdf/2602.03478)).
- **Cost-aware scoring.** Cost-aware contrastive routing reports up to **+25%**
  on the accuracy/cost tradeoff; our scoring makes that tradeoff explicit and
  tunable ([arxiv 2508.12491](https://arxiv.org/pdf/2508.12491)).
- **Cheap signals, not an LLM judge.** We featurize with fast heuristics rather
  than a model call on the hot path, in the spirit of prefill/lightweight-signal
  routing ([arxiv 2603.20895](https://arxiv.org/html/2603.20895v2)).
- **Cascading.** Unified routing-and-cascading shows confidence-based escalation
  beats single-shot selection ([arxiv 2410.10347](https://arxiv.org/pdf/2410.10347)).

## Install

```bash
pip install -e .            # core, zero required dependencies
pip install -e ".[dev]"     # + pytest, pyyaml for tests and YAML configs
```

## Use

```bash
# Which model would be chosen, and why (no API call):
llm-router route "Extract all dates and amounts from this invoice as JSON"

# Route + execute the cascade (uses the offline mock provider by default):
llm-router run "Refactor this function and fix the bug"

# Quantify savings vs an always-frontier baseline on the sample suite:
llm-router eval
```

```python
from llm_router import Router
router = Router()                       # or Router(load_registry("config/models.yaml"))
decision = router.route("Summarize this thread in two sentences")
print(decision.chosen.name, decision.rationale)

result = router.run("Prove step by step why Raft is safe")
print(result.attempts, result.total_cost)   # e.g. ['gpt-mini','sonnet','opus']
```

## Going live

The default `MockProvider` is deterministic and offline, so everything (tests,
eval, examples) runs with **zero API keys**. To route real traffic, install an
extra and pass the matching provider:

```bash
pip install -e ".[openai]"   # or ".[anthropic]"
export OPENAI_API_KEY=...
```

```python
from llm_router.providers import OpenAIProvider
router.run("…", provider=OpenAIProvider())
```

Model prices/qualities live in `config/models.yaml` — edit them or add your own
models (including OpenRouter-style entries) without touching code.

## How it works

| Module | Responsibility |
| --- | --- |
| `registry.py` | Model catalog: price, context, latency, per-task quality |
| `features.py` | Fast heuristic featurization (task type, difficulty, size) |
| `policy.py`   | Scoring with the anti-collapse penalty |
| `router.py`   | Selection + confidence-based cascade |
| `providers.py`| Mock / OpenAI / Anthropic behind one interface |
| `evaluate.py` | Cost-savings report vs frontier baseline |

## Status

v0.1.0 — MVP. Tested (`pytest`), runs offline. Roadmap: learned difficulty
estimator, latency-budget hard constraints, per-tenant budgets, OpenRouter
passthrough adapter.

## License

MIT
