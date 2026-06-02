"""Pluggable embeddings.

The default embedder is a dependency-free, deterministic hashing embedder so the
whole library runs offline (and tests are reproducible). It is not as good as a
real embedding model, but it gives meaningful lexical/semantic-ish similarity
for recall. Swap in a real provider for production via the Embedder protocol.
"""
from __future__ import annotations

import math
import re
from typing import List, Protocol

_TOKEN = re.compile(r"[a-z0-9]+")

# A small stopword list. Removing high-frequency noise words sharpens the
# bag-of-words similarity (the MVP embedder has no corpus IDF to lean on).
_STOPWORDS = frozenset("""
a an and are as at be by do does for from how in is it its of on or our that the
their they this to use used using via we what when where which who why will with
you your i me my
""".split())


def _tokens(text: str) -> List[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOPWORDS]


class Embedder(Protocol):
    dim: int
    def embed(self, text: str) -> List[float]: ...


class HashingEmbedder:
    """Hashing-trick bag-of-words with sublinear term weighting, L2-normalized.

    Deterministic across runs and machines (uses a fixed seed in the hash), so
    similarity scores are stable in tests.
    """

    def __init__(self, dim: int = 256):
        self.dim = dim

    def embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        counts: dict[str, int] = {}
        for tok in _tokens(text):
            counts[tok] = counts.get(tok, 0) + 1
        for tok, c in counts.items():
            h = hash_token(tok)
            idx = h % self.dim
            sign = 1.0 if (h >> 31) & 1 else -1.0
            vec[idx] += sign * (1.0 + math.log(c))
        return _l2_normalize(vec)


def hash_token(tok: str) -> int:
    # FNV-1a: stable across processes (unlike Python's salted hash()).
    h = 0x811C9DC5
    for ch in tok.encode():
        h ^= ch
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def _l2_normalize(vec: List[float]) -> List[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm < 1e-12:
        return vec
    return [v / norm for v in vec]


def cosine(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))   # both are L2-normalized
