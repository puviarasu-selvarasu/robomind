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
from robomind.tools.memory_tool import MemoryTool
from robomind.tools.registry import ToolRegistry
from robomind.ui.plain import PlainRenderer
from robomind.ui.voice.null_voice import NullVoice


class TestLearnRecallFlow(unittest.TestCase):
    def setUp(self):
        self.td = TemporaryDirectory()
        cfg = build_config({"home": self.td.name, "retro": "off"})
        self.store = SQLiteMemoryStore(cfg.db)
        tools = ToolRegistry()
        tools.register(MemoryTool(self.store))
        self.ctx = Context(config=cfg, store=self.store,
                           renderer=PlainRenderer(), tools=tools,
                           llm=NullLLM(), voice=NullVoice())
        self.repl = RoboMindREPL(self.ctx)

    def tearDown(self):
        self.store.close()
        self.td.cleanup()

    def _run(self, line):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.repl.onecmd(line)
        return buf.getvalue()

    def test_learn_recall_roundtrip(self):
        self._run("learn servo | SG90 torque is 1.8 kg/cm #torque")
        out = self._run("recall servo")
        self.assertIn("SG90", out)
        self.assertIn("torque", out)

    def test_learn_without_pipe_errors(self):
        out = self._run("learn no pipe here")
        self.assertIn("format", out.lower())

    def test_recall_unknown(self):
        out = self._run("recall zzzzzz")
        self.assertIn("no matches", out.lower())

    def test_tools_list_includes_memory(self):
        out = self._run("tools list")
        self.assertIn("memory", out)


if __name__ == "__main__":
    unittest.main()