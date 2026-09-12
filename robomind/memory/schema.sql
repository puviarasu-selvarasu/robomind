-- RoboMind memory schema, version 1.
-- External-content FTS5 tables with AFTER INSERT/UPDATE/DELETE triggers.
-- Idempotent: safe to re-run.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA synchronous  = NORMAL;

CREATE TABLE IF NOT EXISTS schema_version (
    version    INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------- facts
CREATE TABLE IF NOT EXISTS facts (
    id          INTEGER PRIMARY KEY,
    topic       TEXT NOT NULL,
    fact        TEXT NOT NULL,
    tags        TEXT,
    confidence  REAL DEFAULT 1.0,
    dedupe_hash TEXT UNIQUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_facts_topic ON facts(topic);

CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
    topic, fact, tags,
    content='facts',
    content_rowid='id',
    tokenize='unicode61'
);

CREATE TRIGGER IF NOT EXISTS facts_ai AFTER INSERT ON facts BEGIN
    INSERT INTO facts_fts(rowid, topic, fact, tags)
    VALUES (new.id, new.topic, new.fact, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS facts_ad AFTER DELETE ON facts BEGIN
    INSERT INTO facts_fts(facts_fts, rowid, topic, fact, tags)
    VALUES ('delete', old.id, old.topic, old.fact, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS facts_au AFTER UPDATE ON facts BEGIN
    INSERT INTO facts_fts(facts_fts, rowid, topic, fact, tags)
    VALUES ('delete', old.id, old.topic, old.fact, old.tags);
    INSERT INTO facts_fts(rowid, topic, fact, tags)
    VALUES (new.id, new.topic, new.fact, new.tags);
END;

-- ------------------------------------------------------------- episodes
CREATE TABLE IF NOT EXISTS episodes (
    id           INTEGER PRIMARY KEY,
    input        TEXT NOT NULL,
    intent       TEXT,
    plan_json    TEXT,
    actions_json TEXT,
    result_json  TEXT,
    success      INTEGER,
    score        REAL,
    duration_ms  INTEGER,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_episodes_created ON episodes(created_at);

CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts USING fts5(
    input, intent,
    content='episodes',
    content_rowid='id',
    tokenize='unicode61'
);

CREATE TRIGGER IF NOT EXISTS episodes_ai AFTER INSERT ON episodes BEGIN
    INSERT INTO episodes_fts(rowid, input, intent)
    VALUES (new.id, new.input, new.intent);
END;

CREATE TRIGGER IF NOT EXISTS episodes_ad AFTER DELETE ON episodes BEGIN
    INSERT INTO episodes_fts(episodes_fts, rowid, input, intent)
    VALUES ('delete', old.id, old.input, old.intent);
END;

CREATE TRIGGER IF NOT EXISTS episodes_au AFTER UPDATE ON episodes BEGIN
    INSERT INTO episodes_fts(episodes_fts, rowid, input, intent)
    VALUES ('delete', old.id, old.input, old.intent);
    INSERT INTO episodes_fts(rowid, input, intent)
    VALUES (new.id, new.input, new.intent);
END;

-- ---------------------------------------------------------------- rules
CREATE TABLE IF NOT EXISTS rules (
    id            INTEGER PRIMARY KEY,
    version       INTEGER NOT NULL DEFAULT 1,
    name          TEXT UNIQUE NOT NULL,
    when_json     TEXT NOT NULL,
    then_json     TEXT NOT NULL,
    weight        REAL DEFAULT 1.0,
    hits          INTEGER DEFAULT 0,
    wins          INTEGER DEFAULT 0,
    last_fired_at TIMESTAMP,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO schema_version(version) VALUES (1);