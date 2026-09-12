# Architecture

Layered, dependencies point inward.

- Presenters: ui/, cli/ — CLI, retro renderer, voice, face
- Agent core: core/ — loop, planner, reasoner, reflector, learner
- Domain: domain/ — kinematics, dynamics, electronics, rules, datasheets
- Tools: tools/ — pure functions registered once
- Memory: memory/ — SQLite + FTS5, episodic + semantic + procedural
- Adapters: llm/, ui/voice/, ui/face/ — behind ports

Ports (core/ports.py): LLM, Voice, Renderer, MemoryStore, Tool.

Core and domain import stdlib only. Optional dependencies live behind adapters.