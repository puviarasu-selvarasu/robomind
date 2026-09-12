"""Entry point: ``python -m robomind``."""
from __future__ import annotations

import argparse
import logging
import sys

from . import __version__
from .cli.commands import Context
from .cli.repl import RoboMindREPL
from .config import build_config
from .deps import ollama_available, tier_b_available
from .llm.null_llm import NullLLM
from .logging_setup import setup_logging
from .memory.store import SQLiteMemoryStore
from .tools.registry import ToolRegistry
from .ui.plain import PlainRenderer
from .ui.retro import RetroRenderer
from .ui.voice.null_voice import NullVoice


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="robomind",
                                description="Offline retro-futuristic robotics AI.")
    p.add_argument("--home", type=str, default=None)
    p.add_argument("--db", type=str, default=None)

    p.add_argument("--voice", choices=("on", "off"), default=None)
    p.add_argument("--voice-engine", choices=("sapi", "piper", "espeak"), default=None)
    p.add_argument("--voice-rate", type=int, default=None)

    p.add_argument("--face", choices=("on", "off"), default=None)
    p.add_argument("--face-size", type=str, default=None)
    p.add_argument("--face-palette", choices=("cyan", "amber", "green", "rgb"), default=None)

    p.add_argument("--llm", choices=("on", "off"), default=None)
    p.add_argument("--llm-model", type=str, default=None)
    p.add_argument("--llm-ctx", type=int, default=None)

    p.add_argument("--retro", choices=("on", "off"), default=None)
    p.add_argument("--sound", choices=("on", "off"), default=None)
    p.add_argument("--dry-run", action="store_true", default=None)
    p.add_argument("--verbose", action="store_true", default=None)
    p.add_argument("--boot", action="store_true", default=None)

    p.add_argument("--version", action="version", version=f"robomind {__version__}")
    return p


def _parse_cli(argv: list[str]) -> dict:
    ns = _build_parser().parse_args(argv)
    return {k: v for k, v in vars(ns).items() if v is not None}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    cli = _parse_cli(argv)
    cfg = build_config(cli)

    errors = cfg.validate()
    if errors:
        for e in errors:
            print(f"config error: {e}", file=sys.stderr)
        return 2

    log_file = setup_logging(cfg.log_dir, cfg.log_level, console=cfg.verbose)
    log = logging.getLogger("robomind")
    log.info("robomind starting", extra={"version": __version__, "home": str(cfg.home)})

    # Renderer
    if cfg.retro == "on":
        renderer = RetroRenderer(color=_palette_to_code(cfg.face_palette))
    else:
        renderer = PlainRenderer()

    # Memory
    try:
        store = SQLiteMemoryStore(cfg.db)
    except Exception as exc:
        log.exception("failed to open memory store")
        renderer.error(f"could not open memory store: {exc}")
        return 1

    # Ports
    llm = NullLLM()                # Phase 6 replaces with Ollama adapter
    voice = NullVoice()            # Phase 6.5 replaces with SAPI adapter
    tools = ToolRegistry(dry_run=bool(cfg.dry_run))
    _register_tools(tools, store)

    # Dependency report
    tb = tier_b_available()
    loaded = [k for k, v in tb.items() if v]

    # Banner
    if cfg.boot:
        from .ui.banner import full_boot
        full_boot(__version__)
    renderer.banner(compact=True)

    if loaded and cfg.verbose:
        renderer.info(f"tier B: {', '.join(loaded)}")
    if cfg.llm == "on" and not ollama_available(cfg.ollama_url):
        renderer.warn("llm=on but Ollama is not reachable — falling back to NullLLM")

    ctx = Context(config=cfg, store=store, renderer=renderer,
                  tools=tools, llm=llm, voice=voice)

    repl = RoboMindREPL(ctx)
    try:
        repl.cmdloop()
    except KeyboardInterrupt:
        renderer.info("\ninterrupted.")
    finally:
        store.close()
        llm.close()
        log.info("robomind stopped cleanly")
    return 0

def _register_tools(tools, store) -> None:
    from .tools.calculator_tool import CalculatorTool
    from .tools.cad_tool import CADTool
    from .tools.codegen_tool import CodegenTool
    from .tools.datasheet_tool import DatasheetTool
    from .tools.diagnose_tool import DiagnoseTool
    from .tools.fk_tool import FKTool
    from .tools.ik_tool import IKTool
    from .tools.memory_tool import MemoryTool
    from .tools.trajectory_tool import TrajectoryTool
    from .tools.units_tool import UnitsTool

    tools.register(CalculatorTool())
    tools.register(UnitsTool())
    tools.register(FKTool())
    tools.register(IKTool())
    tools.register(TrajectoryTool())
    tools.register(DatasheetTool())
    tools.register(DiagnoseTool())
    tools.register(CADTool())
    tools.register(CodegenTool())
    tools.register(MemoryTool(store))

def _palette_to_code(name: str) -> str:
    from .ui import ansi
    return {
        "cyan":  ansi.FG_CYAN,
        "amber": ansi.FG_YELLOW,
        "green": ansi.FG_GREEN,
        "rgb":   ansi.FG_BRIGHT_CYAN,
    }.get(name, ansi.FG_CYAN)


if __name__ == "__main__":
    raise SystemExit(main())