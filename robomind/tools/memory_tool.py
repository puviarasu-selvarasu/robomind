"""Memory tool: learn | recall | forget."""
from __future__ import annotations

import re
from typing import Any

from ..core.models import Fact, ToolResult
from ..memory import recall as recall_mod
from .base import BaseTool


_TAG_RE = re.compile(r"#([A-Za-z0-9_\-]+)")


def _extract_tags(text: str) -> tuple[str, tuple[str, ...]]:
    tags = tuple(m.group(1) for m in _TAG_RE.finditer(text))
    cleaned = _TAG_RE.sub("", text).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned, tags


class MemoryTool(BaseTool):
    name = "memory"
    description = "Persist and retrieve facts and episodes."
    safety_class = "read"  # individual actions are gated

    args_schema = {
        "action": "learn | recall | forget",
        "topic": "str (for learn)",
        "fact": "str (for learn)",
        "query": "str (for recall)",
        "tags": "tuple[str] (optional)",
        "limit": "int (recall, default 10)",
    }
    output_schema = {"result": "dict"}

    def __init__(self, store: Any) -> None:
        self.store = store

    def run(self, *, step_id: str = "memory",
            action: str = "", **kwargs: Any) -> ToolResult:
        try:
            if action == "learn":
                return self._learn(step_id, kwargs)
            if action == "recall":
                return self._recall(step_id, kwargs)
            return ToolResult(step_id=step_id, ok=False,
                              error=f"unknown action: {action!r}")
        except Exception as exc:
            return ToolResult(step_id=step_id, ok=False, error=str(exc))

    def _learn(self, step_id: str, kwargs: dict) -> ToolResult:
        topic = (kwargs.get("topic") or "").strip()
        raw_fact = (kwargs.get("fact") or "").strip()
        if not topic or not raw_fact:
            return ToolResult(step_id=step_id, ok=False,
                              error="learn requires topic and fact")

        fact_text, inline_tags = _extract_tags(raw_fact)
        extra_tags = tuple(kwargs.get("tags") or ())
        tags = tuple(dict.fromkeys(inline_tags + extra_tags))

        fact = Fact(topic=topic, fact=fact_text, tags=tags, confidence=1.0)
        fid = self.store.insert_fact(fact)
        stored = self.store.get_fact(fid)
        return ToolResult(
            step_id=step_id, ok=True,
            value={"id": fid, "topic": stored.topic, "fact": stored.fact,
                   "tags": stored.tags, "confidence": stored.confidence},
        )

    def _recall(self, step_id: str, kwargs: dict) -> ToolResult:
        query = (kwargs.get("query") or "").strip()
        if not query:
            return ToolResult(step_id=step_id, ok=False,
                              error="recall requires a query")
        limit = int(kwargs.get("limit") or 10)
        tags = kwargs.get("tags") or ()

        result = recall_mod.recall(
            self.store, query, tags=tags, limit=limit,
            include_episodes=kwargs.get("include_episodes", False),
        )
        return ToolResult(
            step_id=step_id, ok=True,
            value={
                "query": query,
                "facts": [
                    {"id": rf.fact.id, "topic": rf.fact.topic,
                     "fact": rf.fact.fact, "tags": rf.fact.tags,
                     "confidence": rf.fact.confidence,
                     "score": round(rf.score, 4), "source": rf.source}
                    for rf in result.facts
                ],
                "episodes": [
                    {"id": re.episode.id, "input": re.episode.input,
                     "score": round(re.score, 4), "source": re.source}
                    for re in result.episodes
                ],
            },
        )