"""Planar kinematics: FK, 2-link IK, Jacobian, trajectories.

Conventions:
  * Angles in radians internally.
  * Joint angles measured counterclockwise from +x axis.
  * FK for an n-link planar chain: cumulative joint angles.
  * IK for 2-link arm returns two solutions (elbow up / elbow down).
  * All inputs treated as immutable sequences.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


# --------------------------------------------------------------- errors
class KinematicsError(ValueError):
    pass


class Unreachable(KinematicsError):
    pass


# ------------------------------------------------------------ forward kin.
def fk_2d(
    link_lengths: Sequence[float],
    joint_angles_rad: Sequence[float],
) -> tuple[float, float]:
    """Position of end effector of a planar chain.

    Args:
        link_lengths: positive link lengths, meters.
        joint_angles_rad: absolute angles of each link, radians.

    Returns:
        (x, y) in the same length unit.
    """
    if len(link_lengths) != len(joint_angles_rad):
        raise KinematicsError("link_lengths and joint_angles_rad must be same length")
    x = 0.0
    y = 0.0
    for L, theta in zip(link_lengths, joint_angles_rad):
        x += L * math.cos(theta)
        y += L * math.sin(theta)
    return x, y


def fk_2d_relative(
    link_lengths: Sequence[float],
    joint_angles_rel_rad: Sequence[float],
) -> tuple[float, float]:
    """FK where joint angles are relative to the previous link.

    First joint angle is absolute; each subsequent angle adds to the previous.
    """
    if len(link_lengths) != len(joint_angles_rel_rad):
        raise KinematicsError("link_lengths and joint_angles_rel_rad must be same length")
    cumulative: list[float] = []
    acc = 0.0
    for a in joint_angles_rel_rad:
        acc += a
        cumulative.append(acc)
    return fk_2d(link_lengths, cumulative)


def fk_3d_from_planar(
    link_lengths: Sequence[float],
    joint_angles_rad: Sequence[float],
    *,
    base_yaw_rad: float = 0.0,
) -> tuple[float, float, float]:
    """Planar chain rotated about the vertical axis by base_yaw_rad.

    Useful for a simple 3-DOF arm (base yaw + 2R planar).
    Returns (x, y, z). z is 0 for a purely planar chain.
    """
    x2, y2 = fk_2d(link_lengths, joint_angles_rad)
    c = math.cos(base_yaw_rad)
    s = math.sin(base_yaw_rad)
    return x2 * c, x2 * s, y2


# ------------------------------------------------------------ inverse kin.
@dataclass(frozen=True, slots=True)
class IK2Solution:
    theta1_rad: float
    theta2_rad: float
    elbow: str  # "up" | "down"


def workspace_2link(L1: float, L2: float) -> tuple[float, float]:
    """(min_reach, max_reach) for a 2-link arm."""
    if L1 <= 0 or L2 <= 0:
        raise KinematicsError("link lengths must be positive")
    return abs(L1 - L2), L1 + L2


def ik_2d_2link(
    x: float,
    y: float,
    L1: float,
    L2: float,
) -> tuple[IK2Solution, IK2Solution]:
    """Closed-form IK for a 2-link planar arm.

    Returns (elbow_up, elbow_down). Both are valid; caller picks.
    Raises Unreachable if the target is outside the workspace.
    """
    if L1 <= 0 or L2 <= 0:
        raise KinematicsError("link lengths must be positive")

    r2 = x * x + y * y
    r = math.sqrt(r2)
    r_min, r_max = workspace_2link(L1, L2)

    # epsilon tolerance for boundary cases
    eps = 1e-9
    if r > r_max + eps:
        raise Unreachable(f"target r={r:.6f} exceeds max reach {r_max:.6f}")
    if r < r_min - eps:
        raise Unreachable(f"target r={r:.6f} inside min reach {r_min:.6f}")

    cos_t2 = (r2 - L1 * L1 - L2 * L2) / (2.0 * L1 * L2)
    cos_t2 = max(-1.0, min(1.0, cos_t2))

    # elbow-down: theta2 positive; elbow-up: theta2 negative
    t2_down = math.acos(cos_t2)
    t2_up = -t2_down

    def solve_theta1(t2: float) -> float:
        k1 = L1 + L2 * math.cos(t2)
        k2 = L2 * math.sin(t2)
        return math.atan2(y, x) - math.atan2(k2, k1)

    t1_up = solve_theta1(t2_up)
    t1_down = solve_theta1(t2_down)

    return (
        IK2Solution(theta1_rad=t1_up, theta2_rad=t2_up, elbow="up"),
        IK2Solution(theta1_rad=t1_down, theta2_rad=t2_down, elbow="down"),
    )


# -------------------------------------------------------------- jacobian
def jacobian_2d_2link(
    theta1: float,
    theta2: float,
    L1: float,
    L2: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """2x2 Jacobian of the 2-link planar arm. Rows: (dx, dy). Cols: (dθ1, dθ2)."""
    s1 = math.sin(theta1)
    c1 = math.cos(theta1)
    s12 = math.sin(theta1 + theta2)
    c12 = math.cos(theta1 + theta2)
    return (
        (-L1 * s1 - L2 * s12, -L2 * s12),
        ( L1 * c1 + L2 * c12,  L2 * c12),
    )


def jacobian_det_2d_2link(
    theta1: float,
    theta2: float,
    L1: float,
    L2: float,
) -> float:
    """Determinant of the 2-link Jacobian. Zero at singularity."""
    (a, b), (c, d) = jacobian_2d_2link(theta1, theta2, L1, L2)
    return a * d - b * c


# ----------------------------------------------------------- trajectories
def linear_interp(
    start: float,
    end: float,
    n: int,
) -> list[float]:
    """n evenly-spaced samples from start to end inclusive."""
    if n < 2:
        raise KinematicsError("n must be >= 2")
    step = (end - start) / (n - 1)
    return [start + i * step for i in range(n)]


def cubic_interp(
    start: float,
    end: float,
    n: int,
    *,
    v0: float = 0.0,
    v1: float = 0.0,
    duration: float = 1.0,
) -> list[float]:
    """Cubic Hermite interpolation. Assumes uniform time spacing."""
    if n < 2:
        raise KinematicsError("n must be >= 2")
    if duration <= 0:
        raise KinematicsError("duration must be positive")

    dt = duration / (n - 1)
    p0, p1 = start, end
    m0 = v0 * dt
    m1 = v1 * dt

    out: list[float] = []
    for i in range(n):
        t = i / (n - 1)
        t2 = t * t
        t3 = t2 * t
        h00 = 2 * t3 - 3 * t2 + 1
        h10 = t3 - 2 * t2 + t
        h01 = -2 * t3 + 3 * t2
        h11 = t3 - t2
        out.append(h00 * p0 + h10 * m0 + h01 * p1 + h11 * m1)
    return out


@dataclass(frozen=True, slots=True)
class TrapezoidalProfile:
    distance: float
    max_vel: float
    max_accel: float
    t_accel: float       # time to accelerate (equals t_decel)
    t_cruise: float      # time at max velocity (0 if triangular)
    t_total: float
    peak_vel: float      # may be < max_vel if triangular

    def sample(self, n: int) -> list[float]:
        """Return n position samples evenly spaced over t_total."""
        if n < 2:
            raise KinematicsError("n must be >= 2")
        out: list[float] = []
        for i in range(n):
            t = self.t_total * i / (n - 1)
            out.append(self._pos(t))
        return out

    def _pos(self, t: float) -> float:
        a = self.max_accel
        v = self.peak_vel
        ta = self.t_accel
        tc = self.t_cruise
        d = self.distance
        if t <= 0:
            return 0.0
        if t < ta:
            return 0.5 * a * t * t
        if t < ta + tc:
            return 0.5 * a * ta * ta + v * (t - ta)
        if t < self.t_total:
            td = t - (ta + tc)
            return (0.5 * a * ta * ta + v * tc
                    + v * td - 0.5 * a * td * td)
        return d


def trapezoidal_profile(
    distance: float,
    max_vel: float,
    max_accel: float,
) -> TrapezoidalProfile:
    """Generate a trapezoidal or triangular velocity profile for a 1D move."""
    if distance <= 0:
        raise KinematicsError("distance must be positive")
    if max_vel <= 0 or max_accel <= 0:
        raise KinematicsError("max_vel and max_accel must be positive")

    d = abs(distance)
    # distance needed to accelerate to max_vel and back to 0
    d_accel_decel = (max_vel * max_vel) / max_accel

    if d_accel_decel >= d:
        # triangular: peak velocity is reduced
        peak_v = math.sqrt(d * max_accel)
        t_accel = peak_v / max_accel
        t_cruise = 0.0
    else:
        peak_v = max_vel
        t_accel = max_vel / max_accel
        t_cruise = (d - d_accel_decel) / max_vel

    t_total = 2 * t_accel + t_cruise
    return TrapezoidalProfile(
        distance=d,
        max_vel=max_vel,
        max_accel=max_accel,
        t_accel=t_accel,
        t_cruise=t_cruise,
        t_total=t_total,
        peak_vel=peak_v,
    )


# --------------------------------------------------------------- utils
def deg2rad(deg: float) -> float:
    return deg * math.pi / 180.0


def rad2deg(rad: float) -> float:
    return rad * 180.0 / math.pi


def normalize_angle(rad: float) -> float:
    """Wrap angle to (-pi, pi]."""
    x = (rad + math.pi) % (2 * math.pi) - math.pi
    if x <= -math.pi:
        return math.pi
    return x