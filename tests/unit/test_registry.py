import unittest
from robomind.core.models import ToolResult
from robomind.tools.base import BaseTool
from robomind.tools.registry import ToolRegistry


class _Dummy(BaseTool):
    name = "dummy"
    description = "test"
    def run(self, **kwargs):
        return ToolResult(step_id="s1", ok=True)


class TestRegistry(unittest.TestCase):
    def test_empty(self):
        r = ToolRegistry()
        self.assertEqual(r.list(), [])
        self.assertEqual(len(r), 0)

    def test_register_and_get(self):
        r = ToolRegistry()
        t = _Dummy()
        r.register(t)
        self.assertIs(r.get("dummy"), t)
        self.assertIn("dummy", r)

    def test_duplicate_rejected(self):
        r = ToolRegistry()
        r.register(_Dummy())
        with self.assertRaises(ValueError):
            r.register(_Dummy())


if __name__ == "__main__":
    unittest.main()