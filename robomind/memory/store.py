"""SQLite-backed memory store. Tier A: stdlib only.

Thread model: one connection per thread (thread-local). WAL mode.
No long-held transactions. All writes are autocommitted.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from pathlib import Path

from ..core.models import Episode, Fact, Rule


SCHEMA_PATH = Path(__file__).parent / "schema.sql"
CURRENT_VERSION = 1


class SQLiteMemoryStore:
    """Concrete MemoryStore. Satisfies robomind.core.ports.MemoryStore."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._migrate()

    # ---------------------------------------------------------- connection
    def _conn(self) -> sqlite3.Connection:
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(str(self.db_path), isolation_level=None)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA synchronous = NORMAL")
            self._local.conn = conn
        return conn

    def _migrate(self) -> None:
        sql = SCHEMA_PATH.read_text(encoding="utf-8")
        self._conn().executescript(sql)

    # --------------------------------------------------------------- facts
    def insert_fact(self, fact: Fact) -> int:
        h = _dedupe_hash(fact.topic, fact.fact)
        conn = self._conn()
        cur = conn.execute(
            """
            INSERT INTO facts(topic, fact, tags, confidence, dedupe_hash)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(dedupe_hash) DO UPDATE SET
                tags       = excluded.tags,
                confidence = MAX(facts.confidence, excluded.confidence),
                updated_at = CURRENT_TIMESTAMP
            """,
            (fact.topic, fact.fact, ",".join(fact.tags), fact.confidence, h),
        )
        if cur.lastrowid:
            return int(cur.lastrowid)
        row = conn.execute(
            "SELECT id FROM facts WHERE dedupe_hash = ?", (h,)
        ).fetchone()
        return int(row["id"])

    def search_facts(self, query: str, limit: int = 10) -> list[Fact]:
        conn = self._conn()
        try:
            rows = conn.execute(
                """
                SELECT f.* FROM facts_fts
                JOIN facts f ON f.id = facts_fts.rowid
                WHERE facts_fts MATCH ?
                ORDER BY bm25(facts_fts), f.confidence DESC
                LIMIT ?
                """,
                (query, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = conn.execute(
                """
                SELECT * FROM facts
                WHERE topic LIKE ? OR fact LIKE ?
                ORDER BY confidence DESC, updated_at DESC
                LIMIT ?
                """,
                (f"%{query}%", f"%{query}%", limit),
            ).fetchall()
        return [_row_to_fact(r) for r in rows]

    def get_fact(self, fact_id: int) -> Fact | None:
        row = self._conn().execute(
            "SELECT * FROM facts WHERE id = ?", (fact_id,)
        ).fetchone()
        return _row_to_fact(row) if row else None

    def count_facts(self) -> int:
        return int(self._conn().execute("SELECT COUNT(*) FROM facts").fetchone()[0])

    # ------------------------------------------------------------ episodes
    def insert_episode(self, ep: Episode) -> int:
        success = None if ep.success is None else (1 if ep.success else 0)
        cur = self._conn().execute(
            """
            INSERT INTO episodes(input, intent, plan_json, actions_json,
                                 result_json, success, score, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (ep.input, ep.intent, ep.plan_json, ep.actions_json,
             ep.result_json, success, ep.score, ep.duration_ms),
        )
        return int(cur.lastrowid)

    def search_episodes(self, query: str, limit: int = 10) -> list[Episode]:
        conn = self._conn()
        try:
            rows = conn.execute(
                """
                SELECT e.* FROM episodes_fts
                JOIN episodes e ON e.id = episodes_fts.rowid
                WHERE episodes_fts MATCH ?
                ORDER BY bm25(episodes_fts)
                LIMIT ?
                """,
                (query, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = conn.execute(
                "SELECT * FROM episodes WHERE input LIKE ? LIMIT ?",
                (f"%{query}%", limit),
            ).fetchall()
        return [_row_to_episode(r) for r in rows]

    def count_episodes(self) -> int:
        return int(self._conn().execute("SELECT COUNT(*) FROM episodes").fetchone()[0])

    # --------------------------------------------------------------- rules
    def get_rule(self, name: str) -> Rule | None:
        row = self._conn().execute(
            "SELECT * FROM rules WHERE name = ?", (name,)
        ).fetchone()
        return _row_to_rule(row) if row else None

    def upsert_rule(self, rule: Rule) -> int:
        conn = self._conn()
        cur = conn.execute(
            """
            INSERT INTO rules(version, name, when_json, then_json, weight, hits, wins)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                version   = excluded.version,
                when_json = excluded.when_json,
                then_json = excluded.then_json,
                weight    = excluded.weight
            """,
            (rule.version, rule.name, json.dumps(rule.when),
             json.dumps(rule.then), rule.weight, rule.hits, rule.wins),
        )
        if cur.lastrowid:
            return int(cur.lastrowid)
        row = conn.execute("SELECT id FROM rules WHERE name = ?", (rule.name,)).fetchone()
        return int(row["id"])

    def update_rule_stats(self, rule_id: int, hit: bool, win: bool) -> None:
        h = 1 if hit else 0
        w = 1 if win else 0
        self._conn().execute(
            """
            UPDATE rules
               SET hits          = hits + ?,
                   wins          = wins + ?,
                   last_fired_at = CURRENT_TIMESTAMP,
                   weight        = (wins + 1.0) / (hits + 2.0)
             WHERE id = ?
            """,
            (h, w, rule_id),
        )

    def list_rules(self, limit: int = 100) -> list[Rule]:
        rows = self._conn().execute(
            "SELECT * FROM rules ORDER BY weight DESC, hits DESC LIMIT ?", (limit,)
        ).fetchall()
        return [_row_to_rule(r) for r in rows]

    # --------------------------------------------------------------- close
    def close(self) -> None:
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            conn.close()
            self._local.conn = None


# ---------------------------------------------------------------- helpers
def _dedupe_hash(topic: str, fact: str) -> str:
    norm = f"{topic.strip().lower()}|{fact.strip().lower()}"
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def _row_to_fact(r: sqlite3.Row) -> Fact:
    tags_raw = r["tags"] or ""
    return Fact(
        id=r["id"],
        topic=r["topic"],
        fact=r["fact"],
        tags=tuple(t for t in tags_raw.split(",") if t),
        confidence=r["confidence"],
        created_at=r["created_at"],
        updated_at=r["updated_at"],
    )


def _row_to_episode(r: sqlite3.Row) -> Episode:
    return Episode(
        id=r["id"],
        input=r["input"],
        intent=r["intent"],
        plan_json=r["plan_json"],
        actions_json=r["actions_json"],
        result_json=r["result_json"],
        success=None if r["success"] is None else bool(r["success"]),
        score=r["score"],
        duration_ms=r["duration_ms"],
        created_at=r["created_at"],
    )


def _row_to_rule(r: sqlite3.Row) -> Rule:
    return Rule(
        id=r["id"],
        version=r["version"],
        name=r["name"],
        when=json.loads(r["when_json"]),
        then=json.loads(r["then_json"]),
        weight=r["weight"],
        hits=r["hits"],
        wins=r["wins"],
        last_fired_at=r["last_fired_at"],
        created_at=r["created_at"],
    )