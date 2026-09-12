"""Electronics primitives. SI units internally."""
from __future__ import annotations

from dataclasses import dataclass


class ElectronicsError(ValueError):
    pass


# ---------------------------------------------------------------- Ohm's law
def ohm_voltage(current_A: float, resistance_ohm: float) -> float:
    """V = I · R."""
    if resistance_ohm < 0:
        raise ElectronicsError("resistance must be non-negative")
    return current_A * resistance_ohm


def ohm_current(voltage_V: float, resistance_ohm: float) -> float:
    """I = V / R."""
    if resistance_ohm <= 0:
        raise ElectronicsError("resistance must be positive")
    return voltage_V / resistance_ohm


def ohm_resistance(voltage_V: float, current_A: float) -> float:
    """R = V / I."""
    if current_A == 0:
        raise ElectronicsError("current must be non-zero")
    return voltage_V / current_A


def power(voltage_V: float, current_A: float) -> float:
    """P = V · I, watts."""
    return voltage_V * current_A


def power_resistive(current_A: float, resistance_ohm: float) -> float:
    """P = I² · R."""
    return current_A * current_A * resistance_ohm


# ---------------------------------------------------------------- PWM
def pwm_duty(high_time_s: float, period_s: float) -> float:
    """Fraction in [0, 1]."""
    if period_s <= 0:
        raise ElectronicsError("period must be positive")
    if high_time_s < 0:
        raise ElectronicsError("high_time must be non-negative")
    if high_time_s > period_s:
        raise ElectronicsError("high_time cannot exceed period")
    return high_time_s / period_s


def pwm_avg_voltage(supply_V: float, duty: float) -> float:
    """Average voltage of a PWM signal."""
    if not (0.0 <= duty <= 1.0):
        raise ElectronicsError("duty must be in [0, 1]")
    return supply_V * duty


# ---------------------------------------------------------- battery life
def battery_life_hours(
    capacity_mAh: float,
    load_current_mA: float,
    *,
    efficiency: float = 1.0,
    usable_fraction: float = 1.0,
) -> float:
    """Ideal battery life in hours.

    capacity_mAh: rated capacity
    load_current_mA: average draw
    efficiency: converter efficiency (1.0 for direct)
    usable_fraction: portion of capacity safely usable (e.g. 0.8 for LiPo)
    """
    if capacity_mAh <= 0:
        raise ElectronicsError("capacity must be positive")
    if load_current_mA <= 0:
        raise ElectronicsError("load current must be positive")
    if not (0.0 < efficiency <= 1.0):
        raise ElectronicsError("efficiency must be in (0, 1]")
    if not (0.0 < usable_fraction <= 1.0):
        raise ElectronicsError("usable_fraction must be in (0, 1]")
    return capacity_mAh * usable_fraction * efficiency / load_current_mA


# ------------------------------------------------------ motor current
def motor_current_from_torque(
    torque_Nm: float,
    torque_constant_Nm_per_A: float,
) -> float:
    """I = τ / Kt, where Kt is the motor torque constant (N·m per A)."""
    if torque_constant_Nm_per_A <= 0:
        raise ElectronicsError("torque constant must be positive")
    return torque_Nm / torque_constant_Nm_per_A


def motor_torque_from_current(
    current_A: float,
    torque_constant_Nm_per_A: float,
) -> float:
    """τ = Kt · I."""
    return current_A * torque_constant_Nm_per_A


def back_emf(
    speed_rad_s: float,
    back_emf_constant_Vs_per_rad: float,
) -> float:
    """V_bemf = Ke · ω."""
    return speed_rad_s * back_emf_constant_Vs_per_rad


# ----------------------------------------------------- voltage dividers
def voltage_divider(vin_V: float, r1_ohm: float, r2_ohm: float) -> float:
    """Vout = Vin · R2 / (R1 + R2)."""
    if r1_ohm < 0 or r2_ohm < 0:
        raise ElectronicsError("resistances must be non-negative")
    denom = r1_ohm + r2_ohm
    if denom == 0:
        raise ElectronicsError("R1 + R2 must be positive")
    return vin_V * r2_ohm / denom


def led_series_resistor(
    supply_V: float,
    forward_V: float,
    forward_mA: float,
) -> float:
    """R = (Vsupply - Vf) / If, ohms. Returns 0 if supply ≤ Vf."""
    if forward_mA <= 0:
        raise ElectronicsError("forward current must be positive")
    if supply_V <= forward_V:
        raise ElectronicsError("supply must exceed LED forward voltage")
    return (supply_V - forward_V) / (forward_mA / 1000.0)


# ----------------------------------------------------- power budget
@dataclass(frozen=True, slots=True)
class PowerBudget:
    components: tuple[tuple[str, float], ...]  # (name, current_mA)
    total_mA: float
    peak_mA: float
    recommended_supply_mA: float


def power_budget(
    components: list[tuple[str, float]],
    *,
    peak_multiplier: float = 1.5,
    safety_margin: float = 1.2,
) -> PowerBudget:
    """Total current for a set of components, plus recommended supply size.

    peak_multiplier: account for inrush / stall current.
    safety_margin: extra headroom on the supply.
    """
    total = sum(max(0.0, c) for _, c in components)
    peak = total * peak_multiplier
    return PowerBudget(
        components=tuple(components),
        total_mA=total,
        peak_mA=peak,
        recommended_supply_mA=peak * safety_margin,
    )