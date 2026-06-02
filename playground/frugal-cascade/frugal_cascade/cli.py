"""Command-line interface: `frugal-cascade route|run|eval`."""
from __future__ import annotations

import argparse
import json

from .evaluate import SAMPLE_PROMPTS, evaluate
from .registry import default_registry, load_registry
from .router import Router


def _build_router(args) -> Router:
    models = load_registry(args.config) if getattr(args, "config", None) else default_registry()
    return Router(models=models)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="frugal-cascade",
                                     description="Cost-aware LLM router for agent workspaces.")
    parser.add_argument("--config", help="Path to a models.yaml registry.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_route = sub.add_parser("route", help="Show which model would be chosen (no API call).")
    p_route.add_argument("prompt")

    p_run = sub.add_parser("run", help="Route + execute with the cascade (mock provider by default).")
    p_run.add_argument("prompt")
    p_run.add_argument("--no-cascade", action="store_true")

    p_eval = sub.add_parser("eval", help="Run the built-in sample suite and report cost savings.")
    p_eval.add_argument("-v", "--verbose", action="store_true", help="Show per-prompt detail.")

    args = parser.parse_args(argv)
    router = _build_router(args)

    if args.cmd == "route":
        d = router.route(args.prompt)
        print(json.dumps({
            "chosen": d.chosen.name,
            "rationale": d.rationale,
            "ranking": [{"model": s.model.name, "score": s.score,
                         "est_cost": round(s.est_cost, 6)} for s in d.ranked],
        }, indent=2))
    elif args.cmd == "run":
        r = router.run(args.prompt, cascade=not args.no_cascade)
        print(json.dumps({
            "answer": r.response.text, "attempts": r.attempts,
            "escalated": r.escalated, "total_cost": r.total_cost,
            "confidence": r.response.confidence,
        }, indent=2))
    elif args.cmd == "eval":
        report = evaluate(SAMPLE_PROMPTS, router)
        print(f"n={report.n}  routed=${report.routed_cost:.4f}  "
              f"baseline(always-frontier)=${report.baseline_cost:.4f}  "
              f"savings={report.savings_pct}%  escalations={report.escalations}/{report.n}")
        if args.verbose:
            print(json.dumps(report.per_prompt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
