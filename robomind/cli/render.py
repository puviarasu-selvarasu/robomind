"""Thin delegate so CLI code depends only on the renderer port."""
from __future__ import annotations

from typing import Any


def emit(renderer: Any, kind: str, *args: Any) -> None:
    fn = getattr(renderer, kind, None)
    if fn is None:
        return
    fn(*args)