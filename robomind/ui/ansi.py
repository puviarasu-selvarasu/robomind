"""ANSI escapes and terminal helpers. Tier A: stdlib only."""
from __future__ import annotations

import os
import re
import sys

ESC = "\x1b"
CSI = f"{ESC}["
RESET = f"{CSI}0m"
BOLD = f"{CSI}1m"
DIM = f"{CSI}2m"
UNDERLINE = f"{CSI}4m"

FG_BLACK = f"{CSI}30m"
FG_RED = f"{CSI}31m"
FG_GREEN = f"{CSI}32m"
FG_YELLOW = f"{CSI}33m"
FG_BLUE = f"{CSI}34m"
FG_MAGENTA = f"{CSI}35m"
FG_CYAN = f"{CSI}36m"
FG_WHITE = f"{CSI}37m"
FG_BRIGHT_CYAN = f"{CSI}96m"
FG_BRIGHT_WHITE = f"{CSI}97m"

CLEAR_SCREEN = f"{CSI}2J"
CURSOR_HOME = f"{CSI}H"
CURSOR_HIDE = f"{CSI}?25l"
CURSOR_SHOW = f"{CSI}?25h"

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def enable_vt() -> None:
    """Enable ANSI processing on Windows. No-op on POSIX."""
    if sys.platform == "win32":
        try:
            os.system("")
        except Exception:
            pass


def is_windows_terminal() -> bool:
    return bool(os.environ.get("WT_SESSION"))


def supports_truecolor() -> bool:
    return os.environ.get("COLORTERM", "").lower() in ("truecolor", "24bit")


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def visible_len(text: str) -> int:
    return len(strip_ansi(text))