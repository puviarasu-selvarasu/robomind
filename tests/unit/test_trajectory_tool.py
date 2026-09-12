import unittest

from robomind.tools.trajectory_tool import TrajectoryTool


class TestTrajectoryTool(unittest.TestCase):
    def setUp(self):
        self.tool = TrajectoryTool()

    def test_linear(self):
        r = self.tool.run(action="linear", start=0.0, end=10.0, n=11)
        self.assertTrue(r.ok)
        self.assertEqual(len(r.value["samples"]), 11)
        self.assertAlmostEqual(r.value["samples"][0], 0.0)
        self.assertAlmostEqual(r.value["samples"][-1], 10.0)

    def test_cubic(self):
        r = self.tool.run(action="cubic", start=0.0, end=1.0, n=10)
        self.assertTrue(r.ok)
        self.assertEqual(len(r.value["samples"]), 10)

    def test_trapezoidal(self):
        r = self.tool.run(action="trapezoidal",
                          distance=0.5, max_vel=1.0, max_accel=2.0, n=25)
        self.assertTrue(r.ok)
        self.assertEqual(len(r.value["samples"]), 25)
        self.assertIn("meta", r.value)

    def test_bad_action(self):
        r = self.tool.run(action="zigzag")
        self.assertFalse(r.ok)


if __name__ == "__main__":
    unittest.main()