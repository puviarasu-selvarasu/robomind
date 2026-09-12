import math
import unittest

from robomind.tools.fk_tool import FKTool
from robomind.tools.ik_tool import IKTool


class TestFKTool(unittest.TestCase):
    def setUp(self):
        self.tool = FKTool()

    def test_single_link_zero(self):
        r = self.tool.run(link_lengths=[1.0], joint_angles_deg=[0.0])
        self.assertTrue(r.ok)
        self.assertAlmostEqual(r.value["x"], 1.0, places=9)

    def test_two_links(self):
        r = self.tool.run(link_lengths=[1.0, 1.0], joint_angles_deg=[0.0, 90.0])
        self.assertTrue(r.ok)
        self.assertAlmostEqual(r.value["x"], 1.0, places=9)
        self.assertAlmostEqual(r.value["y"], 1.0, places=9)

    def test_mismatch(self):
        r = self.tool.run(link_lengths=[1.0, 1.0], joint_angles_deg=[0.0])
        self.assertFalse(r.ok)


class TestIKTool(unittest.TestCase):
    def setUp(self):
        self.tool = IKTool()

    def test_reachable(self):
        r = self.tool.run(x=1.0, y=1.0, L1=1.0, L2=1.0)
        self.assertTrue(r.ok)
        self.assertEqual(len(r.value["solutions"]), 2)
        elbows = {s["elbow"] for s in r.value["solutions"]}
        self.assertEqual(elbows, {"up", "down"})

    def test_unreachable(self):
        r = self.tool.run(x=5.0, y=0.0, L1=1.0, L2=1.0)
        self.assertFalse(r.ok)
        self.assertIn("unreachable", r.error.lower())

    def test_missing(self):
        r = self.tool.run(x=1.0, y=1.0)
        self.assertFalse(r.ok)

    def test_radians(self):
        r = self.tool.run(x=2.0, y=0.0, L1=1.0, L2=1.0, unit="rad")
        self.assertTrue(r.ok)
        self.assertLess(abs(r.value["solutions"][0]["theta1"]), 1e-6)


if __name__ == "__main__":
    unittest.main()