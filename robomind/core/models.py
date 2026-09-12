"""Immutable dataclasses shared across all layers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Intent:
    name: str
    entities: dict[str, Any] = field(default_factory=dict)
    raw: str = ""
    confidence: float = 1.0


@dataclass(frozen=True, slots=True)
class Step:
    id: str
    tool: str
    args: dict[str, Any] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()
    safety_class: str = "compute"


@dataclass(frozen=True, slots=True)
class Plan:
    id: str
    intent: Intent
    steps: tuple[Step, ...] = ()
    rationale: str = ""
    rule_ids: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class ToolResult:
    step_id: str
    ok: bool
    value: Any = None
    error: str | None = None
    duration_ms: int = 0


@dataclass(frozen=True, slots=True)
class ActionResult:
    plan_id: str
    results: tuple[ToolResult, ...] = ()
    ok: bool = False
    summary: str = ""


@dataclass(frozen=True, slots=True)
class ValidationResult:
    ok: bool
    score: float = 0.0
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Fact:
    topic: str
    fact: str
    tags: tuple[str, ...] = ()
    confidence: float = 1.0
    id: int | None = None
    created_at: str | None = None
    updated_at: str | None = None


@dataclass(frozen=True, slots=True)
class Rule:
    name: str
    when: dict[str, Any]
    then: dict[str, Any]
    version: int = 1
    weight: float = 1.0
    hits: int = 0
    wins: int = 0
    id: int | None = None
    last_fired_at: str | None = None
    created_at: str | None = None


@dataclass(frozen=True, slots=True)
class Episode:
    input: str
    intent: str | None = None
    plan_json: str | None = None
    actions_json: str | None = None
    result_json: str | None = None
    success: bool | None = None
    score: float | None = None
    duration_ms: int | None = None
    id: int | None = None
    created_at: str | None = None