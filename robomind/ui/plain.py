"""Plain renderer: no ANSI, no boxes. Single-stream stdout."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator


class PlainRenderer:
    def banner(self, compact: bool = True) -> None:
        from .. import __version__
        print(f"RoboMind {__version__}")

    @contextmanager
    def stage(self, name: str) -> Iterator[None]:
        print(f"... {name}")
        try:
            yield
        finally:
            print(f"ok  {name}")

    def info(self, msg: str) -> None:
        print(msg)

    def warn(self, msg: str) -> None:
        print(f"WARN: {msg}")

    def error(self, msg: str) -> None:
        print(f"ERROR: {msg}")

    def success(self, msg: str) -> None:
        print(msg)

    def result(self, title: str, lines: list[str]) -> None:
        print(f"--- {title} ---")
        for ln in lines:
            print(ln)
        print("---")

    def clear(self) -> None:
        pass