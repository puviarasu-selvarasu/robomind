import unittest
from robomind.tools.datasheet_tool import DatasheetTool


class TestDatasheetTool(unittest.TestCase):
    def setUp(self):
        self.tool = DatasheetTool()

    def test_lookup(self):
        r = self.tool.run(action="lookup", name="SG90")
        self.assertTrue(r.ok)
        self.assertEqual(r.value["datasheet"]["type"], "servo")

    def test_lookup_missing(self):
        r = self.tool.run(action="lookup", name="NopeNope")
        self.assertFalse(r.ok)

    def test_search(self):
        r = self.tool.run(action="search", query="MG")
        self.assertTrue(r.ok)
        names = {h["name"] for h in r.value["hits"]}
        self.assertIn("MG996R", names)

    def test_category(self):
        r = self.tool.run(action="category", name="MPU6050")
        self.assertTrue(r.ok)
        self.assertEqual(r.value["category"], "sensors")

    def test_list(self):
        r = self.tool.run(action="list")
        self.assertTrue(r.ok)
        self.assertIn("servos", r.value["inventory"])


if __name__ == "__main__":
    unittest.main()