import math
import unittest

from robomind.domain import kinematics as K


class TestFK(unittest.TestCase):
    def test_single_link_along_x(self):
        x, y = K.fk_2d([1.0], [0.0])
        self.assertAlmostEqual(x, 1.0, places=12)
        self.assertAlmostEqual(y, 0.0, places=12)

    def test_single_link_90deg(self):
        x, y = K.fk_2d([1.0], [math.pi / 2])
        self.assertAlmostEqual(x, 0.0, places=12)
        self.assertAlmostEqual(y, 1.0, places=12)

    def test_two_link_known(self):
        # L1=1 along x, L2=1 along 90deg
        x, y = K.fk_2d([1.0, 1.0], [0.0, math.pi / 2])
        self.assertAlmostEqual(x, 1.0, places=12)
        self.assertAlmostEqual(y, 1.0, places=12)

    def test_relative_angles(self):
        # 0 then +90 = absolute 0, 90
        x, y = K.fk_2d_relative([1.0, 1.0], [0.0, math.pi / 2])
        self.assertAlmostEqual(x, 1.0, places=12)
        self.assertAlmostEqual(y, 1.0, places=12)

    def test_3d_base_yaw(self):
        x, y, z = K.fk_3d_from_planar([1.0], [0.0], base_yaw_rad=math.pi / 2)
        self.assertAlmostEqual(x, 0.0, places=12)
        self.assertAlmostEqual(y, 1.0, places=12)
        self.assertAlmostEqual(z, 0.0, places=12)

    def test_length_mismatch_raises(self):
        with self.assertRaises(K.KinematicsError):
            K.fk_2d([1.0, 1.0], [0.0])


class TestIK(unittest.TestCase):
    def test_workspace(self):
        r_min, r_max = K.workspace_2link(1.0, 1.0)
        self.assertAlmostEqual(r_min, 0.0)
        self.assertAlmostEqual(r_max, 2.0)

    def test_reach_along_x(self):
        # Target at (2, 0) with L1=L2=1 -> both solutions collapse to θ=(0,0)
        up, down = K.ik_2d_2link(2.0, 0.0, 1.0, 1.0)
        self.assertAlmostEqual(up.theta1_rad, 0.0, places=6)
        self.assertAlmostEqual(up.theta2_rad, 0.0, places=6)
        self.assertAlmostEqual(down.theta1_rad, 0.0, places=6)
        self.assertAlmostEqual(down.theta2_rad, 0.0, places=6)

    def test_reach_along_y(self):
        # Target (0, 2) with L1=L2=1 -> theta1 = pi/2, theta2 = 0
        up, down = K.ik_2d_2link(0.0, 2.0, 1.0, 1.0)
        self.assertAlmostEqual(up.theta1_rad, math.pi / 2, places=6)
        self.assertAlmostEqual(up.theta2_rad, 0.0, places=6)

    def test_ik_then_fk_roundtrip(self):
        L1, L2 = 1.5, 1.0
        for tx, ty in [(1.0, 1.0), (0.5, -1.2), (2.0, 0.3), (-1.0, 1.0)]:
            up, down = K.ik_2d_2link(tx, ty, L1, L2)
            for sol in (up, down):
                x, y = K.fk_2d([L1, L2], [sol.theta1_rad,
                                          sol.theta1_rad + sol.theta2_rad])
                self.assertAlmostEqual(x, tx, places=6)
                self.assertAlmostEqual(y, ty, places=6)

    def test_unreachable_too_far(self):
        with self.assertRaises(K.Unreachable):
            K.ik_2d_2link(5.0, 0.0, 1.0, 1.0)

    def test_unreachable_too_close(self):
        # With L1=L2=1, the wrist can't get closer than 0 (r_min=0), so pick
        # unequal links to get r_min > 0
        with self.assertRaises(K.Unreachable):
            K.ik_2d_2link(0.0, 0.0, 2.0, 1.0)

    def test_bad_link_raises(self):
        with self.assertRaises(K.KinematicsError):
            K.ik_2d_2link(1.0, 0.0, 0.0, 1.0)


class TestJacobian(unittest.TestCase):
    def test_singular_at_full_extension(self):
        # L1=L2=1, θ1=θ2=0 -> end effector at (2,0), singular
        det = K.jacobian_det_2d_2link(0.0, 0.0, 1.0, 1.0)
        self.assertAlmostEqual(det, 0.0, places=9)

    def test_non_singular(self):
        det = K.jacobian_det_2d_2link(math.pi / 4, math.pi / 4, 1.0, 1.0)
        self.assertNotAlmostEqual(det, 0.0, places=3)


class TestTrajectories(unittest.TestCase):
    def test_linear_endpoints(self):
        s = K.linear_interp(0.0, 10.0, 11)
        self.assertAlmostEqual(s[0], 0.0)
        self.assertAlmostEqual(s[-1], 10.0)
        self.assertEqual(len(s), 11)

    def test_linear_monotonic(self):
        s = K.linear_interp(0.0, 1.0, 5)
        for a, b in zip(s, s[1:]):
            self.assertLess(a, b)

    def test_cubic_zero_velocity_endpoints(self):
        s = K.cubic_interp(0.0, 1.0, 20, v0=0.0, v1=0.0, duration=1.0)
        self.assertAlmostEqual(s[0], 0.0, places=9)
        self.assertAlmostEqual(s[-1], 1.0, places=9)

    def test_trapezoidal_triangular(self):
        # short distance → triangular profile
        p = K.trapezoidal_profile(distance=0.1, max_vel=10.0, max_accel=1.0)
        self.assertEqual(p.t_cruise, 0.0)
        self.assertLess(p.peak_vel, p.max_vel)

    def test_trapezoidal_with_cruise(self):
        # long distance → trapezoidal profile (must exceed v²/a = 100)
        p = K.trapezoidal_profile(distance=200.0, max_vel=10.0, max_accel=1.0)
        self.assertGreater(p.t_cruise, 0.0)
        self.assertAlmostEqual(p.peak_vel, p.max_vel)

    def test_trapezoidal_samples_reach_target(self):
        p = K.trapezoidal_profile(distance=1.0, max_vel=2.0, max_accel=4.0)
        samples = p.sample(50)
        self.assertAlmostEqual(samples[0], 0.0, places=9)
        self.assertAlmostEqual(samples[-1], 1.0, places=9)


class TestAngleUtils(unittest.TestCase):
    def test_deg2rad(self):
        self.assertAlmostEqual(K.deg2rad(180.0), math.pi, places=12)

    def test_rad2deg(self):
        self.assertAlmostEqual(K.rad2deg(math.pi), 180.0, places=9)

    def test_normalize_angle(self):
        self.assertAlmostEqual(K.normalize_angle(3 * math.pi),
                               math.pi, places=9)
        self.assertAlmostEqual(K.normalize_angle(-3 * math.pi),
                               math.pi, places=9)


if __name__ == "__main__":
    unittest.main()