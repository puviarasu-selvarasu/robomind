"""Domain safety and feasibility checks. Each returns a CheckResult."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from . import kinematics as K


@dataclass(frozen=True, slots=True)
class CheckResult:
    ok: bool
    name: str
    message: str
    value: float | None = None
    limit: float | None = None

    def __bool__(self) -> bool:
        return self.ok


# ------------------------------------------------------------- checks
def check_joint_limits(
    angle_rad: float,
    min_rad: float,
    max_rad: float,
    *,
    joint_name: str = "joint",
) -> CheckResult:
    if min_rad >= max_rad:
        return CheckResult(False, f"{joint_name}.limits",
                           f"invalid limit range [{min_rad}, {max_rad}]")
    if angle_rad < min_rad or angle_rad > max_rad:
        return CheckResult(
            False, f"{joint_name}.limits",
            f"{joint_name} angle {angle_rad:.4f} rad outside "
            f"[{min_rad:.4f}, {max_rad:.4f}]",
            value=angle_rad, limit=None,
        )
    return CheckResult(True, f"{joint_name}.limits", "within limits",
                       value=angle_rad)


def check_reach(
    x: float, y: float, L1: float, L2: float,
) -> CheckResult:
    r_min, r_max = K.workspace_2link(L1, L2)
    r = (x * x + y * y) ** 0.5
    if r > r_max + 1e-9:
        return CheckResult(False, "reach",
                           f"target r={r:.4f} exceeds max reach {r_max:.4f}",
                           value=r, limit=r_max)
    if r < r_min - 1e-9:
        return CheckResult(False, "reach",
                           f"target r={r:.4f} inside min reach {r_min:.4f}",
                           value=r, limit=r_min)
    return CheckResult(True, "reach", f"reachable (r={r:.4f})", value=r)


def check_torque(
    required_Nm: float,
    available_Nm: float,
    *,
    joint_name: str = "joint",
) -> CheckResult:
    if available_Nm <= 0:
        return CheckResult(False, f"{joint_name}.torque",
                           f"no available torque specified")
    if required_Nm > available_Nm:
        return CheckResult(
            False, f"{joint_name}.torque",
            f"{joint_name} needs {required_Nm:.4f} N·m, "
            f"only {available_Nm:.4f} N·m available",
            value=required_Nm, limit=available_Nm,
        )
    return CheckResult(True, f"{joint_name}.torque",
                       f"ok ({required_Nm:.4f} / {available_Nm:.4f} N·m)",
                       value=required_Nm, limit=available_Nm)


def check_voltage(
    measured_V: float,
    min_V: float,
    max_V: float,
    *,
    label: str = "supply",
) -> CheckResult:
    if measured_V < min_V or measured_V > max_V:
        return CheckResult(
            False, f"{label}.voltage",
            f"{label} {measured_V:.3f} V outside [{min_V:.3f}, {max_V:.3f}]",
            value=measured_V,
        )
    return CheckResult(True, f"{label}.voltage",
                       f"ok ({measured_V:.3f} V)", value=measured_V)


def check_thermal(
    power_dissipated_W: float,
    max_power_W: float,
    *,
    label: str = "component",
) -> CheckResult:
    if power_dissipated_W > max_power_W:
        return CheckResult(
            False, f"{label}.thermal",
            f"{label} dissipates {power_dissipated_W:.3f} W, "
            f"limit {max_power_W:.3f} W",
            value=power_dissipated_W, limit=max_power_W,
        )
    return CheckResult(True, f"{label}.thermal",
                       f"ok ({power_dissipated_W:.3f} W)",
                       value=power_dissipated_W, limit=max_power_W)


def check_current(
    current_A: float,
    max_current_A: float,
    *,
    label: str = "supply",
) -> CheckResult:
    if current_A > max_current_A:
        return CheckResult(
            False, f"{label}.current",
            f"{label} draws {current_A:.3f} A, limit {max_current_A:.3f} A",
            value=current_A, limit=max_current_A,
        )
    return CheckResult(True, f"{label}.current",
                       f"ok ({current_A:.3f} A)",
                       value=current_A, limit=max_current_A)


# ----------------------------------------------------- aggregator
@dataclass(frozen=True, slots=True)
class RuleSetResult:
    checks: tuple[CheckResult, ...]

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks)

    @property
    def failures(self) -> tuple[CheckResult, ...]:
        return tuple(c for c in self.checks if not c.ok)

    def summary(self) -> str:
        if self.ok:
            return f"all {len(self.checks)} checks passed"
        return "; ".join(f.message for f in self.failures)


def evaluate(checks: Sequence[CheckResult]) -> RuleSetResult:
    return RuleSetResult(checks=tuple(checks))