"""CAD tool. Emits CadQuery script text and validates via ast.parse.

Phase 3 does NOT execute CadQuery. Execution lands in Phase 5 behind an
explicit opt-in. For now the tool guarantees that generated scripts are
syntactically valid Python so they can be inspected or saved to disk.
"""
from __future__ import annotations

import ast
import textwrap
from typing import Any

from ..core.models import ToolResult
from .base import BaseTool


def _validate_python(source: str) -> tuple[bool, str | None]:
    try:
        ast.parse(source)
        return True, None
    except SyntaxError as exc:
        return False, f"line {exc.lineno}: {exc.msg}"


def _bracket_plate(width: float, height: float, thickness: float) -> str:
    return textwrap.dedent(f"""\
        import cadquery as cq

        # Rectangular mounting plate
        width = {width}
        height = {height}
        thickness = {thickness}

        result = (
            cq.Workplane("XY")
            .rect(width, height)
            .extrude(thickness)
        )
    """)


def _servo_bracket(
    servo_width: float, servo_length: float, thickness: float,
) -> str:
    return textwrap.dedent(f"""\
        import cadquery as cq

        # Simple servo mounting bracket (L-shape)
        sw = {servo_width}
        sl = {servo_length}
        t = {thickness}

        base = (
            cq.Workplane("XY")
            .rect(sl + 2 * t, sw + 2 * t)
            .extrude(t)
        )
        wall = (
            cq.Workplane("XY")
            .workplane(offset=t)
            .center(-(sl / 2), 0)
            .rect(t, sw + 2 * t)
            .extrude(sl)
        )
        result = base.union(wall)
    """)


class CADTool(BaseTool):
    name = "cad"
    description = "Generate parametric CadQuery scripts. Phase 3 emits text only."
    safety_class = "write"

    args_schema = {
        "action": "plate | servo_bracket | validate",
        "width": "float (plate)",
        "height": "float (plate)",
        "thickness": "float",
        "servo_width": "float (servo_bracket)",
        "servo_length": "float (servo_bracket)",
        "source": "str (validate)",
    }
    output_schema = {"script": "str"}

    def run(self, *, step_id: str = "cad",
            action: str = "plate", **kwargs: Any) -> ToolResult:
        if action == "plate":
            w = float(kwargs.get("width", 40.0))
            h = float(kwargs.get("height", 30.0))
            t = float(kwargs.get("thickness", 3.0))
            script = _bracket_plate(w, h, t)
            return self._emit(step_id, script, action)
        if action == "servo_bracket":
            sw = float(kwargs.get("servo_width", 12.0))
            sl = float(kwargs.get("servo_length", 23.0))
            t = float(kwargs.get("thickness", 3.0))
            script = _servo_bracket(sw, sl, t)
            return self._emit(step_id, script, action)
        if action == "validate":
            src = kwargs.get("source") or ""
            ok, err = _validate_python(src)
            return ToolResult(step_id=step_id, ok=ok,
                              value={"valid": ok, "error": err} if ok
                              else None,
                              error=None if ok else err)
        return ToolResult(step_id=step_id, ok=False,
                          error=f"unknown action: {action!r}")

    def _emit(self, step_id: str, script: str, action: str) -> ToolResult:
        ok, err = _validate_python(script)
        if not ok:
            return ToolResult(step_id=step_id, ok=False,
                              error=f"internal: generated script invalid ({err})")
        return ToolResult(step_id=step_id, ok=True, value={
            "action": action,
            "script": script,
            "note": "CadQuery execution available in Phase 5",
        })