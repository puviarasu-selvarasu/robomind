"""Tool execution wrapper. Enforces --dry-run at the registry level.

Reserved kwargs:
  _tool_name  — internal, injected by ToolRegistry.execute
  step_id     — keyword-only, injected here
  dry_run     — keyword-only, injected by ToolRegistry.execute

Users must not pass kwargs starting with ``_``. Tools must not declare
parameters named ``_tool_name``, ``dry_run``, or ``step_id``.
"""
from __future__ import annotations

from typing import Any

from ..core.models import ToolResult


BLOCKED_CLASSES = ("write", "hardware")


def execute(
    registry: Any,
    _tool_name: str,
    *,
    dry_run: bool = False,
    step_id: str | None = None,
    **kwargs: Any,
) -> ToolResult:
    reserved = [k for k in kwargs if k.startswith("_")]
    if reserved:
        return ToolResult(step_id=step_id or _tool_name, ok=False,
                          error=f"reserved kwarg(s): {reserved}")
    tool = registry.get(_tool_name)
    if tool is None:
        return ToolResult(step_id=step_id or _tool_name, ok=False,
                          error=f"no such tool: {_tool_name!r}")
    if dry_run and tool.safety_class in BLOCKED_CLASSES:
        return ToolResult(
            step_id=step_id or _tool_name, ok=False,
            error=f"dry-run: blocked {tool.safety_class} tool {_tool_name!r}",
        )
    try:
        return tool.run(step_id=step_id or _tool_name, **kwargs)
    except TypeError as exc:
        return ToolResult(step_id=step_id or _tool_name, ok=False,
                          error=f"argument error: {exc}")
    except Exception as exc:
        return ToolResult(step_id=step_id or _tool_name, ok=False, error=str(exc))