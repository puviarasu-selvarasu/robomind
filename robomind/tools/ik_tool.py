"""Inverse kinematics tool. 2-link planar arm, closed form."""
from __future__ import annotations

from typing import Any

from ..core.models import ToolResult
from ..domain import kinematics as K
from .base import BaseTool


class IKTool(BaseTool):
    name = "ik"
    description = "2-link planar inverse kinematics. Returns elbow-up and elbow-down solutions."
    safety_class = "compute"

    args_schema = {
        "x": "float — target x (meters, or same units as L1/L2)",
        "y": "float — target y",
        "L1": "float — first link length",
        "L2": "float — second link length",
        "unit": "str — 'deg' (default) or 'rad' for output angles",
    }
    output_schema = {"solutions": "list[{theta1, theta2, elbow}]"}

    def run(self, *, step_id: str = "ik",
            x: float | None = None, y: float | None = None,
            L1: float | None = None, L2: float | None = None,
            unit: str = "deg", **_: Any) -> ToolResult:
        if None in (x, y, L1, L2):
            return ToolResult(step_id=step_id, ok=False,
                              error="x, y, L1, L2 are all required")
        try:
            up, down = K.ik_2d_2link(float(x), float(y), float(L1), float(L2))
        except K.Unreachable as exc:
            return ToolResult(step_id=step_id, ok=False,
                              error=f"unreachable: {exc}")
        except K.KinematicsError as exc:
            return ToolResult(step_id=step_id, ok=False, error=str(exc))

        def pack(sol: K.IK2Solution) -> dict:
            if unit == "rad":
                return {"theta1": sol.theta1_rad, "theta2": sol.theta2_rad,
                        "elbow": sol.elbow}
            return {"theta1": K.rad2deg(sol.theta1_rad),
                    "theta2": K.rad2deg(sol.theta2_rad),
                    "elbow": sol.elbow}

        return ToolResult(step_id=step_id, ok=True, value={
            "target": {"x": float(x), "y": float(y)},
            "L1": float(L1), "L2": float(L2),
            "unit": unit,
            "solutions": [pack(up), pack(down)],
        })