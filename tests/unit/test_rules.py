import math
import unittest

from robomind.domain import rules as R


class TestJointLimits(unittest.TestCase):
    def test_within(self):
        r = R.check_joint_limits(0.0, -math.pi / 2, math.pi / 2)
        self.assertTrue(r.ok)

    def test_outside(self):
        r = R.check_joint_limits(3.0, -1.0, 1.0)
        self.assertFalse(r.ok)

    def test_invalid_range(self):
        r = R.check_joint_limits(0.0, 1.0, -1.0)
        self.assertFalse(r.ok)


class TestReach(unittest.TestCase):
    def test_within(self):
        self.assertTrue(R.check_reach(1.0, 1.0, 1.0, 1.0).ok)

    def test_too_far(self):
        self.assertFalse(R.check_reach(5.0, 0.0, 1.0, 1.0).ok)

    def test_too_close(self):
        self.assertFalse(R.check_reach(0.0, 0.0, 2.0, 1.0).ok)


class TestTorque(unittest.TestCase):
    def test_ok(self):
        self.assertTrue(R.check_torque(0.5, 1.0).ok)

    def test_exceeds(self):
        self.assertFalse(R.check_torque(2.0, 1.0).ok)

    def test_no_available(self):
        self.assertFalse(R.check_torque(0.5, 0.0).ok)


class TestVoltageThermalCurrent(unittest.TestCase):
    def test_voltage_ok(self):
        self.assertTrue(R.check_voltage(11.1, 9.0, 12.6).ok)

    def test_voltage_low(self):
        self.assertFalse(R.check_voltage(8.0, 9.0, 12.6).ok)

    def test_thermal_ok(self):
        self.assertTrue(R.check_thermal(0.5, 1.0).ok)

    def test_thermal_over(self):
        self.assertFalse(R.check_thermal(2.0, 1.0).ok)

    def test_current_ok(self):
        self.assertTrue(R.check_current(0.5, 1.0).ok)

    def test_current_over(self):
        self.assertFalse(R.check_current(2.0, 1.0).ok)


class TestAggregator(unittest.TestCase):
    def test_all_ok(self):
        s = R.evaluate([
            R.check_reach(1.0, 1.0, 1.0, 1.0),
            R.check_torque(0.5, 1.0),
        ])
        self.assertTrue(s.ok)
        self.assertEqual(s.failures, ())

    def test_any_fail(self):
        s = R.evaluate([
            R.check_reach(1.0, 1.0, 1.0, 1.0),
            R.check_torque(2.0, 1.0),
        ])
        self.assertFalse(s.ok)
        self.assertEqual(len(s.failures), 1)


if __name__ == "__main__":
    unittest.main()