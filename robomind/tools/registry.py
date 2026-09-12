"""Tool registry. Name -> tool. Tracks dry-run state."""
from __future__ import annotations

from typing import Any

from ..core.models import ToolResult
from . import runtime
from .base import BaseTool


class ToolRegistry:
    def __init__(self, *, dry_run: bool = False) -> None:
        self._tools: dict[str, BaseTool] = {}
        self.dry_run = dry_run

    def register(self, tool: BaseTool) -> None:
        if not tool.name:
            raise ValueError("tool must have a non-empty name")
        if tool.name in self._tools:
            raise ValueError(f"tool {tool.name!r} already registered")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list(self) -> list[str]:
        return sorted(self._tools.keys())

    def execute(self, _tool_name: str, **kwargs: Any) -> ToolResult:
        return runtime.execute(self, _tool_name, dry_run=self.dry_run, **kwargs)

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._tools