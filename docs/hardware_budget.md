# Hardware budget

Target: i5-8250U, 8 GB single-channel, Windows 11, CPU-only.

| Component | CPU | RAM |
|---|---|---|
| Core agent loop | <5% | 80 MB |
| SQLite memory | <1% | 30 MB |
| Face animator | <1% | 5 MB |
| SAPI voice | 2–4% | 25 MB |
| LLM (Ollama, external) | best-effort | separate process |
| Idle (everything off) | <2% | <150 MB |