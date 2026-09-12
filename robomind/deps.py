"""Tier B dependency detection. Never raises; returns None/False when missing."""
from __future__ import annotations

import importlib
import urllib.request
from typing import Any


_TIER_B = ("pyttsx3", "PIL", "numpy", "numpy_stl", "cadquery", "pytest")


def try_import(name: str) -> Any | None:
    try:
        return importlib.import_module(name)
    except Exception:
        return None


def tier_b_available() -> dict[str, bool]:
    return {name: try_import(name) is not None for name in _TIER_B}


def ollama_available(url: str = "http://localhost:11434", timeout: float = 0.5) -> bool:
    try:
        with urllib.request.urlopen(f"{url}/api/tags", timeout=timeout) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False