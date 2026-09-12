import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from robomind.memory.store import SQLiteMemoryStore
from robomind.tools.memory_tool import MemoryTool


class TestMemoryTool(unittest.TestCase):
    def setUp(self):
        self.td = TemporaryDirectory()
        self.store = SQLiteMemoryStore(Path(self.td.name) / "t.db")
        self.tool = MemoryTool(self.store)

    def tearDown(self):
        self.store.close()
        self.td.cleanup()

    def test_learn_and_get(self):
        r = self.tool.run(action="learn", topic="servo",
                          fact="SG90 torque is 1.8 kg/cm")
        self.assertTrue(r.ok)
        self.assertEqual(r.value["topic"], "servo")
        self.assertEqual(self.store.count_facts(), 1)

    def test_learn_extracts_tags(self):
        r = self.tool.run(action="learn", topic="servo",
                          fact="MG996R stall current 2.5A #current #specs")
        self.assertTrue(r.ok)
        self.assertIn("current", r.value["tags"])
        self.assertIn("specs", r.value["tags"])

    def test_learn_dedupes(self):
        self.tool.run(action="learn", topic="servo", fact="SG90 torque 1.8")
        self.tool.run(action="learn", topic="servo", fact="SG90 torque 1.8")
        self.assertEqual(self.store.count_facts(), 1)

    def test_recall_after_learn(self):
        self.tool.run(action="learn", topic="servo",
                      fact="SG90 torque is 1.8 kg/cm")
        r = self.tool.run(action="recall", query="SG90")
        self.assertTrue(r.ok)
        self.assertGreaterEqual(len(r.value["facts"]), 1)

    def test_learn_missing_args_fails(self):
        r = self.tool.run(action="learn", topic="x")
        self.assertFalse(r.ok)

    def test_unknown_action(self):
        r = self.tool.run(action="nope")
        self.assertFalse(r.ok)


if __name__ == "__main__":
    unittest.main()