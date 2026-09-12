"""Simple fault diagnosis via keyword matching against a curated fault tree.

Phase 3 knowledge base is intentionally small. Phase 8 expands it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..core.models import ToolResult
from .base import BaseTool


@dataclass(frozen=True, slots=True)
class Fault:
    id: str
    keywords: tuple[str, ...]
    symptom: str
    causes: tuple[str, ...]
    checks: tuple[str, ...]


_FAULTS: tuple[Fault, ...] = (
    Fault(
        id="servo.jitter",
        keywords=("jitter", "shaking", "twitching", "unstable", "vibrate"),
        symptom="Servo jitters or twitches without a command.",
        causes=(
            "Shared power rail with MCU logic (brownout)",
            "Insufficient current supply",
            "PWM signal noise or wrong pulse range",
            "Mechanical binding or overload",
        ),
        checks=(
            "Power the servo from a separate 5-6V rail with common ground.",
            "Measure supply voltage under load with an oscilloscope or multimeter.",
            "Verify PWM pulse width is 500–2500 µs at 50 Hz.",
            "Disconnect horn and re-test — rule out mechanical binding.",
        ),
    ),
    Fault(
        id="servo.no_motion",
        keywords=("no motion", "not moving", "dead servo", "silent",
                  "won't move", "will not move"),
        symptom="Servo does not move at all.",
        causes=(
            "No power to servo rail",
            "PWM signal not reaching servo",
            "Servo damaged (burnt coil, stripped gear)",
            "Wrong wiring (signal vs power)",
        ),
        checks=(
            "Confirm 5–6V on the servo power pins with a multimeter.",
            "Verify PWM output with a logic analyzer or scope.",
            "Swap in a known-good servo to isolate.",
            "Check current draw — a stalled burnt servo often draws ~0 or full stall.",
        ),
    ),
    Fault(
        id="motor.overheat",
        keywords=("hot motor", "overheat", "burning", "very hot", "too warm"),
        symptom="Motor or driver runs hot.",
        causes=(
            "Continuous stall current",
            "Over-voltage",
            "Insufficient cooling / enclosed space",
            "Wrong motor driver current limit",
        ),
        checks=(
            "Reduce load or duty cycle.",
            "Verify supply voltage against datasheet max.",
            "Add airflow or heatsink.",
            "Set driver current limit per motor spec.",
        ),
    ),
    Fault(
        id="power.brownout",
        keywords=("brownout", "reset", "restart", "reboot", "mcu reset",
                  "unexpected reset"),
        symptom="MCU resets or brownouts when actuators move.",
        causes=(
            "Supply sag from inrush current",
            "Shared rail between MCU and motors",
            "Undersized regulator or battery",
            "Missing decoupling capacitors",
        ),
        checks=(
            "Split rails: dedicated supply for motors, linear reg for MCU.",
            "Add 100–470 µF electrolytic near motor driver VIN.",
            "Add 100 nF ceramic near MCU VCC.",
            "Measure battery voltage during motion.",
        ),
    ),
    Fault(
        id="comm.i2c_fail",
        keywords=("i2c", "i2c fail", "no sensor", "sensor not found",
                  "bus error"),
        symptom="I2C device not detected or bus errors.",
        causes=(
            "Missing or wrong pull-up resistors",
            "Wrong address",
            "Wiring / solder joint",
            "Voltage level mismatch (3.3V vs 5V device)",
        ),
        checks=(
            "Run an I2C scan sketch.",
            "Verify 4.7 kΩ pull-ups to the bus voltage.",
            "Check address against datasheet.",
            "Confirm voltage levels match between MCU and device.",
        ),
    ),
    Fault(
        id="reach.unreachable",
        keywords=("unreachable", "out of reach", "can't reach", "cannot reach"),
        symptom="Target pose is outside the arm's reachable workspace.",
        causes=(
            "Target beyond max reach (L1 + L2)",
            "Target inside min reach (|L1 − L2|)",
            "Joint limits prevent the required pose",
        ),
        checks=(
            "Compute r = sqrt(x² + y²) and compare against workspace.",
            "Consider moving the base or relaxing link lengths.",
            "Check joint limits — a valid IK solution may violate a limit.",
        ),
    ),
)


def _score(fault: Fault, tokens: set[str]) -> float:
    hits = sum(1 for kw in fault.keywords
               if " " in kw and kw in " ".join(tokens)
               or kw in tokens)
    return hits / max(1, len(fault.keywords))


import re

def diagnose(text: str, *, top_k: int = 3) -> list[tuple[Fault, float]]:
    """Match faults by exact token, prefix, or multi-word substring."""
    lower = text.lower()
    tokens = re.findall(r"[a-z0-9_]+", lower)
    token_set = set(tokens)

    scored: list[tuple[Fault, float]] = []
    for f in _FAULTS:
        hits = 0
        for kw in f.keywords:
            if " " in kw:
                if kw in lower:
                    hits += 1
            else:
                if kw in token_set or any(t.startswith(kw) for t in tokens):
                    hits += 1
        if hits:
            scored.append((f, hits / len(f.keywords)))
    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:top_k]


class DiagnoseTool(BaseTool):
    name = "diagnose"
    description = "Suggest causes and checks for a robotics symptom."
    safety_class = "read"

    args_schema = {
        "symptom": "str — free text description",
        "top_k": "int — number of matches (default 3)",
    }
    output_schema = {"matches": "list[{id, symptom, causes, checks, score}]"}

    def run(self, *, step_id: str = "diagnose",
            symptom: str = "", top_k: int = 3, **_: Any) -> ToolResult:
        if not symptom.strip():
            return ToolResult(step_id=step_id, ok=False,
                              error="symptom required")
        matches = diagnose(symptom, top_k=int(top_k))
        if not matches:
            return ToolResult(step_id=step_id, ok=True, value={
                "symptom": symptom,
                "matches": [],
                "note": "no known fault matched — expand the knowledge base",
            })
        return ToolResult(step_id=step_id, ok=True, value={
            "symptom": symptom,
            "matches": [
                {"id": f.id, "symptom": f.symptom,
                 "causes": list(f.causes), "checks": list(f.checks),
                 "score": round(s, 3)}
                for f, s in matches
            ],
        })