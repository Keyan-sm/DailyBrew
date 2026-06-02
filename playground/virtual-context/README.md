# virtual-context

**Memory for LLM agents, kept in SQLite outside the context window and edited by
the model through tool calls — so the agent can remember more than fits in its
prompt, and recall the right thing on demand.** An implementation of MemGPT's
external-context idea (Packer et al., 2023) with the memory-stream retrieval
score from Generative Agents (Park et al., 2023).

A flat `CLAUDE.md`/`AGENTS.md` file either fits in context or it doesn't, and it
can't rank what's relevant right now. This keeps memory on "disk," pages the
relevant pieces back in, and ranks them by relevance, recency, and importance.

```text
>>> mem.recall("which database do we run in production")
[0.67] (fact)       Production database is PostgreSQL 16 on AWS RDS.
[0.33] (preference) The user prefers terse, no-emoji responses.
```

## Highlights
- **External context** (MemGPT) — memory lives in SQLite, not the prompt; you're not bounded by the context window.
- **Memory as tool calls** (MemGPT) — the model itself calls `remember` / `recall` / `supersede` / `forget` (`tools.py`).
- **Recency + importance + relevance ranking** (Generative Agents) — the retrieval score, implemented in `recall()`.
- **Runs offline** — deterministic hashing embedder, zero dependencies, zero API keys.
- **Migrates a markdown file in one call** — `import_markdown(CLAUDE.md)`.

## The papers it implements

**MemGPT** — *Towards LLMs as Operating Systems*, Packer, Wooders, Lin, Fang,
Patil & Gonzalez, UC Berkeley, 2023
([arXiv:2310.08560](https://arxiv.org/abs/2310.08560)). Borrows OS virtual
memory: a fixed **main context** (RAM, the prompt) and an unbounded **external
context** (disk). The LLM manages what's paged in by issuing **function calls**
to read and write its own memory.

**Generative Agents** — *Interactive Simulacra of Human Behavior*, Park et al.,
Stanford, 2023 ([arXiv:2304.03442](https://arxiv.org/abs/2304.03442)). Retrieves
from a memory stream with a composite score:
`α·relevance + α·recency + α·importance`, where relevance is embedding cosine
similarity, recency is exponential decay, and importance is a 1–10 score.

## What is faithful, and what is mine

| Component | Source | Fidelity |
| --- | --- | --- |
| External-context store, paged in on demand | MemGPT | **Faithful** to the idea |
| Memory operations exposed as model **tool calls** | MemGPT | **Faithful** (`tools.py` + `dispatch()`) |
| `recall()` = relevance + recency + importance | Generative Agents | **Faithful** to the formula |
| Autonomous paging loop (memory-pressure interrupts, queue manager) | MemGPT | **Not implemented.** Memory ops are model-driven, not self-triggered. |
| `importance` (salience) | Generative Agents | **Set explicitly**, not LLM-scored 1–10 (roadmap). |
| `supersede()` / `as_of` time-travel | — | **Mine.** Tracks facts that change over time; not from either paper. |
| Markdown import/export | — | **Mine.** Migration convenience. |

## Install
```bash
pip install -e .            # stdlib + sqlite, zero required dependencies
pip install -e ".[dev]"     # + pytest
```

## Use
```bash
virtual-context --db agent.db remember "User prefers terse answers" --kind preference
virtual-context --db agent.db recall   "how should I respond"
virtual-context --db agent.db import    CLAUDE.md      # migrate an existing file
virtual-context --db agent.db summarize
```
```python
from virtual_context import MemoryStore
mem = MemoryStore("agent.db")
mem.remember("Production database is PostgreSQL 16 on AWS RDS.", kind="fact", salience=0.9)
mem.recall("which database do we run in production")
```

### Wiring it into an agent (the MemGPT part)
```python
from virtual_context import MemoryStore, TOOLS, dispatch
mem = MemoryStore("agent.db")
# Give TOOLS to the model as its tool/function schema. On each tool call:
result = dispatch(mem, tool_call.name, tool_call.arguments)
```

### Facts that change (my extension)
```python
old = mem.remember("API base URL is api.v1.example.com", kind="fact")
mem.supersede(old, "API base URL is api.v2.example.com")   # keeps history
mem.recall("api base url", as_of="2026-05-01")             # what we knew then
```

## Module map
| Module | Responsibility |
| --- | --- |
| `store.py`       | SQLite external context + CRUD |
| `memory.py`      | remember / recall / supersede / summarize / decay |
| `embedding.py`   | Pluggable embeddings (offline hashing default) |
| `temporal.py`    | Recency decay + timestamps |
| `tools.py`       | MemGPT-style memory-as-tools + `dispatch()` |
| `markdown_io.py` | Import/export markdown |

## Status
v0.1.0 — MVP, `pytest`-tested, runs offline. Roadmap: real vector index behind
the same API, LLM-scored importance and an LLM-backed `summarize()`, and an
optional MemGPT-style autonomous paging loop.

## License
MIT
