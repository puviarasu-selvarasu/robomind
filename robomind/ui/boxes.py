"""Box-drawing primitives. Single write per box to avoid flicker."""
from __future__ import annotations

from dataclasses import dataclass, field

from .ansi import BOLD, FG_CYAN, RESET, visible_len

SINGLE = {"tl": "┌", "tr": "┐", "bl": "└", "br": "┘", "h": "─", "v": "│"}
DOUBLE = {"tl": "╔", "tr": "╗", "bl": "╚", "br": "╝", "h": "═", "v": "║"}
HEAVY  = {"tl": "┏", "tr": "┓", "bl": "┗", "br": "┛", "h": "━", "v": "┃"}

STYLES = {"single": SINGLE, "double": DOUBLE, "heavy": HEAVY}


@dataclass
class Box:
    title: str = ""
    lines: list[str] = field(default_factory=list)
    width: int = 60
    style: str = "single"
    color: str = FG_CYAN


def _wrap(line: str, width: int) -> list[str]:
    if visible_len(line) <= width:
        return [line]
    words = line.split(" ")
    out, cur = [], ""
    for w in words:
        candidate = f"{cur} {w}".strip()
        if visible_len(candidate) <= width:
            cur = candidate
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out or [""]


def render(box: Box) -> str:
    g = STYLES.get(box.style, SINGLE)
    inner = box.width - 2

    wrapped: list[str] = []
    for ln in box.lines:
        wrapped.extend(_wrap(ln, inner))
    if not wrapped:
        wrapped = [""]

    top: str
    if box.title:
        title = f" {box.title} "
        pad = inner - visible_len(title)
        if pad < 0:
            title = title[:inner]
            pad = 0
        top = f"{g['tl']}{g['h']}{title}{g['h'] * pad}{g['tr']}"
    else:
        top = f"{g['tl']}{g['h'] * inner}{g['tr']}"

    bottom = f"{g['bl']}{g['h'] * inner}{g['br']}"

    mid = []
    for ln in wrapped:
        pad = inner - visible_len(ln)
        mid.append(f"{g['v']} {ln}{' ' * max(0, pad - 1)}{g['v']}")

    body = "\n".join([top, *mid, bottom])
    return f"{BOLD}{box.color}{body}{RESET}"