"""Compact banner and full boot sequence."""
from __future__ import annotations

import sys
import time
from typing import Iterable

from . import ansi

_WORDMARK = r"""
 ____   ___  ____   ___  __  __ ___ _   _ ____
|  _ \ / _ \| __ ) / _ \|  \/  |_ _| \ | |  _ \
| |_) | | | |  _ \| | | | |\/| || ||  \| | | | |
|  _ <| |_| | |_) | |_| | |  | || || |\  | |_| |
|_| \_\\___/|____/ \___/|_|  |_|___|_| \_|____/
""".strip("\n").splitlines()


def wordmark() -> list[str]:
    return list(_WORDMARK)


def compact(version: str, *, color: str = ansi.FG_CYAN) -> str:
    line = f"◤ ROBOMIND {version} ◢"
    return f"{ansi.BOLD}{color}{line}{ansi.RESET}"


def full_boot(
    version: str,
    *,
    write=None,
    delay_ms: int = 25,
    stages: Iterable[str] = (
        "loading config",
        "opening memory",
        "registering tools",
        "wiring ports",
        "ready",
    ),
) -> None:
    """Print the full boot sequence. Uses typewriter effect; skip on keypress."""
    write = write or (lambda s: sys.stdout.write(s) or sys.stdout.flush())

    write(ansi.CLEAR_SCREEN + ansi.CURSOR_HOME)
    for line in _WORDMARK:
        write(f"{ansi.BOLD}{ansi.FG_CYAN}{line}{ansi.RESET}\n")
    write(f"{ansi.DIM}  offline robotics engineer · {version}{ansi.RESET}\n\n")

    for stage in stages:
        _type_line(f"  {ansi.FG_GREEN}✓{ansi.RESET} {stage}", delay_ms, write)
        write("\n")
    write("\n")


def _type_line(text: str, delay_ms: int, write) -> None:
    for ch in text:
        write(ch)
        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)
        if _key_pressed():
            write(text[len(text) - len(text):])  # flush rest instantly
            return


def _key_pressed() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import msvcrt
        return msvcrt.kbhit()
    except Exception:
        return False