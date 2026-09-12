"""Configuration resolution: CLI flags > env vars > config.json > defaults.

Precedence is applied per-field. Paths derive from ``home`` unless explicitly set.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _default_home() -> Path:
    """E:/robomind/data if the drive exists, else %USERPROFILE%/robomind/data."""
    candidate = Path("E:/robomind/data")
    if candidate.drive and Path(candidate.drive + "/").exists():
        return candidate
    profile = os.environ.get("USERPROFILE") or str(Path.home())
    return Path(profile) / "robomind" / "data"


@dataclass(slots=True)
class Config:
    # paths
    home: Path
    db: Path
    log_dir: Path
    faces_dir: Path
    models_dir: Path

    # llm
    ollama_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5-coder:0.5b"
    llm_keep_alive: str = "60s"
    llm_ctx: int = 2048
    llm: str = "off"

    # voice
    voice: str = "off"
    voice_engine: str = "sapi"
    voice_rate: int = 180

    # face
    face: str = "off"
    face_size: str = "50x25"
    face_palette: str = "cyan"

    # ui / behavior
    retro: str = "on"
    sound: str = "off"
    dry_run: bool = False
    verbose: bool = False
    boot: bool = False

    # logging
    log_level: str = "INFO"

    def __post_init__(self) -> None:
        for p in (self.home, self.log_dir, self.faces_dir, self.models_dir):
            p.mkdir(parents=True, exist_ok=True)
        self.db.parent.mkdir(parents=True, exist_ok=True)

    def validate(self) -> list[str]:
        errors: list[str] = []
        for field_name in ("voice", "face", "llm", "retro", "sound"):
            val = getattr(self, field_name)
            if val not in ("on", "off"):
                errors.append(f"{field_name} must be on|off, got {val!r}")
        try:
            w, h = self.face_size.lower().split("x")
            int(w)
            int(h)
        except Exception:
            errors.append(f"face_size must be WxH, got {self.face_size!r}")
        if self.llm_ctx < 256:
            errors.append(f"llm_ctx must be >= 256, got {self.llm_ctx}")
        return errors


def _load_json_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _env_overrides() -> dict[str, Any]:
    out: dict[str, Any] = {}
    simple = {
        "ROBOMIND_OLLAMA_URL": "ollama_url",
        "ROBOMIND_LLM_MODEL": "llm_model",
        "ROBOMIND_LLM_KEEP_ALIVE": "llm_keep_alive",
        "ROBOMIND_VOICE": "voice",
        "ROBOMIND_FACE": "face",
        "ROBOMIND_SOUND": "sound",
        "ROBOMIND_LOG_LEVEL": "log_level",
    }
    for env_key, field_name in simple.items():
        v = os.environ.get(env_key)
        if v is not None:
            out[field_name] = v
    paths = {
        "ROBOMIND_HOME": "home",
        "ROBOMIND_DB": "db",
        "ROBOMIND_LOG_DIR": "log_dir",
        "ROBOMIND_FACES": "faces_dir",
        "ROBOMIND_MODELS": "models_dir",
    }
    for env_key, field_name in paths.items():
        v = os.environ.get(env_key)
        if v:
            out[field_name] = Path(v)
    return out


def _resolve_home(cli: dict[str, Any]) -> Path:
    if cli.get("home"):
        return Path(cli["home"])
    env_home = os.environ.get("ROBOMIND_HOME")
    if env_home:
        return Path(env_home)
    return _default_home()


def build_config(cli_args: dict[str, Any] | None = None) -> Config:
    """Build a fully-resolved Config from CLI, env, config.json, and defaults."""
    cli = {k: v for k, v in (cli_args or {}).items() if v is not None}

    home = _resolve_home(cli)
    json_cfg = _load_json_config(home / "config.json")
    env_cfg = _env_overrides()

    merged: dict[str, Any] = {}
    merged.update(json_cfg)
    merged.update(env_cfg)
    merged.update(cli)

    # home may have been overridden by env or CLI
    home = Path(merged.get("home", home))
    merged["home"] = home

    for key, default in (
        ("db", home / "robomind.db"),
        ("log_dir", home / "logs"),
        ("faces_dir", home / "faces"),
        ("models_dir", home / "models"),
    ):
        if key not in merged:
            merged[key] = default
        merged[key] = Path(merged[key])

    valid = {k: v for k, v in merged.items() if k in Config.__dataclass_fields__}
    return Config(**valid)