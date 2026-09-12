"""Trajectory generator tool."""
from __future__ import annotations

from typing import Any

from ..core.models import ToolResult
from ..domain import kinematics as K
from .base import BaseTool


class TrajectoryTool(BaseTool):
    name = "trajectory"
    description = "Generate 1D motion profiles: linear, cubic, trapezoidal."
    safety_class = "compute"

    args_schema = {
        "action": "linear | cubic | trapezoidal",
        "start": "float (linear, cubic)",
        "end": "float (linear, cubic)",
        "n": "int — samples",
        "v0": "float — initial velocity (cubic)",
        "v1": "float — final velocity (cubic)",
        "duration": "float — seconds (cubic)",
        "distance": "float (trapezoidal)",
        "max_vel": "float (trapezoidal)",
        "max_accel": "float (trapezoidal)",
    }
    output_schema = {"samples": "list[float]", "meta": "dict"}

    def run(self, *, step_id: str = "traj",
            action: str = "linear", **kwargs: Any) -> ToolResult:
        try:
            if action == "linear":
                return self._linear(step_id, kwargs)
            if action == "cubic":
                return self._cubic(step_id, kwargs)
            if action == "trapezoidal":
                return self._trapezoidal(step_id, kwargs)
        except (K.KinematicsError, TypeError, ValueError) as exc:
            return ToolResult(step_id=step_id, ok=False, error=str(exc))
        return ToolResult(step_id=step_id, ok=False,
                          error=f"unknown action: {action!r}")

    def _linear(self, step_id: str, kw: dict) -> ToolResult:
        s = float(kw.get("start"))
        e = float(kw.get("end"))
        n = int(kw.get("n", 20))
        samples = K.linear_interp(s, e, n)
        return ToolResult(step_id=step_id, ok=True,
                          value={"samples": samples,
                                 "meta": {"kind": "linear", "n": n}})

    def _cubic(self, step_id: str, kw: dict) -> ToolResult:
        s = float(kw.get("start"))
        e = float(kw.get("end"))
        n = int(kw.get("n", 20))
        v0 = float(kw.get("v0", 0.0))
        v1 = float(kw.get("v1", 0.0))
        dur = float(kw.get("duration", 1.0))
        samples = K.cubic_interp(s, e, n, v0=v0, v1=v1, duration=dur)
        return ToolResult(step_id=step_id, ok=True,
                          value={"samples": samples,
                                 "meta": {"kind": "cubic", "n": n,
                                          "duration": dur}})

    def _trapezoidal(self, step_id: str, kw: dict) -> ToolResult:
        d = float(kw.get("distance"))
        vmax = float(kw.get("max_vel"))
        amax = float(kw.get("max_accel"))
        n = int(kw.get("n", 30))
        p = K.trapezoidal_profile(d, vmax, amax)
        samples = p.sample(n)
        return ToolResult(step_id=step_id, ok=True, value={
            "samples": samples,
            "meta": {
                "kind": "trapezoidal", "n": n,
                "t_accel": p.t_accel, "t_cruise": p.t_cruise,
                "t_total": p.t_total, "peak_vel": p.peak_vel,
                "triangular": p.t_cruise == 0.0,
            },
        })