"""Ranked recall strategies over facts and episodes.

Combines FTS5 bm25 ranking with:
  - confidence weighting for facts
  - Reciprocal Rank Fusion (RRF) across result lists
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from ..core.models import Episode, Fact


RRF_K = 60.0  # standard RRF constant


@dataclass(slots=True)
class RankedFact:
    fact: Fact
    score: float
    source: str  # "fts" | "tag" | "like"


@dataclass(slots=True)
class RankedEpisode:
    episode: Episode
    score: float
    source: str


@dataclass(slots=True)
class RecallResult:
    query: str
    facts: list[RankedFact] = field(default_factory=list)
    episodes: list[RankedEpisode] = field(default_factory=list)


def _rrf_score(rank: int, k: float = RRF_K) -> float:
    return 1.0 / (k + rank + 1.0)


def recall_facts(
    store: Any,
    query: str,
    *,
    tags: Iterable[str] | None = None,
    limit: int = 10,
    min_confidence: float = 0.0,
) -> list[RankedFact]:
    """Return top facts for a query, ranked by FTS + confidence + tag match."""
    tags = tuple(t.strip().lower() for t in (tags or ()) if t.strip())
    candidates: dict[int, RankedFact] = {}

    # FTS pass
    for rank, f in enumerate(store.search_facts(query, limit=limit * 3)):
        if f.confidence < min_confidence:
            continue
        base = _rrf_score(rank)
        score = base * (0.5 + 0.5 * f.confidence)
        candidates[f.id] = RankedFact(fact=f, score=score, source="fts")

    # Tag pass — only if tags supplied
    if tags:
        for f in store.list_facts(limit=500):
            lower_tags = {t.lower() for t in f.tags}
            if lower_tags.intersection(tags):
                if f.confidence < min_confidence:
                    continue
                score = 0.5 * f.confidence
                existing = candidates.get(f.id)
                if existing is None or score > existing.score:
                    candidates[f.id] = RankedFact(fact=f, score=score, source="tag")

    ranked = sorted(candidates.values(), key=lambda r: r.score, reverse=True)
    return ranked[:limit]


def recall_episodes(
    store: Any,
    query: str,
    *,
    limit: int = 10,
) -> list[RankedEpisode]:
    """FTS-ranked episodes."""
    rows = store.search_episodes(query, limit=limit)
    return [
        RankedEpisode(episode=e, score=_rrf_score(rank), source="fts")
        for rank, e in enumerate(rows)
    ]


def recall(
    store: Any,
    query: str,
    *,
    tags: Iterable[str] | None = None,
    limit: int = 10,
    min_confidence: float = 0.0,
    include_episodes: bool = False,
) -> RecallResult:
    """Combined recall. Facts always; episodes optional."""
    result = RecallResult(query=query)
    result.facts = recall_facts(
        store, query, tags=tags, limit=limit, min_confidence=min_confidence
    )
    if include_episodes:
        result.episodes = recall_episodes(store, query, limit=limit)
    return result