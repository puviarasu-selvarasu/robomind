import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from robomind.core.models import Episode
from robomind.memory import cbr
from robomind.memory.store import SQLiteMemoryStore


class TestCbr(unittest.TestCase):
    def setUp(self):
        self.td = TemporaryDirectory()
        self.store = SQLiteMemoryStore(Path(self.td.name) / "t.db")

    def tearDown(self):
        self.store.close()
        self.td.cleanup()

    def test_tokenize_drops_stopwords(self):
        t = cbr.tokenize("design the 2-dof arm")
        self.assertIn("design", t)
        self.assertIn("2", t)
        self.assertNotIn("the", t)

    def test_jaccard_identical(self):
        a = cbr.tokenize("servo torque")
        self.assertAlmostEqual(cbr.jaccard(a, a), 1.0)

    def test_jaccard_disjoint(self):
        a = cbr.tokenize("servo torque")
        b = cbr.tokenize("battery voltage")
        self.assertEqual(cbr.jaccard(a, b), 0.0)

    def test_similar_episodes_ranks(self):
        self.store.insert_episode(Episode(input="design a 2-dof arm reaching x=150 y=80"))
        self.store.insert_episode(Episode(input="battery life for a 12v lipo"))
        self.store.insert_episode(Episode(input="design a 3-dof arm"))
        cases = cbr.similar_episodes(self.store, "design arm reaching x y", k=2)
        self.assertGreaterEqual(len(cases), 1)
        self.assertIn("arm", cases[0].episode.input)


if __name__ == "__main__":
    unittest.main()