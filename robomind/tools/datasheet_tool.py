"""Datasheet lookup tool."""
from __future__ import annotations

from typing import Any

from ..core.models import ToolResult
from ..domain import datasheets as D
from .base import BaseTool


class DatasheetTool(BaseTool):
    name = "datasheet"
    description = "Look up specs for common robotics components."
    safety_class = "read"

    args_schema = {
        "action": "lookup | search | category | list",
        "name": "str (lookup, category)",
        "query": "str (search)",
        "limit": "int (search, default 10)",
    }
    output_schema = {"result": "dict"}

    def run(self, *, step_id: str = "datasheet",
            action: str = "lookup", **kwargs: Any) -> ToolResult:
        if action == "lookup":
            name = kwargs.get("name")
            if not name:
                return ToolResult(step_id=step_id, ok=False,
                                  error="name required")
            sheet = D.lookup(name)
            if sheet is None:
                return ToolResult(step_id=step_id, ok=False,
                                  error=f"unknown component: {name!r}")
            return ToolResult(step_id=step_id, ok=True,
                              value={"name": name, "datasheet": sheet})
        if action == "search":
            q = kwargs.get("query") or ""
            hits = D.search(q, limit=int(kwargs.get("limit", 10)))
            return ToolResult(step_id=step_id, ok=True,
                              value={"query": q,
                                     "hits": [{"name": n, "category": c}
                                              for n, c in hits]})
        if action == "category":
            name = kwargs.get("name")
            if not name:
                return ToolResult(step_id=step_id, ok=False,
                                  error="name required")
            cat = D.category_of(name)
            return ToolResult(step_id=step_id, ok=True,
                              value={"name": name, "category": cat})
        if action == "list":
            return ToolResult(step_id=step_id, ok=True,
                              value={"inventory": D.all_names()})
        return ToolResult(step_id=step_id, ok=False,
                          error=f"unknown action: {action!r}")