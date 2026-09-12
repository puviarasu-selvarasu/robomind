"""Structured JSON-lines logging."""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path


_STANDARD_ATTRS = frozenset({
    "args", "asctime", "created", "exc_info", "exc_text", "filename",
    "funcName", "levelname", "levelno", "lineno", "module", "msecs",
    "message", "msg", "name", "pathname", "process", "processName",
    "relativeCreated", "stack_info", "thread", "threadName",
})


class JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        for k, v in record.__dict__.items():
            if k in _STANDARD_ATTRS or k.startswith("_"):
                continue
            try:
                json.dumps(v)
                payload[k] = v
            except Exception:
                payload[k] = repr(v)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(log_dir: Path, level: str = "INFO", *, console: bool = False) -> Path:
    """Configure root logger. Returns path of the active log file."""
    log_dir.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(level.upper())
    for h in list(root.handlers):
        root.removeHandler(h)

    day = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"robomind-{day}.jsonl"

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(JsonLineFormatter())
    fh.setLevel(level.upper())
    root.addHandler(fh)

    if console:
        ch = logging.StreamHandler(sys.stderr)
        ch.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        ch.setLevel(level.upper())
        root.addHandler(ch)

    return log_file