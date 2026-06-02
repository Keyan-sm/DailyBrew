"""SQLite-backed persistence for memories.

One table, indexed for the access patterns we care about (kind, time,
supersession chains). Embeddings are stored as JSON; for an MVP we score
similarity in Python, which is fine up to tens of thousands of rows. Swap in a
vector index (sqlite-vss / a vector DB) behind this same API when you outgrow it.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .temporal import now_ts


@dataclass
class Memory:
    content: str
    kind: str = "note"                       # fact | decision | preference | task | note
    tags: List[str] = field(default_factory=list)
    salience: float = 0.5                    # 0..1 importance prior
    source: Optional[str] = None
    created_at: float = field(default_factory=now_ts)
    updated_at: float = field(default_factory=now_ts)
    superseded_by: Optional[int] = None
    embedding: List[float] = field(default_factory=list)
    id: Optional[int] = None


SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    content       TEXT NOT NULL,
    kind          TEXT NOT NULL DEFAULT 'note',
    tags          TEXT NOT NULL DEFAULT '[]',
    salience      REAL NOT NULL DEFAULT 0.5,
    source        TEXT,
    created_at    REAL NOT NULL,
    updated_at    REAL NOT NULL,
    superseded_by INTEGER,
    embedding     TEXT NOT NULL DEFAULT '[]'
);
CREATE INDEX IF NOT EXISTS idx_mem_kind ON memories(kind);
CREATE INDEX IF NOT EXISTS idx_mem_created ON memories(created_at);
CREATE INDEX IF NOT EXISTS idx_mem_superseded ON memories(superseded_by);
"""


class Store:
    def __init__(self, path: str | Path = ":memory:"):
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    def insert(self, mem: Memory) -> int:
        cur = self.conn.execute(
            """INSERT INTO memories
               (content, kind, tags, salience, source, created_at, updated_at,
                superseded_by, embedding)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (mem.content, mem.kind, json.dumps(mem.tags), mem.salience, mem.source,
             mem.created_at, mem.updated_at, mem.superseded_by,
             json.dumps(mem.embedding)))
        self.conn.commit()
        mem.id = int(cur.lastrowid)
        return mem.id

    def get(self, mem_id: int) -> Optional[Memory]:
        row = self.conn.execute("SELECT * FROM memories WHERE id=?", (mem_id,)).fetchone()
        return _row_to_memory(row) if row else None

    def all(self, kind: Optional[str] = None, include_superseded: bool = True) -> List[Memory]:
        q = "SELECT * FROM memories"
        clauses, params = [], []
        if kind:
            clauses.append("kind=?"); params.append(kind)
        if not include_superseded:
            clauses.append("superseded_by IS NULL")
        if clauses:
            q += " WHERE " + " AND ".join(clauses)
        q += " ORDER BY created_at DESC"
        return [_row_to_memory(r) for r in self.conn.execute(q, params).fetchall()]

    def set_fields(self, mem_id: int, **fields) -> None:
        if not fields:
            return
        cols = ", ".join(f"{k}=?" for k in fields)
        vals = [json.dumps(v) if k in ("tags", "embedding") else v
                for k, v in fields.items()]
        self.conn.execute(f"UPDATE memories SET {cols} WHERE id=?", [*vals, mem_id])
        self.conn.commit()

    def delete(self, mem_id: int) -> None:
        self.conn.execute("DELETE FROM memories WHERE id=?", (mem_id,))
        self.conn.commit()


def _row_to_memory(row: sqlite3.Row) -> Memory:
    return Memory(
        id=row["id"], content=row["content"], kind=row["kind"],
        tags=json.loads(row["tags"]), salience=row["salience"], source=row["source"],
        created_at=row["created_at"], updated_at=row["updated_at"],
        superseded_by=row["superseded_by"], embedding=json.loads(row["embedding"]),
    )
