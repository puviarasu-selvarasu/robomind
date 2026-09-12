import io
import unittest
from contextlib import redirect_stdout
from tempfile import TemporaryDirectory

from robomind.cli.commands import Context
from robomind.cli.repl import RoboMindREPL
from robomind.config import build_config
from robomind.llm.null_llm import NullLLM
from robomind.memory.store import SQLiteMemoryStore
from robomind.tools.calculator_tool import CalculatorTool
from robomind.tools.cad_tool import CADTool
from robomind.tools.codegen_tool import CodegenTool
from robomind.tools.datasheet_tool import DatasheetTool
from robomind.tools.diagnose_tool import DiagnoseTool
from robomind.tools.fk_tool import FKTool
from robomind.tools.ik_tool import IKTool
from robomind.tools.memory_tool import MemoryTool
from robomind.tools.registry import ToolRegistry
from robomind.tools.trajectory_tool import TrajectoryTool
from robomind.tools.units_tool import UnitsTool
from robomind.ui.plain import PlainRenderer
from robomind.ui.voice.null_voice import NullVoice


class TestToolsRegistered(unittest.TestCase):
    def setUp(self):
        self.td = TemporaryDirectory()
        cfg = build_config({"home": self.td.name, "retro": "off"})
        self.store = SQLiteMemoryStore(cfg.db)
        tools = ToolRegistry()
        for tool in (CalculatorTool(), UnitsTool(), FKTool(), IKTool(),
                     TrajectoryTool(), DatasheetTool(), DiagnoseTool(),
                     CADTool(), CodegenTool(), MemoryTool(self.store)):
            tools.register(tool)
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

    def test_tools_list_has_ten(self):
        out = self._run("tools list")
        for name in ("calculator", "units", "fk", "ik", "trajectory",
                     "datasheet", "diagnose", "cad", "codegen", "memory"):
            self.assertIn(name, out, f"missing tool in list: {name}")

    def test_tools_help(self):
        out = self._run("tools help ik")
        self.assertIn("inverse kinematics", out.lower())

    def test_call_calculator(self):
        out = self._run("call calculator expr=2+3*4")
        self.assertIn("14", out)

    def test_call_ik(self):
        out = self._run("call ik x=1 y=1 L1=1 L2=1")
        self.assertIn("solutions", out.lower())
        self.assertIn("up", out)
        self.assertIn("down", out)

    def test_call_units(self):
        out = self._run("call units action=convert value=1000 from_unit=mm to_unit=m")
        self.assertIn("1.0", out)

    def test_dry_run_blocks_cad(self):
        self.ctx.tools.dry_run = True
        out = self._run("call cad action=plate")
        self.assertIn("dry-run", out)


if __name__ == "__main__":
    unittest.main()