"""Run me: `python examples/quickstart.py` (offline, no API keys)."""
from llm_memory import MemoryStore

mem = MemoryStore()  # in-memory; pass a path to persist

mem.remember("Production DB is PostgreSQL 16 on AWS RDS.", kind="fact", salience=0.9)
mem.remember("User prefers terse, no-emoji answers.", kind="preference", salience=0.8)
old = mem.remember("Deploy target is staging-east.", kind="fact")

print("Recall 'where do we deploy':")
for h in mem.recall("where do we deploy", k=2):
    print(f"  [{h.score}] ({h.memory.kind}) {h.memory.content}")

# A fact changes — supersede instead of overwrite, preserving history.
mem.supersede(old, "Deploy target is prod-east (cutover 2026-06).", kind="fact")
print("\nAfter supersede, recall 'deploy target':")
for h in mem.recall("deploy target", k=3):
    print(f"  [{h.score}] {h.memory.content}")

print("\nFull history chain of the original memory:")
print("  " + " -> ".join(m.content for m in mem.history(old)))

print("\nDigest:")
print(mem.summarize())
