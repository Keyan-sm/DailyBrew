# llm-memory

**A structured, temporal, queryable memory layer for LLM agents — a drop-in
upgrade from "a pile of markdown files."**

A `CLAUDE.md`/`AGENTS.md` file is a fine start, but it can't tell you what's
*relevant right now*, it can't represent a fact *changing over time*, and it
grows until it poisons the context window. `llm-memory` keeps agent memory in
SQLite with semantic recall, recency/importance ranking, supersession history,
and time-travel queries — and exposes the whole thing as **tools the model can
call**.

```python
from llm_memory import MemoryStore
mem = MemoryStore("agent.db")

mem.remember("Prod DB is PostgreSQL 16 on RDS.", kind="fact", salience=0.9)
mem.recall("what database do we use")          # ranked, relevant memories

old = mem.remember("Deploy target is staging-east.", kind="fact")
mem.supersede(old, "Deploy target is prod-east.")   # fact changed → keep history
mem.recall("deploy target", as_of="2026-05-01")     # time-travel: what we knew then
```

## What it gives you over a markdown file

| | markdown file | llm-memory |
| --- | --- | --- |
| Retrieval | dump it all into context | ranked recall (similarity + recency + salience) |
| Changing facts | edit/overwrite, history lost | `supersede()` keeps an auditable chain |
| Time | none | `as_of` time-travel + recency decay |
| Forgetting | manual | `decay_and_prune()` |
| Agent control | harness-only | memory ops exposed as **callable tools** |
| Migration | — | `import_markdown()` / `export_markdown()` |

## Research grounding

Built from recent agent-memory work, taking what transfers to a dev harness:

- **Memory operations as actions.** Rather than the harness deciding when to
  read/write, the model calls `memory_remember` / `memory_recall` /
  `memory_supersede` itself — the direction in *Agentic Memory*
  ([arxiv 2601.01885](https://arxiv.org/abs/2601.01885)). See `tools.py`.
- **Persistent, temporally-chained state** instead of stateless RAG lookups, per
  *Continuum Memory Architectures*
  ([arxiv 2601.09913](https://arxiv.org/pdf/2601.09913)). See `supersede()` / `history()`.
- **Target the hard query types.** Recent benchmarks show the largest gains come
  on **temporal** (+~29.6) and **multi-hop** (+~23.1) queries — exactly what
  `as_of` recall and supersession chains address
  ([survey, arxiv 2603.07670](https://arxiv.org/html/2603.07670v1);
  [AMA-Bench, arxiv 2602.22769](https://arxiv.org/html/2602.22769v1)).
- **Keep a strong long-context baseline reachable.** AMA-Bench found naive
  long-context often beats fancy memory; `summarize()` + `export_markdown()` let
  you fall back to dumping a curated digest into context when that's better.

## Install & use

```bash
pip install -e .            # zero required dependencies (stdlib + sqlite)
pip install -e ".[dev]"     # + pytest

llm-memory --db agent.db remember "User prefers terse answers" --kind preference
llm-memory --db agent.db recall "how should I respond"
llm-memory --db agent.db import CLAUDE.md       # migrate an existing file
llm-memory --db agent.db summarize
```

Everything runs **offline**: the default `HashingEmbedder` is deterministic and
dependency-free. Swap in a real embedding model by implementing the one-method
`Embedder` protocol.

## Wiring memory into an agent

```python
from llm_memory import MemoryStore, TOOLS, dispatch
mem = MemoryStore("agent.db")
# Give TOOLS to your model as its tool/function schema, then on each tool call:
result = dispatch(mem, tool_call.name, tool_call.arguments)
```

## Module map

| Module | Responsibility |
| --- | --- |
| `store.py`       | SQLite schema + CRUD |
| `embedding.py`   | Pluggable embeddings (offline hashing default) |
| `memory.py`      | High-level ops: remember/recall/update/supersede/summarize/decay |
| `temporal.py`    | Recency decay + timestamp handling |
| `tools.py`       | Memory-as-tools schemas + `dispatch()` |
| `markdown_io.py` | Import/export markdown |

## Status

v0.1.0 — MVP. Tested (`pytest`), runs offline. Roadmap: real vector index
(sqlite-vss) behind the same API, LLM-backed `summarize()`, conflict detection
on `remember()`.

## License

MIT
