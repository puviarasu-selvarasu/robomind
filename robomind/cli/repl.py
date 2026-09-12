"""RoboMind REPL. cmd.Cmd subclass with retro UI and stub commands."""
from __future__ import annotations

import cmd
import shlex

from . import commands as C
from .commands import Context, STUB_COMMANDS


class RoboMindREPL(cmd.Cmd):
    intro = ""

    def __init__(self, ctx: Context) -> None:
        super().__init__()
        self.ctx = ctx
        self.prompt = "robomind> "

    # --------------------------------------------------------- dispatch
    def default(self, line: str) -> None:
        name = line.split(maxsplit=1)[0] if line else ""
        if name in STUB_COMMANDS:
            C.cmd_stub(self.ctx, name)
        else:
            self.ctx.renderer.error(f"unknown command: {name!r}. Try 'help'.")

    def emptyline(self) -> None:
        pass

    # --------------------------------------------------------- builtins
    def do_help(self, arg: str) -> None:
        if arg:
            method = getattr(self, f"do_{arg}", None)
            if method and method.__doc__:
                self.ctx.renderer.info(method.__doc__.strip())
            else:
                self.ctx.renderer.error(f"no such command: {arg}")
            return

        lines = [
            "ask <text>              — ask RoboMind a robotics question      (Phase 4)",
            "ik <x> <y> [z]          — inverse kinematics                    (Phase 4)",
            "fk <angles...>          — forward kinematics                    (Phase 4)",
            "learn <topic> | <fact>  — store a fact                          (Phase 1)",
            "recall <query>          — search memory                         (Phase 1)",
            "datasheet <part>        — look up a component                   (Phase 4)",
            "codegen <target> <spec> — generate code                         (Phase 3)",
            "why [id|last]           — explain last decision                 (Phase 5)",
            "stats [what]            — rule/fact/episode stats               (Phase 5)",
            "config list             — show resolved configuration",
            "tools list              — list registered tools",
            "version                 — show version",
            "clear                   — clear screen",
            "boot                    — replay boot sequence",
            "quit / exit             — leave the REPL",
        ]
        self.ctx.renderer.result("commands", lines)

    def do_quit(self, arg: str) -> bool:
        """Exit the REPL."""
        self.ctx.renderer.info("bye.")
        return True

    def do_exit(self, arg: str) -> bool:
        """Exit the REPL."""
        return self.do_quit(arg)

    def do_EOF(self, arg: str) -> bool:
        return self.do_quit(arg)

    def do_clear(self, arg: str) -> None:
        """Clear screen."""
        self.ctx.renderer.clear()

    def do_version(self, arg: str) -> None:
        """Print version."""
        C.cmd_version(self.ctx)

    def do_config(self, arg: str) -> None:
        """config list — show resolved configuration."""
        C.cmd_config(self.ctx, shlex.split(arg))

    def do_tools(self, arg: str) -> None:
        """tools list | tools help <name>"""
        C.cmd_tools(self.ctx, shlex.split(arg))

    def do_boot(self, arg: str) -> None:
        """Replay boot sequence (compact)."""
        self.ctx.renderer.banner(compact=True)