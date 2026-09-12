"""Unit conversion tool. Wraps robomind.domain.units."""
from __future__ import annotations

from typing import Any

from ..core.models import ToolResult
from ..domain import units as U
from .base import BaseTool


class UnitsTool(BaseTool):
    name = "units"
    description = "Convert between units, or list known units."
    safety_class = "compute"

    args_schema = {
        "action": "convert | list | category",
        "value": "float (convert)",
        "from_unit": "str (convert)",
        "to_unit": "str (convert)",
        "unit": "str (category)",
    }
    output_schema = {"result": "dict"}

    def run(self, *, step_id: str = "units", action: str = "convert",
            **kwargs: Any) -> ToolResult:
        if action == "convert":
            return self._convert(step_id, kwargs)
        if action == "list":
            return ToolResult(step_id=step_id, ok=True,
                              value={"units": U.known_units()})
        if action == "category":
            unit = kwargs.get("unit")
            if not unit:
                return ToolResult(step_id=step_id, ok=False,
                                  error="unit required")
            cat = U.category_of(unit)
            return ToolResult(step_id=step_id, ok=True,
                              value={"unit": unit, "category": cat})
        return ToolResult(step_id=step_id, ok=False,
                          error=f"unknown action: {action!r}")

    def _convert(self, step_id: str, kwargs: dict) -> ToolResult:
        v = kwargs.get("value")
        f = kwargs.get("from_unit")
        t = kwargs.get("to_unit")
        if v is None or f is None or t is None:
            return ToolResult(step_id=step_id, ok=False,
                              error="convert requires value, from_unit, to_unit")
        try:
            value = float(v)
        except (TypeError, ValueError):
            return ToolResult(step_id=step_id, ok=False,
                              error=f"value must be numeric, got {v!r}")
        from_unit = str(f)
        to_unit = str(t)
        try:
            result = U.convert(value, from_unit, to_unit)
        except ValueError as exc:
            return ToolResult(step_id=step_id, ok=False, error=str(exc))
        return ToolResult(step_id=step_id, ok=True, value={
            "value": value, "from": from_unit, "to": to_unit, "result": result,
        })