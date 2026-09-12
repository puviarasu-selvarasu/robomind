import math
import unittest

from robomind.domain import units as U


class TestConversions(unittest.TestCase):
    def test_length(self):
        self.assertAlmostEqual(U.convert(1000, "mm", "m"), 1.0, places=12)
        self.assertAlmostEqual(U.convert(1, "in", "mm"), 25.4, places=9)
        self.assertAlmostEqual(U.convert(1, "ft", "in"), 12.0, places=9)
        self.assertAlmostEqual(U.convert(1, "m", "cm"), 100.0, places=12)

    def test_angle(self):
        self.assertAlmostEqual(U.convert(180, "deg", "rad"), math.pi, places=12)
        self.assertAlmostEqual(U.convert(math.pi, "rad", "deg"), 180.0, places=9)
        self.assertAlmostEqual(U.convert(1, "turn", "deg"), 360.0, places=9)

    def test_force(self):
        self.assertAlmostEqual(U.convert(1, "kgf", "N"), 9.80665, places=9)
        self.assertAlmostEqual(U.convert(1, "lbf", "N"), 4.4482216152605, places=9)

    def test_torque(self):
        # 1 kgf·cm = 0.0980665 N·m
        self.assertAlmostEqual(U.convert(1, "kgcm", "Nm"), 0.0980665, places=9)
        self.assertAlmostEqual(U.convert(1, "Nm", "Nmm"), 1000.0, places=9)

    def test_roundtrip(self):
        for unit_a, unit_b in [("mm", "in"), ("kg", "lb"), ("deg", "rad")]:
            v = 12.345
            got = U.convert(U.convert(v, unit_a, unit_b), unit_b, unit_a)
            self.assertAlmostEqual(got, v, places=9)

    def test_incompatible_raises(self):
        with self.assertRaises(ValueError):
            U.convert(1, "m", "kg")

    def test_unknown_unit_raises(self):
        with self.assertRaises(ValueError):
            U.convert(1, "furlong", "m")

    def test_known_units_includes_servo_torque(self):
        ku = U.known_units()
        self.assertIn("kgcm", ku["torque"])
        self.assertIn("Nm", ku["torque"])


class TestQuantity(unittest.TestCase):
    def test_add_same_category(self):
        q = U.Quantity(1.0, "m") + U.Quantity(500.0, "mm")
        self.assertAlmostEqual(q.value, 1.5)
        self.assertEqual(q.unit, "m")

    def test_add_incompatible_raises(self):
        with self.assertRaises(ValueError):
            U.Quantity(1.0, "m") + U.Quantity(1.0, "s")

    def test_to(self):
        q = U.Quantity(1000.0, "mm").to("m")
        self.assertAlmostEqual(q.value, 1.0)

    def test_scalar_mul(self):
        q = U.Quantity(2.0, "Nm") * 3
        self.assertAlmostEqual(q.value, 6.0)
        q2 = 3 * U.Quantity(2.0, "Nm")
        self.assertAlmostEqual(q2.value, 6.0)

    def test_scalar_div(self):
        q = U.Quantity(6.0, "Nm") / 3
        self.assertAlmostEqual(q.value, 2.0)

    def test_neg(self):
        q = -U.Quantity(2.0, "Nm")
        self.assertAlmostEqual(q.value, -2.0)


if __name__ == "__main__":
    unittest.main()