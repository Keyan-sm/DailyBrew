# Research notes — what shaped these two projects

Quick survey of recent LLM-routing and agent-memory work (drawn from arXiv /
Hugging Face papers, ~mid-2026), pulling the techniques that transfer into an
agent-based dev workspace/harness. These are the "biggest claimed gains" ideas
that the two MVPs deliberately implement.

## Routing → `llm-router`
| Idea | Source | What we took |
| --- | --- | --- |
| Routing *collapse*: routers default to the priciest model even when a cheap one suffices | [When Routing Collapses, 2602.03478](https://arxiv.org/pdf/2602.03478) | Explicit **anti-collapse penalty** on easy requests (`policy.py`) |
| Cost-aware contrastive routing, **+25%** on accuracy/cost tradeoff | [2508.12491](https://arxiv.org/pdf/2508.12491) | Cost made an explicit, tunable term in scoring |
| Lightweight/prefill signals instead of an LLM judge on the hot path | [Prefill Activations, 2603.20895](https://arxiv.org/html/2603.20895v2) | Heuristic featurization (`features.py`) — no model call to route |
| Unified routing **and cascading** beats single-shot selection | [2410.10347](https://arxiv.org/pdf/2410.10347) | Confidence-based **cascade** (cheap→capable) in `router.py` |
| Cross-attention cost-aware selection, +6.6% AIQ | [2509.09782](https://arxiv.org/pdf/2509.09782) | Per-task quality profiles in the registry |

Result on the built-in sample suite: **~32% cheaper** than always calling the
frontier model, while still escalating the genuinely hard prompts.

## Memory → `llm-memory`
| Idea | Source | What we took |
| --- | --- | --- |
| Memory **operations as agent actions** (store/recall/update/discard) | [Agentic Memory, 2601.01885](https://arxiv.org/abs/2601.01885) | `tools.py`: memory exposed as callable tools + `dispatch()` |
| Persistent, **temporally-chained** state vs stateless RAG | [Continuum Memory, 2601.09913](https://arxiv.org/pdf/2601.09913) | `supersede()` / `history()` chains, recency decay |
| Biggest gains are on **temporal (+~29.6)** and **multi-hop (+~23.1)** queries | [Survey 2603.07670](https://arxiv.org/html/2603.07670v1) | `as_of` time-travel recall; supersession multi-hop |
| Long-context baseline is often *stronger* than fancy memory | [AMA-Bench 2602.22769](https://arxiv.org/html/2602.22769v1) | `summarize()` + `export_markdown()` to dump a curated digest |

## Harness framing (why "drop into any agent workspace")
- [Code as Agent Harness, 2605.18747](https://arxiv.org/abs/2605.18747) and
  [Runtime Harness Adaptation, 2605.22166](https://arxiv.org/abs/2605.22166)
  frame planning + **memory** + tool use as the harness layer you improve
  *without* retraining the model. Both projects are designed to slot in there:
  the router as the model-selection layer, the memory store as the persistence
  layer, each usable by any frozen model via a tiny interface.
