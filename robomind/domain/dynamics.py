"""Rigid-body dynamics for serial arms. SI units internally.

Conventions:
  * Mass in kg, length in m, torque in N·m, angular accel in rad/s².
  * g = 9.80665 m/s².
  * Gravity torque uses the horizontal projection of the arm.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

G = 9.80665  # m/s²


class DynamicsError(ValueError):
    pass


# ----------------------------------------------------------- basic torque
def torque_from_force(force_N: float, lever_arm_m: float) -> float:
    """τ = F × r. Force perpendicular to lever arm."""
    if lever_arm_m < 0:
        raise DynamicsError("lever arm must be non-negative")
    return force_N * lever_arm_m


def gravity_torque(
    mass_kg: float,
    com_distance_m: float,
    *,
    angle_rad: float = 0.0,
) -> float:
    """Gravity torque about a joint.

    τ = m · g · r · cos(angle), where angle is measured from horizontal.
    At angle=0 (link horizontal), torque is maximum.
    At angle=π/2 (link vertical, up), torque is zero.
    """
    if mass_kg < 0:
        raise DynamicsError("mass must be non-negative")
    if com_distance_m < 0:
        raise DynamicsError("com_distance must be non-negative")
    return mass_kg * G * com_distance_m * math.cos(angle_rad)


def inertial_torque(inertia_kgm2: float, angular_accel_rad_s2: float) -> float:
    """τ = J · α."""
    if inertia_kgm2 < 0:
        raise DynamicsError("inertia must be non-negative")
    return inertia_kgm2 * angular_accel_rad_s2


def friction_torque(
    normal_force_N: float,
    friction_coeff: float,
    contact_radius_m: float,
) -> float:
    """Coulomb friction torque at a joint/bearing."""
    if friction_coeff < 0:
        raise DynamicsError("friction coefficient must be non-negative")
    return friction_coeff * normal_force_N * contact_radius_m


# ------------------------------------------------------------- inertia
@dataclass(frozen=True, slots=True)
class RodInertia:
    point_mass_end: float
    point_mass_center: float
    uniform_rod_end: float


def rod_inertia(mass_kg: float, length_m: float) -> RodInertia:
    """Inertia of a uniform rod about three standard axes.

    point_mass_end:    m · L²         (mass concentrated at tip)
    point_mass_center: 0
    uniform_rod_end:   m · L² / 3     (uniform rod pivoted at one end)
    """
    if mass_kg < 0 or length_m < 0:
        raise DynamicsError("mass and length must be non-negative")
    return RodInertia(
        point_mass_end=mass_kg * length_m * length_m,
        point_mass_center=0.0,
        uniform_rod_end=mass_kg * length_m * length_m / 3.0,
    )


def parallel_axis(inertia_com_kgm2: float, mass_kg: float, distance_m: float) -> float:
    """Parallel axis theorem: J = J_com + m · d²."""
    return inertia_com_kgm2 + mass_kg * distance_m * distance_m


# ---------------------------------------------------------------- gears
def gear_output_torque(
    input_torque_Nm: float,
    ratio: float,
    *,
    efficiency: float = 1.0,
) -> float:
    """τ_out = τ_in · ratio · η. ratio > 1 means torque increase."""
    if ratio <= 0:
        raise DynamicsError("gear ratio must be positive")
    if not (0.0 < efficiency <= 1.0):
        raise DynamicsError("efficiency must be in (0, 1]")
    return input_torque_Nm * ratio * efficiency


def gear_output_speed(input_speed_rad_s: float, ratio: float) -> float:
    """ω_out = ω_in / ratio."""
    if ratio <= 0:
        raise DynamicsError("gear ratio must be positive")
    return input_speed_rad_s / ratio


def reflected_inertia(load_inertia_kgm2: float, ratio: float) -> float:
    """J_reflected = J_load / ratio²."""
    if ratio <= 0:
        raise DynamicsError("gear ratio must be positive")
    return load_inertia_kgm2 / (ratio * ratio)


# ----------------------------------------------------- total requirement
@dataclass(frozen=True, slots=True)
class TorqueRequirement:
    gravity: float
    inertial: float
    friction: float
    total: float
    safety_margin: float
    required_with_margin: float


def required_joint_torque(
    *,
    mass_kg: float,
    com_distance_m: float,
    angle_rad: float = 0.0,
    inertia_kgm2: float = 0.0,
    angular_accel_rad_s2: float = 0.0,
    normal_force_N: float = 0.0,
    friction_coeff: float = 0.0,
    contact_radius_m: float = 0.0,
    safety_margin: float = 1.5,
) -> TorqueRequirement:
    """Sum the three torque components and apply a safety margin."""
    if safety_margin < 1.0:
        raise DynamicsError("safety_margin must be >= 1.0")
    tg = gravity_torque(mass_kg, com_distance_m, angle_rad=angle_rad)
    ti = inertial_torque(inertia_kgm2, angular_accel_rad_s2)
    tf = friction_torque(normal_force_N, friction_coeff, contact_radius_m)
    total = tg + ti + tf
    return TorqueRequirement(
        gravity=tg, inertial=ti, friction=tf,
        total=total,
        safety_margin=safety_margin,
        required_with_margin=total * safety_margin,
    )