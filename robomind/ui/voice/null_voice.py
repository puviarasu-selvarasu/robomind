"""Silent voice adapter."""
from __future__ import annotations


class NullVoice:
    def speak(self, text: str) -> None:
        pass

    def stop(self) -> None:
        pass

    def is_speaking(self) -> bool:
        return False

    def is_available(self) -> bool:
        return False