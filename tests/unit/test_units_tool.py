import unittest
from robomind.tools.units_tool import UnitsTool


class TestUnitsTool(unittest.TestCase):
    def setUp(self):
        self.tool = UnitsTool()

    def test_convert(self):
        r = self.tool.run(action="convert", value=1000, from_unit="mm", to_unit="m")
        self.assertTrue(r.ok)
        self.assertAlmostEqual(r.value["result"], 1.0)

    def test_convert_missing(self):
        r = self.tool.run(action="convert", value=1)
        self.assertFalse(r.ok)

    def test_list(self):
        r = self.tool.run(action="list")
        self.assertTrue(r.ok)
        self.assertIn("length", r.value["units"])

    def test_category(self):
        r = self.tool.run(action="category", unit="kgcm")
        self.assertTrue(r.ok)
        self.assertEqual(r.value["category"], "torque")


if __name__ == "__main__":
    unittest.main()