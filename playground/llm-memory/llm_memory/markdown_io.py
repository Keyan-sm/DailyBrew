"""Import from / export to markdown.

The point of the library is to be a drop-in upgrade over "a pile of markdown
files" (CLAUDE.md, AGENTS.md, notes). So we make the migration trivial: import
an existing markdown file into structured memories, and export back to markdown
for human review or for harnesses that still want a flat file.
"""
from __future__ import annotations

import re
from pathlib import Path

from .memory import MemoryStore

_BULLET = re.compile(r"^\s*[-*]\s+(.*)$")
_HEADING = re.compile(r"^#{1,6}\s+(.*)$")

# Map common section headings to memory kinds.
_KIND_HINTS = {
    "decision": "decision", "decisions": "decision",
    "preference": "preference", "preferences": "preference", "style": "preference",
    "todo": "task", "tasks": "task", "task": "task",
    "fact": "fact", "facts": "fact", "context": "fact",
}


def import_markdown(store: MemoryStore, path: str | Path, default_kind: str = "note") -> int:
    """Parse a markdown file into memories. Bullets become individual memories;
    the current heading determines their kind. Returns the count imported."""
    text = Path(path).read_text()
    kind = default_kind
    count = 0
    for line in text.splitlines():
        h = _HEADING.match(line)
        if h:
            label = h.group(1).strip().lower()
            kind = next((v for k, v in _KIND_HINTS.items() if k in label), default_kind)
            continue
        b = _BULLET.match(line)
        if b and b.group(1).strip():
            store.remember(b.group(1).strip(), kind=kind, source=str(path))
            count += 1
    return count


def export_markdown(store: MemoryStore, path: str | Path | None = None) -> str:
    """Render active memories grouped by kind as markdown."""
    by_kind: dict[str, list[str]] = {}
    for m in store.store.all(include_superseded=False):
        by_kind.setdefault(m.kind, []).append(m.content)
    parts = ["# Memory\n"]
    for kind in sorted(by_kind):
        parts.append(f"\n## {kind.capitalize()}\n")
        parts.extend(f"- {c}" for c in by_kind[kind])
    out = "\n".join(parts) + "\n"
    if path:
        Path(path).write_text(out)
    return out
