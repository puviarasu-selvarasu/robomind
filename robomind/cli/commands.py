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
            ctx.renderer.info("No tools registered.")
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


def cmd_learn(ctx: Context, args: list[str]) -> None:
    """Usage: learn <topic> | <fact> [#tag ...]"""
    if not args:
        ctx.renderer.info("usage: learn <topic> | <fact> [#tag ...]")
        return
    raw = " ".join(args)
    if "|" not in raw:
        ctx.renderer.error("format: learn <topic> | <fact>")
        return
    topic, fact = raw.split("|", 1)
    tool = ctx.tools.get("memory")
    if tool is None:
        ctx.renderer.error("memory tool not registered")
        return
    result = tool.run(action="learn", topic=topic.strip(), fact=fact.strip())
    if not result.ok:
        ctx.renderer.error(result.error or "learn failed")
        return
    v = result.value
    tag_str = f" [{', '.join(v['tags'])}]" if v.get("tags") else ""
    ctx.renderer.success(
        f"learned #{v['id']}: {v['topic']} — {v['fact']}{tag_str}"
    )


def cmd_recall(ctx: Context, args: list[str]) -> None:
    """Usage: recall <query> [#tag ...]"""
    if not args:
        ctx.renderer.info("usage: recall <query> [#tag ...]")
        return
    raw = " ".join(args)

    # Extract #tags as filter
    tags = [w[1:] for w in raw.split() if w.startswith("#")]
    query = " ".join(w for w in raw.split() if not w.startswith("#")).strip()
    if not query and not tags:
        ctx.renderer.info("usage: recall <query> [#tag ...]")
        return

    tool = ctx.tools.get("memory")
    if tool is None:
        ctx.renderer.error("memory tool not registered")
        return
    result = tool.run(action="recall", query=query or " ".join(tags),
                      tags=tags, limit=10, include_episodes=True)
    if not result.ok:
        ctx.renderer.error(result.error or "recall failed")
        return

    facts = result.value["facts"]
    episodes = result.value["episodes"]

    if not facts and not episodes:
        ctx.renderer.info(f"no matches for {query!r}")
        return

    if facts:
        lines = []
        for i, f in enumerate(facts, 1):
            tag_str = f" [{', '.join(f['tags'])}]" if f["tags"] else ""
            lines.append(
                f"{i:>2}. #{f['id']:<4} [{f['topic']}]{tag_str} "
                f"conf={f['confidence']:.2f} {f['source']} — {f['fact']}"
            )
        ctx.renderer.result(f"recall: {query}", lines)

    if episodes:
        lines = []
        for i, e in enumerate(episodes, 1):
            preview = e["input"][:60] + ("…" if len(e["input"]) > 60 else "")
            lines.append(f"{i:>2}. #{e['id']:<4} sim={e['score']:.3f} — {preview}")
        ctx.renderer.result("similar episodes", lines)


def cmd_stub(ctx: Context, name: str) -> None:
    phase = STUB_COMMANDS.get(name, "?")
    ctx.renderer.warn(f"'{name}' is not yet implemented (Phase {phase}).")