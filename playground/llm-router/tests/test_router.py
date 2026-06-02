from llm_router import Router, featurize, score_models, default_registry
from llm_router.evaluate import SAMPLE_PROMPTS, evaluate
from llm_router.policy import Weights


def test_featurize_detects_code_and_chat():
    assert featurize("Refactor this ```python\nx=1\n``` and fix the bug").task_type == "code"
    assert featurize("What's the capital of France?").task_type == "chat"


def test_easy_request_does_not_pick_frontier_model():
    # Anti-collapse: a trivial prompt should route to a cheap model, not opus.
    router = Router()
    decision = router.route("What's the capital of France?")
    assert decision.chosen.name in {"haiku", "gpt-mini"}


def test_hard_request_prefers_capable_model():
    router = Router()
    hard = "Prove step by step why this distributed consensus design is correct. " * 20
    decision = router.route(hard)
    assert decision.ranked[0].quality_fit >= 0.85


def test_cascade_escalates_on_low_confidence():
    router = Router()
    hard = "Derive and prove the regret bound step by step in full detail. " * 20
    result = router.run(hard, confidence_threshold=0.95)
    # A high threshold on a hard task forces escalation through multiple models.
    assert result.escalated
    assert len(result.attempts) >= 2


def test_eval_reports_savings_vs_frontier_baseline():
    report = evaluate(SAMPLE_PROMPTS)
    assert report.routed_cost < report.baseline_cost
    assert report.savings_pct > 0


def test_long_context_filters_small_window_models():
    # Force a request larger than gpt-mini's 128k window; it must be excluded.
    huge = "word " * 60_000
    feat = featurize(huge)
    assert feat.needs_long_context
    scored = score_models(default_registry(), feat, Weights())
    assert all(s.model.max_context >= feat.est_tokens_in for s in scored)
