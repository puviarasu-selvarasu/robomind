import unittest

from robomind.core.models import ToolResult
from robomind.tools.base import BaseTool
from robomind.tools.registry import ToolRegistry


class _WriteTool(BaseTool):
    name = "writer"
    description = "write test tool"
    safety_class = "write"
    def run(self, *, step_id="s", **kwargs):
        return ToolResult(step_id=step_id, ok=True, value="wrote")


class _ReadTool(BaseTool):
    name = "reader"
    description = "read test tool"
    safety_class = "read"
    def run(self, *, step_id="s", **kwargs):
        return ToolResult(step_id=step_id, ok=True, value="read")


class TestRuntime(unittest.TestCase):
    def setUp(self):
        self.reg = ToolRegistry()
        self.reg.register(_WriteTool())
        self.reg.register(_ReadTool())

    def test_read_allowed_in_dry_run(self):
        self.reg.dry_run = True
        r = self.reg.execute("reader")
        self.assertTrue(r.ok)

    def test_write_blocked_in_dry_run(self):
        self.reg.dry_run = True
        r = self.reg.execute("writer")
        self.assertFalse(r.ok)
        self.assertIn("dry-run", r.error)

    def test_write_allowed_without_dry_run(self):
        r = self.reg.execute("writer")
        self.assertTrue(r.ok)

    def test_unknown_tool(self):
        r = self.reg.execute("nope")
        self.assertFalse(r.ok)


if __name__ == "__main__":
    unittest.main()