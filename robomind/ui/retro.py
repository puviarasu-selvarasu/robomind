"""Retro renderer: cyan-on-black, box drawing, stage indicators."""
from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import Iterator

from . import ansi
from .boxes import Box, render as render_box


class RetroRenderer:
    def __init__(self, *, color: str = ansi.FG_CYAN, out=None) -> None:
        self.color = color
        self.out = out or sys.stdout
        ansi.enable_vt()

    def _w(self, s: str) -> None:
        self.out.write(s)
        self.out.flush()

    def banner(self, compact: bool = True) -> None:
        from .. import __version__
        if compact:
            self._w("\n" + ansi.BOLD + self.color +
                    f"◤ ROBOMIND {__version__} ◢" +
                    ansi.RESET + "\n\n")

    @contextmanager
    def stage(self, name: str) -> Iterator[None]:
        self._w(f"{self.color}⧗{ansi.RESET} {name}... ")
        try:
            yield
        finally:
            self._w(f"{ansi.FG_GREEN}✓{ansi.RESET}\n")

    def info(self, msg: str) -> None:
        self._w(msg + "\n")

    def warn(self, msg: str) -> None:
        self._w(f"{ansi.FG_YELLOW}WARN:{ansi.RESET} {msg}\n")

    def error(self, msg: str) -> None:
        self._w(f"{ansi.FG_RED}ERROR:{ansi.RESET} {msg}\n")

    def success(self, msg: str) -> None:
        self._w(f"{ansi.FG_GREEN}{msg}{ansi.RESET}\n")

    def result(self, title: str, lines: list[str]) -> None:
        self._w(render_box(Box(title=title, lines=lines, width=64, color=self.color)) + "\n")

    def clear(self) -> None:
        self._w(ansi.CLEAR_SCREEN + ansi.CURSOR_HOME)