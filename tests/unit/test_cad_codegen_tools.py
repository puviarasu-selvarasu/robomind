import ast
import unittest

from robomind.tools.cad_tool import CADTool
from robomind.tools.codegen_tool import CodegenTool


class TestCADTool(unittest.TestCase):
    def setUp(self):
        self.tool = CADTool()

    def test_plate_emits_valid_python(self):
        r = self.tool.run(action="plate", width=50, height=30, thickness=3)
        self.assertTrue(r.ok)
        ast.parse(r.value["script"])

    def test_servo_bracket_emits_valid_python(self):
        r = self.tool.run(action="servo_bracket")
        self.assertTrue(r.ok)
        ast.parse(r.value["script"])

    def test_validate_ok(self):
        r = self.tool.run(action="validate", source="x = 1 + 2")
        self.assertTrue(r.ok)

    def test_validate_bad(self):
        r = self.tool.run(action="validate", source="x = (")
        self.assertFalse(r.ok)

    def test_bad_action(self):
        r = self.tool.run(action="nope")
        self.assertFalse(r.ok)


class TestCodegenTool(unittest.TestCase):
    def setUp(self):
        self.tool = CodegenTool()

    def test_arduino(self):
        r = self.tool.run(target="arduino", theta1_deg=30, theta2_deg=-15)
        self.assertTrue(r.ok)
        self.assertIn("Servo", r.value["code"])
        self.assertIn("30", r.value["code"])

    def test_micropython_valid_python(self):
        r = self.tool.run(target="micropython", theta1_deg=10, theta2_deg=20)
        self.assertTrue(r.ok)
        ast.parse(r.value["code"])

    def test_ros2_valid_python(self):
        r = self.tool.run(target="ros2", theta1_deg=10, theta2_deg=20)
        self.assertTrue(r.ok)
        ast.parse(r.value["code"])

    def test_unknown_target(self):
        r = self.tool.run(target="fortran")
        self.assertFalse(r.ok)


if __name__ == "__main__":
    unittest.main()