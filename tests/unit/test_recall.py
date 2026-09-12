import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from robomind.core.models import Fact
from robomind.memory import recall
from robomind.memory.store import SQLiteMemoryStore


class TestRecall(unittest.TestCase):
    def setUp(self):
        self.td = TemporaryDirectory()
        self.store = SQLiteMemoryStore(Path(self.td.name) / "t.db")
        self.store.insert_fact(Fact(topic="servo", fact="SG90 torque is 1.8 kg/cm",
                                    tags=("torque",)))
        self.store.insert_fact(Fact(topic="servo", fact="MG996R stall current 2.5A",
                                    tags=("current",)))
        self.store.insert_fact(Fact(topic="battery", fact="LiPo 3S nominal 11.1V"))

    def tearDown(self):
        self.store.close()
        self.td.cleanup()

    def test_recall_facts_by_text(self):
        r = recall.recall_facts(self.store, "SG90", limit=5)
        self.assertGreaterEqual(len(r), 1)
        self.assertIn("SG90", r[0].fact.fact)

    def test_recall_facts_by_tag(self):
        r = recall.recall_facts(self.store, "servo", tags=("current",), limit=5)
        facts = [rf.fact.fact for rf in r]
        self.assertTrue(any("MG996R" in f for f in facts))

    def test_min_confidence_filter(self):
        self.store.set_fact_confidence(1, 0.0)
        r = recall.recall_facts(self.store, "SG90", min_confidence=0.5)
        self.assertEqual(len(r), 0)

    def test_recall_returns_empty_for_unknown(self):
        r = recall.recall_facts(self.store, "zzzzzz", limit=5)
        self.assertEqual(len(r), 0)


if __name__ == "__main__":
    unittest.main()