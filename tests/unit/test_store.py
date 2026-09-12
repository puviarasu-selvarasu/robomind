import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from robomind.core.models import Fact, Rule
from robomind.memory.store import SQLiteMemoryStore


class TestStore(unittest.TestCase):
    def setUp(self):
        self.td = TemporaryDirectory()
        self.db_path = Path(self.td.name) / "test.db"
        self.store = SQLiteMemoryStore(self.db_path)

    def tearDown(self):
        self.store.close()
        self.td.cleanup()

    def test_db_file_created(self):
        self.assertTrue(self.db_path.exists())

    def test_wal_mode_active(self):
        conn = sqlite3.connect(str(self.db_path))
        try:
            mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        finally:
            conn.close()
        self.assertEqual(mode.lower(), "wal")

    def test_schema_version_is_one(self):
        conn = sqlite3.connect(str(self.db_path))
        try:
            row = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()
        finally:
            conn.close()
        self.assertEqual(row[0], 1)

    def test_all_tables_present(self):
        conn = sqlite3.connect(str(self.db_path))
        try:
            names = {
                r[0] for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type IN ('table','view')"
                ).fetchall()
            }
        finally:
            conn.close()
        for t in ("facts", "facts_fts", "episodes", "episodes_fts",
                  "rules", "schema_version"):
            self.assertIn(t, names, f"missing table {t}")

    def test_fact_insert_and_search(self):
        fid = self.store.insert_fact(
            Fact(topic="servo", fact="SG90 torque is 1.8 kg/cm")
        )
        self.assertGreater(fid, 0)
        results = self.store.search_facts("SG90", limit=5)
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("SG90", results[0].fact)

    def test_fact_dedupe(self):
        f = Fact(topic="servo", fact="SG90 torque is 1.8 kg/cm")
        id1 = self.store.insert_fact(f)
        id2 = self.store.insert_fact(f)
        self.assertEqual(id1, id2)
        self.assertEqual(self.store.count_facts(), 1)

    def test_rule_upsert_and_get(self):
        r = Rule(name="test_rule", when={"intent": "x"}, then={"call": "y"})
        rid = self.store.upsert_rule(r)
        self.assertGreater(rid, 0)
        got = self.store.get_rule("test_rule")
        self.assertIsNotNone(got)
        self.assertEqual(got.name, "test_rule")
        self.assertEqual(got.when, {"intent": "x"})

    def test_episode_insert(self):
        from robomind.core.models import Episode
        eid = self.store.insert_episode(Episode(input="hello", intent="greet"))
        self.assertGreater(eid, 0)
        self.assertEqual(self.store.count_episodes(), 1)


if __name__ == "__main__":
    unittest.main()