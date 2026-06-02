"""Run me: `python examples/quickstart.py` (no API keys needed — uses the mock provider)."""
from frugal_cascade import Router
from frugal_cascade.evaluate import SAMPLE_PROMPTS, evaluate

router = Router()

print("== Routing decisions ==")
for prompt in ["What's the capital of France?",
               "Refactor this ```python``` function and fix the bug",
               "Prove step by step why Raft is safe. " * 15]:
    d = router.route(prompt)
    print(f"  {d.features.task_type:13} diff={d.features.difficulty:<5} -> {d.chosen.name}")

print("\n== Cost evaluation vs always-frontier baseline ==")
report = evaluate(SAMPLE_PROMPTS, router)
print(f"  routed=${report.routed_cost:.6f}  baseline=${report.baseline_cost:.6f}  "
      f"savings={report.savings_pct}%  escalations={report.escalations}/{report.n}")
