"""MemoryStore: the high-level API an agent (or harness) actually uses.

Beyond a flat markdown file, this gives you the memory *operations* recent
agent-memory work (e.g. AgeMem) exposes as first-class actions — remember,
recall, update, supersede, summarize, forget — plus temporal recall and
supersession chains so changing facts are handled correctly rather than
silently duplicated.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .embedding import Embedder, HashingEmbedder, cosine
from .store import Memory, Store
from .temporal import now_ts, recency_weight, to_ts


@dataclass
class Hit:
    memory: Memory
    score: float
    similarity: float
    recency: float


class MemoryStore:
    def __init__(self, path: str = ":memory:", embedder: Optional[Embedder] = None,
                 half_life_days: float = 30.0):
        self.store = Store(path)
        self.embedder = embedder or HashingEmbedder()
        self.half_life_days = half_life_days

    # --- write operations -------------------------------------------------
    def remember(self, content: str, kind: str = "note", tags: Optional[List[str]] = None,
                 salience: float = 0.5, source: Optional[str] = None) -> int:
        mem = Memory(content=content, kind=kind, tags=tags or [], salience=salience,
                     source=source, embedding=self.embedder.embed(content))
        return self.store.insert(mem)

    def update(self, mem_id: int, content: str) -> None:
        """Edit in place (typo fix, rewording). For a *changed fact*, prefer
        supersede() so the history is preserved."""
        self.store.set_fields(mem_id, content=content,
                              embedding=self.embedder.embed(content),
                              updated_at=now_ts())

    def supersede(self, old_id: int, new_content: str, **kw) -> int:
        """Record that a fact changed: create the new memory and link the old
        one to it. Keeps an auditable temporal chain instead of overwriting."""
        new_id = self.remember(new_content, **kw)
        self.store.set_fields(old_id, superseded_by=new_id, updated_at=now_ts())
        return new_id

    def forget(self, mem_id: int) -> None:
        self.store.delete(mem_id)

    def decay_and_prune(self, threshold: float = 0.05) -> int:
        """Drop memories whose salience-weighted recency has fallen below a
        threshold. Returns the number pruned."""
        now = now_ts()
        pruned = 0
        for m in self.store.all():
            effective = m.salience * recency_weight(m.created_at, now, self.half_life_days)
            if effective < threshold and m.superseded_by is None:
                self.store.delete(m.id)  # type: ignore[arg-type]
                pruned += 1
        return pruned

    # --- read operations --------------------------------------------------
    def recall(self, query: str, k: int = 5, kind: Optional[str] = None,
               include_superseded: bool = False, as_of=None) -> List[Hit]:
        """Rank memories by a blend of semantic similarity, recency, and
        salience. `as_of` enables time-travel: only memories that existed (and
        were not yet superseded) at that timestamp are considered."""
        qvec = self.embedder.embed(query)
        cutoff = to_ts(as_of) if as_of is not None else None
        now = cutoff or now_ts()
        hits: List[Hit] = []
        for m in self.store.all(kind=kind, include_superseded=True):
            if cutoff is not None and m.created_at > cutoff:
                continue
            superseded = m.superseded_by is not None
            if not include_superseded and as_of is None and superseded:
                continue
            sim = cosine(qvec, m.embedding) if m.embedding else 0.0
            rec = recency_weight(m.created_at, now, self.half_life_days)
            score = 0.6 * sim + 0.25 * rec + 0.15 * m.salience
            hits.append(Hit(memory=m, score=round(score, 4),
                            similarity=round(sim, 4), recency=round(rec, 4)))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]

    def history(self, mem_id: int) -> List[Memory]:
        """Follow the supersession chain forward from an id (multi-hop)."""
        chain: List[Memory] = []
        current = self.store.get(mem_id)
        seen = set()
        while current and current.id not in seen:
            seen.add(current.id)
            chain.append(current)
            current = self.store.get(current.superseded_by) if current.superseded_by else None
        return chain

    def summarize(self, kind: Optional[str] = None, max_items: int = 10) -> str:
        """Extractive digest of the most salient current memories. A production
        deployment would pass these to an LLM; the selection logic lives here so
        that call stays cheap and focused."""
        current = [m for m in self.store.all(kind=kind, include_superseded=False)]
        current.sort(key=lambda m: m.salience * recency_weight(m.created_at), reverse=True)
        lines = [f"- ({m.kind}) {m.content}" for m in current[:max_items]]
        return "\n".join(lines) if lines else "(no active memories)"
