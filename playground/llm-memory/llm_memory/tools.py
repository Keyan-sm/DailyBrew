"""Memory-as-tools: expose memory operations as tool/function schemas an LLM
agent can call directly.

This is the "memory operations as actions" idea from recent agent-memory work:
instead of the harness deciding when to write/read memory, the model itself
calls these tools. The schemas are vendor-neutral JSON; adapt the wrapper to
OpenAI `tools` or Anthropic `tools` as needed. `dispatch()` wires a tool call
straight to a MemoryStore.
"""
from __future__ import annotations

from typing import Any, Dict

from .memory import MemoryStore

TOOLS = [
    {
        "name": "memory_remember",
        "description": "Store a new memory (a fact, decision, preference, task, or note).",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "kind": {"type": "string",
                         "enum": ["fact", "decision", "preference", "task", "note"]},
                "tags": {"type": "array", "items": {"type": "string"}},
                "salience": {"type": "number", "description": "0..1 importance"},
            },
            "required": ["content"],
        },
    },
    {
        "name": "memory_recall",
        "description": "Retrieve the most relevant memories for a query, ranked by "
                       "semantic similarity, recency, and importance.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "k": {"type": "integer", "default": 5},
                "kind": {"type": "string"},
                "as_of": {"type": "string",
                          "description": "ISO timestamp for time-travel recall"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "memory_supersede",
        "description": "Record that a previously stored fact has changed. Links the "
                       "old memory to the new one, preserving history.",
        "parameters": {
            "type": "object",
            "properties": {
                "old_id": {"type": "integer"},
                "new_content": {"type": "string"},
            },
            "required": ["old_id", "new_content"],
        },
    },
    {
        "name": "memory_forget",
        "description": "Delete a memory by id.",
        "parameters": {
            "type": "object",
            "properties": {"mem_id": {"type": "integer"}},
            "required": ["mem_id"],
        },
    },
]


def dispatch(store: MemoryStore, name: str, args: Dict[str, Any]) -> Any:
    """Execute a tool call against a MemoryStore and return a JSON-able result."""
    if name == "memory_remember":
        return {"id": store.remember(
            args["content"], kind=args.get("kind", "note"),
            tags=args.get("tags"), salience=args.get("salience", 0.5))}
    if name == "memory_recall":
        hits = store.recall(args["query"], k=args.get("k", 5),
                            kind=args.get("kind"), as_of=args.get("as_of"))
        return [{"id": h.memory.id, "content": h.memory.content,
                 "kind": h.memory.kind, "score": h.score} for h in hits]
    if name == "memory_supersede":
        return {"new_id": store.supersede(args["old_id"], args["new_content"])}
    if name == "memory_forget":
        store.forget(args["mem_id"])
        return {"ok": True}
    raise ValueError(f"unknown tool: {name}")
