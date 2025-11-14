"""Test OBD-II unit correction for standard PIDs."""

from __future__ import annotations

import pytest
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfTemperature

from custom_components.torque.sensor import TorqueSensor, correct_unit_for_pid


class TestOBD2UnitCorrection:
    """Test OBD-II standard PID unit correction."""

    @pytest.mark.parametrize(
        "pid,input_unit,expected_unit,description",
        [
            # OBD-II standard temperature PIDs that always return Celsius
            (0x05, "°F", UnitOfTemperature.CELSIUS, "Engine Coolant Temperature"),
            (0x0F, "°F", UnitOfTemperature.CELSIUS, "Intake Air Temperature"),
            (0x46, "°F", UnitOfTemperature.CELSIUS, "Ambient Air Temperature"),
            (0x5C, "°F", UnitOfTemperature.CELSIUS, "Engine Oil Temperature"),
            (0x3C, "°F", UnitOfTemperature.CELSIUS, "Catalyst Temperature B1S1"),
            (0x3D, "°F", UnitOfTemperature.CELSIUS, "Catalyst Temperature B2S1"),
            (0x3E, "°F", UnitOfTemperature.CELSIUS, "Catalyst Temperature B1S2"),
            (0x3F, "°F", UnitOfTemperature.CELSIUS, "Catalyst Temperature B2S2"),
            # Non-standard PIDs should not be corrected
            (0x221E1C, "°F", "°F", "Custom Ford Transmission Temp - unchanged"),
            (0x2203CA, "°F", "°F", "Custom Ford IAT2 - unchanged"),
            # Celsius input should remain unchanged
            (0x0F, "°C", "°C", "Intake Air Temperature with Celsius"),
            (0x05, "°C", "°C", "Coolant Temperature with Celsius"),
        ],
    )
    def test_correct_unit_for_pid(self, pid, input_unit, expected_unit, description):
        """Test that correct_unit_for_pid corrects units for OBD-II standard PIDs."""
        result = correct_unit_for_pid(pid, input_unit)
        assert (
            result == expected_unit
        ), f"{description}: Expected {expected_unit}, got {result}"

    def test_intake_air_temperature_sensor_with_fahrenheit_label(self):
        """Test Intake Air Temperature sensor correctly uses Celsius despite F label.

        This is the main bug fix: PID 0x0F always returns Celsius per OBD-II spec,
        but Torque may send unit as "°F" based on user display preferences.
        """
        # Create sensor with PID 0x0F and unit "°F" (as Torque might send)
        sensor = TorqueSensor(
            name="Intake Air Temperature",
            unit="°F",  # Wrong unit from Torque
            pid=0x0F,
            vehicle="Test Car",
            options={},
        )

        # The sensor should be corrected to use Celsius
        assert sensor._attr_native_unit_of_measurement == UnitOfTemperature.CELSIUS
        assert sensor._attr_device_class == SensorDeviceClass.TEMPERATURE

    def test_coolant_temperature_sensor_with_fahrenheit_label(self):
        """Test Engine Coolant Temperature sensor correctly uses Celsius despite F label."""
        sensor = TorqueSensor(
            name="Engine Coolant Temperature",
            unit="°F",  # Wrong unit from Torque
            pid=0x05,
            vehicle="Test Car",
            options={},
        )

        # The sensor should be corrected to use Celsius
        assert sensor._attr_native_unit_of_measurement == UnitOfTemperature.CELSIUS
        assert sensor._attr_device_class == SensorDeviceClass.TEMPERATURE

    def test_ambient_temperature_sensor_with_fahrenheit_label(self):
        """Test Ambient Air Temperature sensor correctly uses Celsius despite F label."""
        sensor = TorqueSensor(
            name="Ambient Air Temperature",
            unit="°F",  # Wrong unit from Torque
            pid=0x46,
            vehicle="Test Car",
            options={},
        )

        # The sensor should be corrected to use Celsius
        assert sensor._attr_native_unit_of_measurement == UnitOfTemperature.CELSIUS
        assert sensor._attr_device_class == SensorDeviceClass.TEMPERATURE

    def test_custom_temperature_sensor_not_corrected(self):
        """Test that custom (non-OBD-II) temperature sensors are not corrected.

        Custom PIDs like Ford-specific PIDs should respect the unit from Torque
        because they may actually return data in the specified unit.
        """
        # Ford custom transmission temp PID
        sensor = TorqueSensor(
            name="[FORD]Transmission Temp",
            unit="°F",
            pid=0x221E1C,
            vehicle="Test Car",
            options={},
        )

        # Custom PIDs should keep their original unit
        assert sensor._attr_native_unit_of_measurement == UnitOfTemperature.FAHRENHEIT
        assert sensor._attr_device_class == SensorDeviceClass.TEMPERATURE

    def test_intake_air_temp_with_celsius_label_unchanged(self):
        """Test Intake Air Temperature sensor with correct Celsius label is unchanged."""
        sensor = TorqueSensor(
            name="Intake Air Temperature",
            unit="°C",
            pid=0x0F,
            vehicle="Test Car",
            options={},
        )

        # Should remain Celsius
        assert sensor._attr_native_unit_of_measurement == UnitOfTemperature.CELSIUS
        assert sensor._attr_device_class == SensorDeviceClass.TEMPERATURE

    def test_real_world_scenario_intake_air_temp(self):
        """Test real-world scenario from issue: Intake Air Temperature.

        Issue: Torque sends unit as "°F" but actual data is in Celsius.
        The value 11.0°C (51.8°F) should be displayed as 11.0°C, not 11.0°F.
        """
        from unittest.mock import Mock

        sensor = TorqueSensor(
            name="Intake Air Temperature",
            unit="°F",  # Torque sends this
            pid=0x0F,
            vehicle="Test Car",
            options={},
        )

        # Verify unit is corrected to Celsius
        assert sensor._attr_native_unit_of_measurement == UnitOfTemperature.CELSIUS

        # Mock the async_write_ha_state method
        sensor.async_write_ha_state = Mock()

        # Simulate receiving a value (11.0°C from the example payload)
        sensor.async_on_update("11.0")

        # Value should be stored as-is (11.0) with Celsius unit
        assert sensor._attr_native_value == 11.0
        # Home Assistant will now correctly display this as 11°C
        # instead of incorrectly showing it as 11°F

    def test_all_obd2_standard_temperature_pids_corrected(self):
        """Test that all OBD-II standard temperature PIDs are corrected."""
        obd2_temp_pids = [
            (0x05, "Engine Coolant Temperature"),
            (0x0F, "Intake Air Temperature"),
            (0x46, "Ambient Air Temperature"),
            (0x5C, "Engine Oil Temperature"),
            (0x3C, "Catalyst Temperature (Bank 1, Sensor 1)"),
            (0x3D, "Catalyst Temperature (Bank 2, Sensor 1)"),
            (0x3E, "Catalyst Temperature (Bank 1, Sensor 2)"),
            (0x3F, "Catalyst Temperature (Bank 2, Sensor 2)"),
        ]

        for pid, name in obd2_temp_pids:
            # Test with Fahrenheit label (should be corrected to Celsius)
            sensor = TorqueSensor(
                name=name,
                unit="°F",
                pid=pid,
                vehicle="Test Car",
                options={},
            )

            assert (
                sensor._attr_native_unit_of_measurement == UnitOfTemperature.CELSIUS
            ), f"PID 0x{pid:02X} ({name}) should be corrected to Celsius"
            assert sensor._attr_device_class == SensorDeviceClass.TEMPERATURE

    def test_non_temperature_pids_unchanged(self):
        """Test that non-temperature PIDs are not affected by correction."""
        # Speed sensor
        speed_sensor = TorqueSensor(
            name="Vehicle Speed",
            unit="mph",
            pid=0x0D,
            vehicle="Test Car",
            options={},
        )
        assert (
            speed_sensor._attr_native_unit_of_measurement != UnitOfTemperature.CELSIUS
        )

        # Pressure sensor
        pressure_sensor = TorqueSensor(
            name="Intake Manifold Pressure",
            unit="psi",
            pid=0x0B,
            vehicle="Test Car",
            options={},
        )
        assert (
            pressure_sensor._attr_native_unit_of_measurement
            != UnitOfTemperature.CELSIUS
        )

        # RPM sensor
        rpm_sensor = TorqueSensor(
            name="Engine RPM",
            unit="rpm",
            pid=0x0C,
            vehicle="Test Car",
            options={},
        )
        assert rpm_sensor._attr_native_unit_of_measurement != UnitOfTemperature.CELSIUS
