"""Forward kinematics tool. 2-link or n-link planar chains."""
from __future__ import annotations

from typing import Any

from ..core.models import ToolResult
from ..domain import kinematics as K
from .base import BaseTool


class FKTool(BaseTool):
    name = "fk"
    description = "Forward kinematics for a planar chain (absolute or relative angles)."
    safety_class = "compute"

    args_schema = {
        "link_lengths": "list[float] — meters",
        "joint_angles_deg": "list[float] — degrees; absolute by default",
        "relative": "bool — if true, angles are relative to previous link",
    }
    output_schema = {"x": "float", "y": "float"}

    def run(self, *, step_id: str = "fk",
            link_lengths: list | None = None,
            joint_angles_deg: list | None = None,
            relative: bool = False,
            **_: Any) -> ToolResult:
        if not link_lengths or not joint_angles_deg:
            return ToolResult(step_id=step_id, ok=False,
                              error="link_lengths and joint_angles_deg required")
        if len(link_lengths) != len(joint_angles_deg):
            return ToolResult(step_id=step_id, ok=False,
                              error="link_lengths and joint_angles_deg must match length")
        angles_rad = [K.deg2rad(a) for a in joint_angles_deg]
        try:
            if relative:
                x, y = K.fk_2d_relative(link_lengths, angles_rad)
            else:
                x, y = K.fk_2d(link_lengths, angles_rad)
        except K.KinematicsError as exc:
            return ToolResult(step_id=step_id, ok=False, error=str(exc))
        return ToolResult(step_id=step_id, ok=True,
                          value={"x": x, "y": y, "n_links": len(link_lengths)})