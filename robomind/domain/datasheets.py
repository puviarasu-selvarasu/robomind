"""Curated datasheets for common hobby robotics components.

Values are typical / nominal. Real parts vary by vendor and batch.
Always verify against the specific part before trusting a design.
"""
from __future__ import annotations

from typing import Any


SERVOS: dict[str, dict[str, Any]] = {
    "SG90": {
        "type": "servo",
        "torque_kgcm": 1.8,
        "torque_Nm": 1.8 * 0.0980665,
        "speed_s_per_60deg": 0.10,
        "voltage_min_V": 4.8,
        "voltage_max_V": 6.0,
        "stall_current_A": 0.7,
        "idle_current_mA": 10,
        "weight_g": 9,
        "rotation_deg": 180,
    },
    "MG90S": {
        "type": "servo",
        "torque_kgcm": 2.2,
        "torque_Nm": 2.2 * 0.0980665,
        "speed_s_per_60deg": 0.10,
        "voltage_min_V": 4.8,
        "voltage_max_V": 6.0,
        "stall_current_A": 1.0,
        "weight_g": 13,
        "rotation_deg": 180,
    },
    "MG996R": {
        "type": "servo",
        "torque_kgcm": 11.0,
        "torque_Nm": 11.0 * 0.0980665,
        "speed_s_per_60deg": 0.14,
        "voltage_min_V": 4.8,
        "voltage_max_V": 7.2,
        "stall_current_A": 2.5,
        "weight_g": 55,
        "rotation_deg": 180,
    },
    "DS3218": {
        "type": "servo",
        "torque_kgcm": 20.0,
        "torque_Nm": 20.0 * 0.0980665,
        "speed_s_per_60deg": 0.16,
        "voltage_min_V": 4.8,
        "voltage_max_V": 6.8,
        "stall_current_A": 3.0,
        "weight_g": 60,
        "rotation_deg": 270,
    },
}


MOTORS: dict[str, dict[str, Any]] = {
    "N20_30RPM": {
        "type": "dc_gear_motor",
        "nominal_voltage_V": 6.0,
        "no_load_rpm": 30,
        "stall_torque_kgcm": 3.0,
        "stall_torque_Nm": 3.0 * 0.0980665,
        "stall_current_A": 1.2,
        "no_load_current_mA": 40,
        "gear_ratio": 300,
    },
    "28BYJ-48": {
        "type": "stepper",
        "nominal_voltage_V": 5.0,
        "steps_per_rev": 2048,   # with internal 1:64 gearing
        "phase_current_A": 0.16,
        "holding_torque_kgcm": 0.3,
        "holding_torque_Nm": 0.3 * 0.0980665,
        "weight_g": 30,
    },
    "NEMA17_17HS4401": {
        "type": "stepper",
        "nominal_voltage_V": 12.0,
        "steps_per_rev": 200,
        "phase_current_A": 1.7,
        "holding_torque_Nm": 0.4,
        "weight_g": 280,
    },
}


MCUS: dict[str, dict[str, Any]] = {
    "Arduino_Uno": {
        "type": "mcu",
        "mcu": "ATmega328P",
        "clock_MHz": 16,
        "flash_KB": 32,
        "ram_KB": 2,
        "io_voltage_V": 5.0,
        "digital_pins": 14,
        "pwm_pins": 6,
        "adc_pins": 6,
        "adc_bits": 10,
        "max_pin_current_mA": 40,
        "max_total_current_mA": 200,
    },
    "ESP32_DevKitC": {
        "type": "mcu",
        "mcu": "ESP32",
        "clock_MHz": 240,
        "flash_MB": 4,
        "ram_KB": 520,
        "io_voltage_V": 3.3,
        "digital_pins": 34,
        "pwm_pins": 16,
        "adc_pins": 18,
        "adc_bits": 12,
        "wifi": True,
        "bluetooth": True,
        "max_pin_current_mA": 40,
    },
    "RP2040_Pico": {
        "type": "mcu",
        "mcu": "RP2040",
        "clock_MHz": 133,
        "flash_MB": 2,
        "ram_KB": 264,
        "io_voltage_V": 3.3,
        "digital_pins": 26,
        "pwm_pins": 16,
        "adc_pins": 3,
        "adc_bits": 12,
        "max_pin_current_mA": 16,
    },
    "STM32F103_BluePill": {
        "type": "mcu",
        "mcu": "STM32F103C8",
        "clock_MHz": 72,
        "flash_KB": 64,
        "ram_KB": 20,
        "io_voltage_V": 3.3,
        "digital_pins": 37,
        "pwm_pins": 15,
        "adc_pins": 10,
        "adc_bits": 12,
        "max_pin_current_mA": 20,
    },
}


SENSORS: dict[str, dict[str, Any]] = {
    "MPU6050": {
        "type": "imu",
        "voltage_V": 3.3,
        "current_mA": 4,
        "gyro_range_dps": (250, 500, 1000, 2000),
        "accel_range_g": (2, 4, 8, 16),
        "interface": "I2C",
        "i2c_addr": 0x68,
    },
    "HC-SR04": {
        "type": "ultrasonic_distance",
        "voltage_V": 5.0,
        "current_mA": 15,
        "range_cm": (2, 400),
        "resolution_cm": 0.3,
        "interface": "GPIO_trig_echo",
    },
    "BMP280": {
        "type": "pressure_temperature",
        "voltage_V": 3.3,
        "current_mA": 1,
        "pressure_range_hPa": (300, 1100),
        "interface": "I2C_SPI",
        "i2c_addr": 0x76,
    },
    "DHT22": {
        "type": "temperature_humidity",
        "voltage_V": 3.3,
        "current_mA": 1.5,
        "temp_range_C": (-40, 80),
        "humidity_range_pct": (0, 100),
        "interface": "one_wire",
    },
    "VL53L0X": {
        "type": "tof_distance",
        "voltage_V": 2.8,
        "current_mA": 10,
        "range_m": 2.0,
        "interface": "I2C",
        "i2c_addr": 0x29,
    },
}


BATTERIES: dict[str, dict[str, Any]] = {
    "LiPo_1S": {
        "type": "lipo",
        "nominal_V": 3.7,
        "full_V": 4.2,
        "empty_V": 3.0,
        "capacity_mAh": 1000,
        "max_discharge_C": 20,
        "usable_fraction": 0.8,
    },
    "LiPo_3S": {
        "type": "lipo",
        "nominal_V": 11.1,
        "full_V": 12.6,
        "empty_V": 9.0,
        "capacity_mAh": 2200,
        "max_discharge_C": 25,
        "usable_fraction": 0.8,
    },
    "LiIon_18650": {
        "type": "li_ion",
        "nominal_V": 3.7,
        "full_V": 4.2,
        "empty_V": 2.8,
        "capacity_mAh": 2500,
        "max_discharge_C": 5,
        "usable_fraction": 0.85,
    },
    "AA_NiMH": {
        "type": "nimh",
        "nominal_V": 1.2,
        "full_V": 1.45,
        "empty_V": 0.9,
        "capacity_mAh": 2000,
        "max_discharge_C": 2,
        "usable_fraction": 0.9,
    },
}


_ALL: dict[str, dict[str, dict[str, Any]]] = {
    "servos": SERVOS,
    "motors": MOTORS,
    "mcus": MCUS,
    "sensors": SENSORS,
    "batteries": BATTERIES,
}


def lookup(name: str) -> dict[str, Any] | None:
    """Return the datasheet for a component, or None if not found."""
    key = name.strip()
    for table in _ALL.values():
        if key in table:
            return table[key]
        # case-insensitive fallback
        for k, v in table.items():
            if k.lower() == key.lower():
                return v
    return None


def category_of(name: str) -> str | None:
    key = name.strip().lower()
    for cat, table in _ALL.items():
        for k in table:
            if k.lower() == key:
                return cat
    return None


def search(query: str, *, limit: int = 10) -> list[tuple[str, str]]:
    """Substring search across all components. Returns list of (name, category)."""
    q = query.strip().lower()
    if not q:
        return []
    hits: list[tuple[str, str]] = []
    for cat, table in _ALL.items():
        for name in table:
            if q in name.lower():
                hits.append((name, cat))
                if len(hits) >= limit:
                    return hits
    return hits


def all_names() -> dict[str, tuple[str, ...]]:
    """Category -> tuple of names."""
    return {cat: tuple(sorted(t.keys())) for cat, t in _ALL.items()}