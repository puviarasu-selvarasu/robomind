"""Null LLM: silent no-op. Used when Ollama is off or unavailable."""
from __future__ import annotations


class NullLLM:
    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 256,
        temperature: float = 0.2,
    ) -> str:
        return ""

    def is_available(self) -> bool:
        return False

    def close(self) -> None:
        pass