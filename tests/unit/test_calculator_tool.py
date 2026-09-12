import math
import unittest

from robomind.tools.calculator_tool import CalculatorTool, safe_eval


class TestSafeEval(unittest.TestCase):
    def test_basic(self):
        self.assertAlmostEqual(safe_eval("2 + 3 * 4"), 14.0)
        self.assertAlmostEqual(safe_eval("(2 + 3) * 4"), 20.0)

    def test_functions(self):
        self.assertAlmostEqual(safe_eval("sqrt(16)"), 4.0)
        self.assertAlmostEqual(safe_eval("sin(pi/2)"), 1.0)

    def test_unary(self):
        self.assertAlmostEqual(safe_eval("-5"), -5.0)

    def test_rejects_unknown_name(self):
        with self.assertRaises(ValueError):
            safe_eval("__import__('os')")

    def test_rejects_attribute(self):
        with self.assertRaises(ValueError):
            safe_eval("(1).__class__")

    def test_rejects_call_to_non_whitelist(self):
        with self.assertRaises(ValueError):
            safe_eval("open('x')")


class TestCalculatorTool(unittest.TestCase):
    def setUp(self):
        self.tool = CalculatorTool()

    def test_ok(self):
        r = self.tool.run(expr="2 + 2")
        self.assertTrue(r.ok)
        self.assertAlmostEqual(r.value["value"], 4.0)

    def test_empty(self):
        r = self.tool.run(expr="")
        self.assertFalse(r.ok)


if __name__ == "__main__":
    unittest.main()