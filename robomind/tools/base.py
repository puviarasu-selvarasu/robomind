"""Tool base class. Every tool subclasses this."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Literal

from ..core.models import ToolResult


SafetyClass = Literal["read", "compute", "write", "hardware"]


class BaseTool(ABC):
    name: str = ""
    description: str = ""
    args_schema: dict[str, Any] = {}
    output_schema: dict[str, Any] = {}
    safety_class: SafetyClass = "compute"

    @abstractmethod
    def run(self, **kwargs: Any) -> ToolResult:
        ...

    def help(self) -> str:
        lines = [f"{self.name} — {self.description}",
                 f"safety: {self.safety_class}"]
        if self.args_schema:
            lines.append("args:")
            for k, v in self.args_schema.items():
                lines.append(f"  {k}: {v}")
        return "\n".join(lines)