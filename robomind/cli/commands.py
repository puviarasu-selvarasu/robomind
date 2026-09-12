"""Command handlers. Called from the REPL."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .. import __version__


@dataclass
class Context:
    config: Any
    store: Any
    renderer: Any
    tools: Any
    llm: Any
    voice: Any


STUB_COMMANDS = {
    "ask": 4, "ik": 4, "fk": 4, "traj": 4, "diagnose": 4, "datasheet": 4,
    "cad": 3, "codegen": 3,
    "learn": 1, "recall": 1,
    "correct": 5, "why": 5, "stats": 5,
    "export": 7, "reset": 7, "history": 7, "sound": 7,
    "voice": "6.5", "face": "6.5", "say": "6.5",
}


def cmd_version(ctx: Context) -> None:
    ctx.renderer.info(f"RoboMind {__version__}")


def cmd_config(ctx: Context, args: list[str]) -> None:
    c = ctx.config
    if args and args[0] == "list":
        lines = [
            f"home          : {c.home}",
            f"db            : {c.db}",
            f"log_dir       : {c.log_dir}",
            f"ollama_url    : {c.ollama_url}",
            f"llm_model     : {c.llm_model}",
            f"llm           : {c.llm}",
            f"voice         : {c.voice}",
            f"face          : {c.face}",
            f"face_size     : {c.face_size}",
            f"face_palette  : {c.face_palette}",
            f"retro         : {c.retro}",
            f"sound         : {c.sound}",
            f"dry_run       : {c.dry_run}",
            f"log_level     : {c.log_level}",
        ]
        ctx.renderer.result("config", lines)
    else:
        ctx.renderer.info("usage: config list")


def cmd_tools(ctx: Context, args: list[str]) -> None:
    names = ctx.tools.list()
    if not args or args[0] == "list":
        if not names:
            ctx.renderer.info("No tools registered (Phase 0).")
        else:
            ctx.renderer.result("tools", names)
    elif args[0] == "help" and len(args) >= 2:
        tool = ctx.tools.get(args[1])
        if tool is None:
            ctx.renderer.error(f"no such tool: {args[1]}")
        else:
            ctx.renderer.info(tool.help())
    else:
        ctx.renderer.info("usage: tools list | tools help <name>")


def cmd_stub(ctx: Context, name: str) -> None:
    phase = STUB_COMMANDS.get(name, "?")
    ctx.renderer.warn(f"'{name}' is not yet implemented (Phase {phase}).")