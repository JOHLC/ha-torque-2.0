"""Comprehensive test for all sensor types to verify unit normalization and device class support."""

from __future__ import annotations

import pytest
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)

from custom_components.torque.sensor import TorqueSensor


class TestComprehensiveRawValuePassthrough:
    """Test that sensor types use Home Assistant standard units and device classes."""

    @pytest.mark.parametrize(
        "name,unit,pid,expected_unit,expected_device_class,description",
        [
            # Temperature sensors - OBD-II standard PIDs are corrected to Celsius
            (
                "Coolant Temperature",
                "°F",
                5,
                UnitOfTemperature.CELSIUS,
                SensorDeviceClass.TEMPERATURE,
                "OBD-II PID 0x05 corrected to Celsius",
            ),
            (
                "Air Intake Temperature",
                "°C",
                15,
                UnitOfTemperature.CELSIUS,
                SensorDeviceClass.TEMPERATURE,
                "Should normalize and set device class",
            ),
            ("Oil Temperature", "K", 23, "K", None, "Should preserve unknown unit"),
            # Speed sensors - should normalize and set device class
            (
                "Vehicle Speed",
                "mph",
                13,
                UnitOfSpeed.MILES_PER_HOUR,
                SensorDeviceClass.SPEED,
                "Should normalize and set device class",
            ),
            (
                "Vehicle Speed",
                "km/h",
                13,
                UnitOfSpeed.KILOMETERS_PER_HOUR,
                SensorDeviceClass.SPEED,
                "Should normalize and set device class",
            ),
            (
                "Vehicle Speed",
                "kmh",
                13,
                UnitOfSpeed.KILOMETERS_PER_HOUR,
                SensorDeviceClass.SPEED,
                "Should normalize variant",
            ),
            # Pressure sensors - should normalize and set device class
            (
                "Intake Manifold Pressure",
                "kPa",
                11,
                UnitOfPressure.KPA,
                SensorDeviceClass.PRESSURE,
                "Should normalize and set device class",
            ),
            (
                "Fuel Pressure",
                "psi",
                10,
                UnitOfPressure.PSI,
                SensorDeviceClass.PRESSURE,
                "Should normalize and set device class",
            ),
            (
                "Barometric Pressure",
                "bar",
                51,
                UnitOfPressure.BAR,
                SensorDeviceClass.PRESSURE,
                "Should normalize and set device class",
            ),
            # Voltage sensors - should normalize and set device class
            (
                "Battery Voltage",
                "V",
                14,
                UnitOfElectricPotential.VOLT,
                SensorDeviceClass.VOLTAGE,
                "Should normalize and set device class",
            ),
            (
                "Battery Voltage",
                "volt",
                14,
                UnitOfElectricPotential.VOLT,
                SensorDeviceClass.VOLTAGE,
                "Should normalize variant",
            ),
            # Distance sensors - should normalize and set device class
            (
                "Trip Distance",
                "miles",
                161,
                UnitOfLength.MILES,
                SensorDeviceClass.DISTANCE,
                "Should normalize and set device class",
            ),
            (
                "Trip Distance",
                "km",
                161,
                UnitOfLength.KILOMETERS,
                SensorDeviceClass.DISTANCE,
                "Should normalize and set device class",
            ),
            # No normalization for these
            ("Engine RPM", "rpm", 12, "rpm", None, "Should preserve RPM"),
            ("Engine Load", "%", 4, "%", None, "Should preserve percentage"),
            (
                "Custom Sensor",
                "custom_unit",
                200,
                "custom_unit",
                None,
                "Should preserve custom units",
            ),
        ],
    )
    def test_sensor_unit_normalization_and_device_class(
        self, name, unit, pid, expected_unit, expected_device_class, description
    ):
        """Test that sensor units are normalized to Home Assistant constants and device classes are set appropriately."""
        sensor = TorqueSensor(name, unit, pid, "TestCar", {})

        assert (
            sensor._attr_native_unit_of_measurement == expected_unit
        ), f"{name}: Expected unit '{expected_unit}', got '{sensor._attr_native_unit_of_measurement}'. {description}"

        assert (
            sensor._attr_device_class == expected_device_class
        ), f"{name}: Expected device_class '{expected_device_class}', got '{sensor._attr_device_class}'. {description}"

    def test_all_sensor_types_accept_all_numeric_values(self):
        """Test that all sensor types accept all numeric values without filtering."""
        sensor_types = [
            ("Vehicle Speed", "mph", 13),
            ("Coolant Temperature", "°F", 5),
            ("Engine RPM", "rpm", 12),
            ("Intake Pressure", "kPa", 11),
            ("Battery Voltage", "V", 14),
            ("Engine Load", "%", 4),
            ("Fuel Flow", "L/h", 94),
            ("Trip Distance", "miles", 161),
            ("Engine Torque", "Nm", 98),
            ("Timing Advance", "°", 14),
        ]

        test_values = [
            0.0,  # Zero
            -50.0,  # Negative
            0.5,  # Small positive
            100.0,  # Normal positive
            999999.9,  # Large positive
        ]

        for name, unit, pid in sensor_types:
            sensor = TorqueSensor(name, unit, pid, "TestCar", {})

            for value in test_values:
                # All values should be considered valid (no filtering)
                assert sensor._is_value_valid(
                    value
                ), f"{name} rejected value {value}, but should accept all numeric values"

    def test_sensor_specific_significance_thresholds(self):
        """Test that different sensor types have appropriate significance thresholds."""
        test_cases = [
            ("Vehicle Speed", "mph", 13, 1.0),  # Speed: 1 unit
            ("Coolant Temperature", "°F", 5, 0.5),  # Temperature: 0.5 degrees
            ("Engine RPM", "rpm", 12, 50.0),  # RPM: 50 revolutions
            ("Battery Voltage", "V", 14, 0.1),  # Voltage: 0.1 volts
            ("Intake Pressure", "kPa", 11, 1.0),  # Pressure: 1 unit
            ("Engine Load", "%", 4, 0.1),  # Default: 0.1 for unmatched sensors
        ]

        for name, unit, pid, expected_threshold in test_cases:
            sensor = TorqueSensor(name, unit, pid, "TestCar", {})
            actual_threshold = sensor._get_significant_change_threshold()

            assert (
                actual_threshold == expected_threshold
            ), f"{name} has wrong significance threshold: expected {expected_threshold}, got {actual_threshold}"
