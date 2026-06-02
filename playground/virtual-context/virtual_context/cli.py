"""CLI: `virtual-context remember|recall|summarize|import|export` against a SQLite DB."""
from __future__ import annotations

import argparse
import json

from .markdown_io import export_markdown, import_markdown
from .memory import MemoryStore


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="virtual-context",
                                     description="A structured, queryable memory layer for agents.")
    parser.add_argument("--db", default="memory.db", help="SQLite path (default: memory.db)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_rem = sub.add_parser("remember")
    p_rem.add_argument("content")
    p_rem.add_argument("--kind", default="note")
    p_rem.add_argument("--salience", type=float, default=0.5)

    p_rec = sub.add_parser("recall")
    p_rec.add_argument("query")
    p_rec.add_argument("-k", type=int, default=5)
    p_rec.add_argument("--kind")

    sub.add_parser("summarize").add_argument("--kind", default=None)

    p_imp = sub.add_parser("import"); p_imp.add_argument("path")
    p_exp = sub.add_parser("export"); p_exp.add_argument("path", nargs="?")

    args = parser.parse_args(argv)
    mem = MemoryStore(args.db)

    if args.cmd == "remember":
        print(json.dumps({"id": mem.remember(args.content, kind=args.kind,
                                             salience=args.salience)}))
    elif args.cmd == "recall":
        hits = mem.recall(args.query, k=args.k, kind=args.kind)
        print(json.dumps([{"id": h.memory.id, "content": h.memory.content,
                           "kind": h.memory.kind, "score": h.score} for h in hits], indent=2))
    elif args.cmd == "summarize":
        print(mem.summarize(kind=args.kind))
    elif args.cmd == "import":
        print(f"imported {import_markdown(mem, args.path)} memories from {args.path}")
    elif args.cmd == "export":
        out = export_markdown(mem, args.path)
        if not args.path:
            print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
