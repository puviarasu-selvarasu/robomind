# RoboMind

Offline, CLI-based retro-futuristic AI that acts as a robotics engineer
(hardware + software). Thinks in a cognitive loop. Learns from experience.
Runs entirely on a CPU-only Windows machine. Never touches the cloud.

## Phase

Phase 0 — skeleton. Boots, reads config, writes logs, creates the SQLite
memory database. No REPL yet.

## Quick start

    pip install -e .
    python -m robomind

## Requirements

- Python 3.11+
- Windows 10/11, Windows Terminal recommended
- Optional: Ollama (local LLM), pyttsx3 (voice), Pillow (face capture)

## Layout

- `robomind/` — package source
- `data/` — runtime data (gitignored): DB, logs, faces, models
- `scripts/` — offline prep tools
- `tests/` — unit + integration tests
- `docs/` — architecture, commands, budgets

## License

Personal project. No license yet.