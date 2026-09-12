import unittest

from robomind.domain import electronics as E


class TestOhm(unittest.TestCase):
    def test_voltage(self):
        self.assertAlmostEqual(E.ohm_voltage(0.5, 100.0), 50.0)

    def test_current(self):
        self.assertAlmostEqual(E.ohm_current(5.0, 100.0), 0.05)

    def test_resistance(self):
        self.assertAlmostEqual(E.ohm_resistance(5.0, 0.01), 500.0)

    def test_power(self):
        self.assertAlmostEqual(E.power(5.0, 0.2), 1.0)

    def test_power_resistive(self):
        self.assertAlmostEqual(E.power_resistive(0.1, 100.0), 1.0)

    def test_current_zero_resistance_raises(self):
        with self.assertRaises(E.ElectronicsError):
            E.ohm_current(5.0, 0.0)


class TestPWM(unittest.TestCase):
    def test_duty_50(self):
        self.assertAlmostEqual(E.pwm_duty(0.001, 0.002), 0.5)

    def test_duty_invalid(self):
        with self.assertRaises(E.ElectronicsError):
            E.pwm_duty(0.003, 0.002)

    def test_avg_voltage(self):
        self.assertAlmostEqual(E.pwm_avg_voltage(12.0, 0.25), 3.0)


class TestBattery(unittest.TestCase):
    def test_life_basic(self):
        # 2000 mAh at 1000 mA → 2 h
        self.assertAlmostEqual(E.battery_life_hours(2000.0, 1000.0), 2.0)

    def test_life_with_efficiency_and_usable(self):
        h = E.battery_life_hours(2000.0, 1000.0,
                                 efficiency=0.8, usable_fraction=0.5)
        self.assertAlmostEqual(h, 2000.0 * 0.5 * 0.8 / 1000.0)

    def test_life_invalid(self):
        with self.assertRaises(E.ElectronicsError):
            E.battery_life_hours(0.0, 100.0)


class TestMotor(unittest.TestCase):
    def test_current_from_torque(self):
        I = E.motor_current_from_torque(0.1, 0.05)
        self.assertAlmostEqual(I, 2.0)

    def test_torque_from_current(self):
        t = E.motor_torque_from_current(2.0, 0.05)
        self.assertAlmostEqual(t, 0.1)

    def test_back_emf(self):
        v = E.back_emf(10.0, 0.01)
        self.assertAlmostEqual(v, 0.1)


class TestDividersAndLeds(unittest.TestCase):
    def test_voltage_divider(self):
        v = E.voltage_divider(12.0, 1000.0, 1000.0)
        self.assertAlmostEqual(v, 6.0)

    def test_led_resistor(self):
        # 5 V supply, 2 V forward, 20 mA → 150 ohm
        r = E.led_series_resistor(5.0, 2.0, 20.0)
        self.assertAlmostEqual(r, 150.0)

    def test_led_invalid(self):
        with self.assertRaises(E.ElectronicsError):
            E.led_series_resistor(2.0, 3.0, 20.0)


class TestPowerBudget(unittest.TestCase):
    def test_budget(self):
        b = E.power_budget([("mcu", 50.0), ("servo", 700.0)],
                           peak_multiplier=1.5, safety_margin=1.2)
        self.assertAlmostEqual(b.total_mA, 750.0)
        self.assertAlmostEqual(b.peak_mA, 1125.0)
        self.assertAlmostEqual(b.recommended_supply_mA, 1350.0)


if __name__ == "__main__":
    unittest.main()