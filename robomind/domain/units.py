"""Unit conversion and small dimensional quantities.

Design:
  * Every category has a base SI unit (or SI-compatible: N·m for torque).
  * Conversions are pure functions with a lookup table.
  * Quantity is a frozen dataclass with arithmetic limited to:
      - add/sub within the same category
      - mul/div by scalar
      - to() conversion
  * No full dimensional analysis (no derived units tracking). Keep it simple.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Category = Literal[
    "length", "mass", "time", "angle",
    "force", "torque", "voltage", "current",
]

_CONVERSIONS: dict[str, dict[str, float]] = {
    "length": {
        "m": 1.0, "mm": 0.001, "cm": 0.01, "km": 1000.0,
        "in": 0.0254, "ft": 0.3048, "mil": 0.0000254, "um": 0.000001,
    },
    "mass": {
        "kg": 1.0, "g": 0.001, "mg": 0.000001,
        "lb": 0.45359237, "oz": 0.028349523125,
    },
    "time": {
        "s": 1.0, "ms": 0.001, "us": 0.000001, "ns": 0.000000001,
        "min": 60.0, "hr": 3600.0,
    },
    "angle": {
        "rad": 1.0,
        "deg": 0.017453292519943295,
        "grad": 0.015707963267948967,
        "turn": 6.283185307179586,
    },
    "force": {
        "N": 1.0, "kN": 1000.0, "mN": 0.001,
        "lbf": 4.4482216152605,
        "kgf": 9.80665,
        "dyn": 0.00001,
    },
    "torque": {
        # base: N·m
        "Nm": 1.0,
        "Nmm": 0.001,
        "Ncm": 0.01,
        "kgcm": 0.0980665,       # 1 kgf·cm
        "kgm": 9.80665,          # 1 kgf·m
        "ozin": 0.007061551833333333,
        "lbin": 0.11298482902777778,
        "lbf": 4.4482216152605,  # placeholder — see note below
    },
    "voltage": {"V": 1.0, "mV": 0.001, "kV": 1000.0, "uV": 0.000001},
    "current": {"A": 1.0, "mA": 0.001, "uA": 0.000001},
}


def _find_category(unit: str) -> str | None:
    for cat, table in _CONVERSIONS.items():
        if unit in table:
            return cat
    return None


def known_units() -> dict[str, tuple[str, ...]]:
    """Return category -> tuple of unit names."""
    return {cat: tuple(sorted(t.keys())) for cat, t in _CONVERSIONS.items()}


def category_of(unit: str) -> str | None:
    return _find_category(unit)


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert value from one unit to another. Raises ValueError on mismatch."""
    if from_unit == to_unit:
        return float(value)
    cat_f = _find_category(from_unit)
    cat_t = _find_category(to_unit)
    if cat_f is None:
        raise ValueError(f"unknown unit: {from_unit!r}")
    if cat_t is None:
        raise ValueError(f"unknown unit: {to_unit!r}")
    if cat_f != cat_t:
        raise ValueError(
            f"incompatible units: {from_unit!r} is {cat_f}, {to_unit!r} is {cat_t}"
        )
    base = float(value) * _CONVERSIONS[cat_f][from_unit]
    return base / _CONVERSIONS[cat_t][to_unit]


@dataclass(frozen=True, slots=True)
class Quantity:
    value: float
    unit: str

    # -------------------------------------------------------------- helpers
    @property
    def category(self) -> str | None:
        return _find_category(self.unit)

    def to(self, unit: str) -> "Quantity":
        return Quantity(convert(self.value, self.unit, unit), unit)

    def __add__(self, other: "Quantity") -> "Quantity":
        if not isinstance(other, Quantity):
            return NotImplemented
        if self.category != other.category:
            raise ValueError(f"cannot add {self.unit} and {other.unit}")
        return Quantity(self.value + other.to(self.unit).value, self.unit)

    def __sub__(self, other: "Quantity") -> "Quantity":
        if not isinstance(other, Quantity):
            return NotImplemented
        if self.category != other.category:
            raise ValueError(f"cannot subtract {self.unit} and {other.unit}")
        return Quantity(self.value - other.to(self.unit).value, self.unit)

    def __mul__(self, scalar: float) -> "Quantity":
        return Quantity(self.value * float(scalar), self.unit)

    __rmul__ = __mul__

    def __truediv__(self, scalar: float) -> "Quantity":
        return Quantity(self.value / float(scalar), self.unit)

    def __neg__(self) -> "Quantity":
        return Quantity(-self.value, self.unit)

    def __repr__(self) -> str:
        return f"Quantity({self.value}, {self.unit!r})"