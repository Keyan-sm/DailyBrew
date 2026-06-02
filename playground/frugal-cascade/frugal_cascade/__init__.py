"""frugal-cascade: a FrugalGPT-style cost-aware LLM cascade and router."""
from .features import RequestFeatures, featurize
from .policy import ScoredModel, Weights, score_models
from .providers import AnthropicProvider, MockProvider, OpenAIProvider, Provider, Response
from .registry import Model, default_registry, load_registry
from .router import Decision, Router, RunResult

__version__ = "0.1.0"
__all__ = [
    "Router", "Decision", "RunResult", "Model", "default_registry", "load_registry",
    "RequestFeatures", "featurize", "Weights", "ScoredModel", "score_models",
    "Provider", "Response", "MockProvider", "OpenAIProvider", "AnthropicProvider",
]
