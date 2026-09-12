"""Case-based reasoning via Jaccard token similarity.

Retrieval strategy:
  1. FTS pre-filter (top N candidates) when a query is present.
  2. Jaccard re-rank by token overlap over ``episodes.input``.
  3. Return top-k.

Falls back to full scan for small stores (< 200 episodes) so early use
is not penalized by FTS tokenization quirks.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from ..core.models import Episode


_TOKEN_RE = re.compile(r"[a-z0-9_]+")
_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for",
    "is", "are", "be", "with", "by", "at", "as", "it", "this", "that",
    "i", "me", "my", "you", "we", "us", "our",
})

FULL_SCAN_THRESHOLD = 200
PRE_FILTER_LIMIT = 100


@dataclass(slots=True)
class Case:
    episode: Episode
    similarity: float


def tokenize(text: str) -> frozenset[str]:
    if not text:
        return frozenset()
    return frozenset(
        t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS
    )


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def similar_episodes(
    store: Any,
    query: str,
    *,
    k: int = 3,
    min_similarity: float = 0.05,
) -> list[Case]:
    """Return top-k similar past episodes for a text query."""
    q_tokens = tokenize(query)
    if not q_tokens:
        return []

    total = store.count_episodes()
    if total == 0:
        return []

    if total <= FULL_SCAN_THRESHOLD:
        candidates = store.list_episodes(limit=total)
    else:
        candidates = store.search_episodes(query, limit=PRE_FILTER_LIMIT)
        if not candidates:
            candidates = store.list_episodes(limit=PRE_FILTER_LIMIT)

    scored: list[Case] = []
    for ep in candidates:
        sim = jaccard(q_tokens, tokenize(ep.input))
        if sim >= min_similarity:
            scored.append(Case(episode=ep, similarity=sim))

    scored.sort(key=lambda c: c.similarity, reverse=True)
    return scored[:k]