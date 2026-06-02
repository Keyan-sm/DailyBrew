"""virtual-context: MemGPT-style virtual context + Generative-Agents memory retrieval for LLM agents."""
from .embedding import Embedder, HashingEmbedder, cosine
from .memory import Hit, MemoryStore
from .store import Memory, Store
from .tools import TOOLS, dispatch

__version__ = "0.1.0"
__all__ = [
    "MemoryStore", "Hit", "Memory", "Store",
    "Embedder", "HashingEmbedder", "cosine", "TOOLS", "dispatch",
]
