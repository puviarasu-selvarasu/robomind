import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from robomind.cli.commands import Context
from robomind.cli.repl import RoboMindREPL
from robomind.config import build_config
from robomind.llm.null_llm import NullLLM
from robomind.memory.store import SQLiteMemoryStore
from robomind.tools.registry import ToolRegistry
from robomind.ui.plain import PlainRenderer
from robomind.ui.voice.null_voice import NullVoice


class TestReplBoot(unittest.TestCase):
    def setUp(self):
        self.td = TemporaryDirectory()
        cfg = build_config({"home": self.td.name, "retro": "off"})
        self.store = SQLiteMemoryStore(cfg.db)
        self.ctx = Context(
            config=cfg, store=self.store, renderer=PlainRenderer(),
            tools=ToolRegistry(), llm=NullLLM(), voice=NullVoice(),
        )
        self.repl = RoboMindREPL(self.ctx)

    def tearDown(self):
        self.store.close()
        self.td.cleanup()

    def _onecmd(self, line):
        buf = io.StringIO()
        with redirect_stdout(buf):
            stop = self.repl.onecmd(line)
        return stop, buf.getvalue()

    def test_help_lists_commands(self):
        stop, out = self._onecmd("help")
        self.assertFalse(stop)
        self.assertIn("ask", out)
        self.assertIn("config list", out)

    def test_version(self):
        _, out = self._onecmd("version")
        self.assertIn("RoboMind", out)

    def test_tools_empty(self):
        _, out = self._onecmd("tools list")
        self.assertIn("No tools registered", out)

    def test_quit_stops(self):
        stop, _ = self._onecmd("quit")
        self.assertTrue(stop)

    def test_stub_command(self):
        _, out = self._onecmd("ask design an arm")
        self.assertIn("not yet implemented", out)


if __name__ == "__main__":
    unittest.main()