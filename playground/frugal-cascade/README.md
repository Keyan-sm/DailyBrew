# frugal-cascade

**An LLM cascade: send each request to a cheap model first, score the answer,
and escalate to a stronger model only when the score is low.** A dependency-free
implementation of the cascade strategy from FrugalGPT (Chen, Zaharia & Zou,
2023), plus a single-shot router in the style of RouteLLM (Ong et al., 2024).

The point is to stop paying frontier prices for requests a small model already
handles. Cascading means you only spend the expensive call when the cheap answer
isn't good enough.

```text
$ frugal-cascade eval
n=6  routed=$0.0337  baseline(always-frontier)=$0.0496  savings=32.0%  escalations=2/6
```
*(Synthetic suite, mock provider — see "Numbers, honestly" below.)*

## Highlights
- **FrugalGPT cascade** — cheap→expensive, a scorer accepts or escalates each answer (`router.py`).
- **RouteLLM-style single-shot routing** — pick one model up front by predicted need (`policy.py`).
- **Runs offline.** A deterministic mock provider means tests, eval, and examples need **no API keys**.
- **Explainable.** Every decision returns its score breakdown; no opaque model picks the model.
- Adapters for OpenAI and Anthropic; models/prices live in editable `config/models.yaml`.

## The papers it implements

**FrugalGPT** — *How to Use Large Language Models While Reducing Cost and
Improving Performance*, Chen, Zaharia & Zou, Stanford, 2023
([arXiv:2305.05176](https://arxiv.org/abs/2305.05176)). Proposes the **LLM
cascade**: route a query through a sequence of LLMs from cheap to expensive,
using a learned scoring function to decide whether to accept an answer or
escalate. Reported result: **up to 98% cost reduction** while matching GPT-4, or
+4% accuracy at equal cost.

**RouteLLM** — *Learning to Route LLMs with Preference Data*, Ong et al.,
UC Berkeley / LMSYS, 2024 ([arXiv:2406.18665](https://arxiv.org/abs/2406.18665)).
Trains a **single-shot router** (matrix factorization / BERT / causal-LLM
classifiers) on Chatbot Arena preference data to predict whether a query needs
the strong model. Reported result: **95% of GPT-4 quality using ~26% of GPT-4
calls** (≈48% cost reduction; up to 85% cheaper on MT-Bench).

## What is faithful, and what is mine

To be precise about provenance:

| Component | Source | Fidelity |
| --- | --- | --- |
| Cheap→expensive cascade with accept/escalate | FrugalGPT | **Faithful** to the strategy |
| Single-shot model selection by predicted difficulty | RouteLLM | **Strategy only** |
| **Accept/escalate scorer** | — | **Mine.** FrugalGPT trains a DistilBERT scorer; here it's a confidence heuristic. |
| **Router** | — | **Mine.** RouteLLM trains on preference data; here it's a transparent rule-based score. |
| Anti-collapse cost penalty on easy requests | — | **Mine.** Not from either paper. |

So: faithful to the *mechanisms*, but the learned components are replaced with
transparent heuristics. Training a real scorer/router on preference data is the
roadmap, not a current claim.

## Install
```bash
pip install -e .            # core, zero required dependencies
pip install -e ".[dev]"     # + pytest, pyyaml for tests and YAML configs
```

## Use
```bash
frugal-cascade route "Extract all dates from this invoice as JSON"   # show the choice + why
frugal-cascade run   "Refactor this function and fix the bug"        # cascade + execute (mock)
frugal-cascade eval                                                  # savings vs always-frontier
```
```python
from frugal_cascade import Router
router = Router()
result = router.run("Prove step by step why Raft is safe")
print(result.attempts, result.total_cost)   # e.g. ['gpt-mini', 'sonnet', 'opus']
```

Going live: `pip install -e ".[openai]"`, set `OPENAI_API_KEY`, and pass
`OpenAIProvider()` to `run()`. Prices/qualities are in `config/models.yaml`.

## Numbers, honestly
- The **98% / 48%** figures above are the *papers'* results on real benchmarks. They are not my measurements.
- The **32%** from `frugal-cascade eval` is on a **6-prompt synthetic suite with a deterministic mock provider** — an illustration that the cascade routes and escalates correctly, **not** a benchmark result. Reproducing FrugalGPT/RouteLLM numbers on a real dataset (with a trained scorer) is future work.

## Module map
| Module | Responsibility |
| --- | --- |
| `registry.py` | Model catalog: price, context, latency, per-task quality |
| `features.py` | Heuristic featurization (task type, difficulty, size) |
| `policy.py`   | RouteLLM-style scoring + anti-collapse penalty |
| `router.py`   | FrugalGPT-style cascade |
| `providers.py`| Mock / OpenAI / Anthropic behind one interface |
| `evaluate.py` | Cost-savings report vs frontier baseline |

## Status
v0.1.0 — MVP, `pytest`-tested, runs offline. Roadmap: trained scorer/router on
preference data (to actually reproduce the paper numbers), latency-budget
constraints, OpenRouter passthrough.

## License
MIT
