import time

from virtual_context import MemoryStore, dispatch
from virtual_context.markdown_io import export_markdown, import_markdown
from virtual_context.temporal import now_ts


def test_remember_and_recall_relevance():
    mem = MemoryStore()
    mem.remember("The production database is PostgreSQL 16 on AWS RDS.", kind="fact")
    mem.remember("The user prefers terse, no-emoji responses.", kind="preference")
    mem.remember("We deploy via GitHub Actions on merge to main.", kind="fact")

    hits = mem.recall("what database do we use", k=2)
    assert hits, "expected at least one hit"
    assert "PostgreSQL" in hits[0].memory.content


def test_supersede_creates_history_chain():
    mem = MemoryStore()
    old = mem.remember("API base URL is api.v1.example.com", kind="fact")
    new = mem.supersede(old, "API base URL is api.v2.example.com", kind="fact")

    chain = mem.history(old)
    assert [m.id for m in chain] == [old, new]
    # Superseded fact is excluded from default recall...
    contents = [h.memory.content for h in mem.recall("api base url", k=5)]
    assert any("v2" in c for c in contents)
    assert not any("v1" in c for c in contents)


def test_as_of_time_travel_recall():
    mem = MemoryStore()
    old = mem.remember("Pricing is $20/mo", kind="fact")
    t_mid = now_ts()
    time.sleep(0.01)
    mem.supersede(old, "Pricing is $30/mo", kind="fact")

    # As of the midpoint, only the old fact existed.
    past = mem.recall("pricing", k=5, as_of=t_mid)
    assert any("$20" in h.memory.content for h in past)
    assert not any("$30" in h.memory.content for h in past)


def test_memory_as_tools_dispatch():
    mem = MemoryStore()
    rid = dispatch(mem, "memory_remember",
                   {"content": "Ship the router repo first", "kind": "task"})["id"]
    assert isinstance(rid, int)
    results = dispatch(mem, "memory_recall", {"query": "what should I ship", "k": 3})
    assert any("router" in r["content"] for r in results)


def test_markdown_roundtrip(tmp_path):
    src = tmp_path / "CLAUDE.md"
    src.write_text("# Preferences\n- Be terse\n# Facts\n- DB is Postgres\n")
    mem = MemoryStore()
    n = import_markdown(mem, src)
    assert n == 2
    out = export_markdown(mem)
    assert "Be terse" in out and "Postgres" in out


def test_decay_and_prune_keeps_supersession_history():
    mem = MemoryStore(half_life_days=0.000001)  # force aggressive decay
    old = mem.remember("ephemeral low value note", kind="note", salience=0.01)
    mem.supersede(old, "current value", kind="note", salience=0.9)
    pruned = mem.decay_and_prune(threshold=0.05)
    # The superseded record is protected from pruning (history preserved).
    assert mem.store.get(old) is not None
    assert pruned >= 0
