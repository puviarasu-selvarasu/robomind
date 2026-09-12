import math
import unittest

from robomind.domain import dynamics as D


class TestBasicTorque(unittest.TestCase):
    def test_torque_from_force(self):
        self.assertAlmostEqual(D.torque_from_force(10.0, 0.2), 2.0)

    def test_gravity_horizontal_max(self):
        # link horizontal → full gravity torque
        t = D.gravity_torque(1.0, 0.5, angle_rad=0.0)
        self.assertAlmostEqual(t, 1.0 * D.G * 0.5)

    def test_gravity_vertical_zero(self):
        t = D.gravity_torque(1.0, 0.5, angle_rad=math.pi / 2)
        self.assertAlmostEqual(t, 0.0, places=12)

    def test_inertial_torque(self):
        self.assertAlmostEqual(D.inertial_torque(0.1, 10.0), 1.0)

    def test_friction_torque(self):
        self.assertAlmostEqual(D.friction_torque(10.0, 0.2, 0.05), 0.1)


class TestInertia(unittest.TestCase):
    def test_rod(self):
        r = D.rod_inertia(1.0, 1.0)
        self.assertAlmostEqual(r.point_mass_end, 1.0)
        self.assertAlmostEqual(r.uniform_rod_end, 1.0 / 3.0)
        self.assertAlmostEqual(r.point_mass_center, 0.0)

    def test_parallel_axis(self):
        j = D.parallel_axis(0.1, 2.0, 0.5)
        self.assertAlmostEqual(j, 0.1 + 2.0 * 0.25)


class TestGears(unittest.TestCase):
    def test_output_torque(self):
        t = D.gear_output_torque(0.1, 50.0, efficiency=0.9)
        self.assertAlmostEqual(t, 0.1 * 50.0 * 0.9)

    def test_output_speed(self):
        w = D.gear_output_speed(100.0, 50.0)
        self.assertAlmostEqual(w, 2.0)

    def test_reflected_inertia(self):
        j = D.reflected_inertia(1.0, 10.0)
        self.assertAlmostEqual(j, 0.01)

    def test_bad_ratio_raises(self):
        with self.assertRaises(D.DynamicsError):
            D.gear_output_torque(1.0, 0.0)


class TestRequirement(unittest.TestCase):
    def test_total_and_margin(self):
        r = D.required_joint_torque(
            mass_kg=1.0, com_distance_m=0.3, angle_rad=0.0,
            inertia_kgm2=0.0, angular_accel_rad_s2=0.0,
            normal_force_N=0.0, friction_coeff=0.0, contact_radius_m=0.0,
            safety_margin=2.0,
        )
        self.assertAlmostEqual(r.gravity, 1.0 * D.G * 0.3)
        self.assertAlmostEqual(r.total, r.gravity)
        self.assertAlmostEqual(r.required_with_margin, r.gravity * 2.0)


if __name__ == "__main__":
    unittest.main()