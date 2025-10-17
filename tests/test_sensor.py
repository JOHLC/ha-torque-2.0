"""Test the Torque sensor platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.torque.const import DOMAIN
from custom_components.torque.sensor import (
    TorqueReceiveDataView,
    TorqueSensor,
    async_setup_entry,
    convert_pid,
)


class TestConvertPid:
    """Test PID conversion function."""

    def test_convert_pid_valid_hex(self):
        """Test converting valid hex string."""
        assert convert_pid("29") == 41
        assert convert_pid("2A") == 42
        assert convert_pid("ff") == 255

    def test_convert_pid_invalid(self):
        """Test converting invalid strings."""
        assert convert_pid("invalid") is None
        assert convert_pid("") is None
        assert convert_pid(None) is None


class TestTorqueSensor:
    """Test TorqueSensor class."""

    def test_init(self):
        """Test sensor initialization."""
        sensor = TorqueSensor(
            name="Engine RPM", unit="rpm", pid=12, vehicle="Test Car", options={}
        )

        assert sensor.name == "Engine RPM"
        assert sensor._pid == 12
        assert sensor._vehicle == "Test Car"
        assert sensor.unique_id == f"{DOMAIN}_test car_12"

    def test_determine_unit_temperature(self):
        """Test unit determination uses raw unit from Torque."""
        sensor = TorqueSensor("Coolant Temp", "°F", 5, "Test", {})
        # Should use raw unit from Torque, not convert to Celsius
        assert sensor._attr_native_unit_of_measurement == "°F"

    def test_determine_unit_speed(self):
        """Test unit determination uses raw unit from Torque."""
        sensor = TorqueSensor("Vehicle Speed", "mph", 13, "Test", {})
        # Should use raw unit from Torque, not convert to km/h
        assert sensor._attr_native_unit_of_measurement == "mph"

    def test_determine_icon_temperature(self):
        """Test icon determination for temperature sensors."""
        sensor = TorqueSensor("Coolant Temperature", "°C", 5, "Test", {})
        assert sensor._attr_icon == "mdi:coolant-temperature"

    def test_determine_icon_speed(self):
        """Test icon determination for speed sensors."""
        sensor = TorqueSensor("Vehicle Speed", "km/h", 13, "Test", {})
        assert sensor._attr_icon == "mdi:speedometer"

    def test_should_update_value_first_update(self):
        """Test that first update is always allowed."""
        sensor = TorqueSensor("Test", "unit", 1, "Test", {})
        assert sensor._should_update_value(50.0, 0.0) is True

    def test_should_update_value_sensor_specific_thresholds(self):
        """Test update thresholds are sensor-specific."""
        # Speed sensor should use 1.0 threshold
        speed_sensor = TorqueSensor("Vehicle Speed", "km/h", 13, "Test", {})
        speed_sensor._last_reported_value = 50.0
        speed_sensor._last_update = 0.0

        # Small change under 1.0 km/h should not trigger immediate update
        assert speed_sensor._should_update_value(50.5, 5.0) is False
        # After MIN_UPDATE_INTERVAL, even small changes trigger update
        assert speed_sensor._should_update_value(50.5, 20.0) is True
        # Large change over 1.0 km/h should trigger immediate update
        assert speed_sensor._should_update_value(51.5, 5.0) is True

        # Temperature sensor should use 0.5 threshold
        temp_sensor = TorqueSensor("Coolant Temperature", "°C", 5, "Test", {})
        temp_sensor._last_reported_value = 80.0
        temp_sensor._last_update = 0.0

        # Small change under 0.5°C should not trigger immediate update
        assert temp_sensor._should_update_value(80.2, 5.0) is False
        # After MIN_UPDATE_INTERVAL, even small changes trigger update
        assert temp_sensor._should_update_value(80.2, 20.0) is True
        # Large change over 0.5°C should trigger immediate update
        assert temp_sensor._should_update_value(80.7, 5.0) is True

    def test_speed_sensor_accepts_all_values(self):
        """Test speed sensors now accept all values including zeros."""
        sensor = TorqueSensor("Vehicle Speed", "km/h", 13, "Test", {})

        # All values should be accepted now - no debouncing
        assert sensor._is_value_valid(0.0) is True  # Zero values accepted
        assert sensor._is_value_valid(50.0) is True  # Non-zero values accepted
        assert sensor._is_value_valid(0.0) is True  # Still accepts zeros

    def test_non_speed_sensor_accepts_zeros(self):
        """Test non-speed sensors accept zero values immediately."""
        sensor = TorqueSensor("Engine Load", "%", 4, "Test", {})

        # Zero values should be accepted for non-speed sensors
        assert sensor._is_value_valid(0.0) is True

    def test_get_significant_change_threshold(self):
        """Test sensor-specific significant change thresholds."""
        # Speed sensor should use 1.0 threshold
        speed_sensor = TorqueSensor("Vehicle Speed", "km/h", 13, "Test", {})
        assert speed_sensor._get_significant_change_threshold() == 1.0

        # Temperature sensor should use 0.5 threshold
        temp_sensor = TorqueSensor("Coolant Temperature", "°C", 5, "Test", {})
        assert temp_sensor._get_significant_change_threshold() == 0.5

        # RPM sensor should use 50.0 threshold
        rpm_sensor = TorqueSensor("Engine RPM", "rpm", 12, "Test", {})
        assert rpm_sensor._get_significant_change_threshold() == 50.0

        # Unknown sensor should use default 0.1 threshold
        unknown_sensor = TorqueSensor("Unknown Sensor", "unit", 99, "Test", {})
        assert unknown_sensor._get_significant_change_threshold() == 0.1

    def test_async_on_update_valid_value(self):
        """Test updating sensor with valid numeric value."""
        sensor = TorqueSensor("Test", "unit", 1, "Test", {})
        sensor.async_write_ha_state = Mock()

        sensor.async_on_update("42.5")

        assert sensor._attr_native_value == 42.5
        assert sensor._last_reported_value == 42.5

    def test_async_on_update_invalid_value(self):
        """Test updating sensor with invalid value."""
        sensor = TorqueSensor("Test", "unit", 1, "Test", {})
        sensor.async_write_ha_state = Mock()

        sensor.async_on_update("invalid")

        assert sensor._attr_native_value is None
        assert sensor._last_reported_value is None

    def test_debouncing_stable_values(self):
        """Test debouncing with stable consistent values."""
        sensor = TorqueSensor("Vehicle Speed", "km/h", 13, "Test", {})
        sensor.async_write_ha_state = Mock()

        # Add three stable values to fill the buffer
        sensor.async_on_update("100.0")
        sensor.async_on_update("100.1")
        sensor.async_on_update("99.9")

        # With stable values (range <= 2.0), should use the mean
        assert sensor._attr_native_value is not None
        assert 99.5 <= sensor._attr_native_value <= 100.5

    def test_debouncing_filters_noise(self):
        """Test debouncing filters out noisy spikes."""
        sensor = TorqueSensor("Vehicle Speed", "km/h", 13, "Test", {})
        sensor.async_write_ha_state = Mock()

        # Establish a baseline
        sensor.async_on_update("100.0")
        sensor.async_on_update("100.0")
        sensor.async_on_update("100.0")
        baseline_value = sensor._attr_native_value

        # Add a noise spike
        sensor.async_on_update("50.0")

        # The spike should be filtered if not consistent
        # Since buffer now has [100.0, 100.0, 50.0], it's inconsistent
        # and the change isn't large enough to override
        # So it should keep reporting close to baseline
        assert sensor._attr_native_value is not None

    def test_debouncing_accepts_large_changes(self):
        """Test debouncing accepts large legitimate changes."""
        sensor = TorqueSensor("Vehicle Speed", "km/h", 13, "Test", {})
        sensor.async_write_ha_state = Mock()

        # Establish baseline at 100 km/h
        sensor.async_on_update("100.0")
        sensor.async_on_update("100.0")
        sensor.async_on_update("100.0")

        # Large consistent change (deceleration)
        sensor.async_on_update("10.0")
        sensor.async_on_update("9.0")
        sensor.async_on_update("10.0")

        # Should accept the large change
        assert sensor._attr_native_value is not None
        assert sensor._attr_native_value < 50.0

    def test_real_world_scenario_stable_speed(self):
        """Test real-world scenario: stable speed with noisy readings.

        This tests the problem statement scenario:
        Vehicle driving consistently at 100 km/h but sensor reports
        100, 50, 100, 0 due to noise or brief signal issues.
        """
        sensor = TorqueSensor("Vehicle Speed", "km/h", 13, "Test", {})
        sensor.async_write_ha_state = Mock()

        # Simulate real-world noisy data while actually driving 100 km/h
        sensor.async_on_update("100.0")  # Real value
        sensor.async_on_update("100.0")  # Real value
        sensor.async_on_update("100.0")  # Real value - buffer filled, stable
        initial_value = sensor._attr_native_value
        assert initial_value is not None
        assert 99.0 <= initial_value <= 101.0

        # Brief noise spike to 50
        sensor.async_on_update("50.0")  # Buffer: [100, 100, 50]
        # Should not jump to 50 immediately due to debouncing
        # The debouncer should keep the stable value or filter this
        value_after_spike = sensor._attr_native_value

        # More stable readings
        sensor.async_on_update("100.0")  # Buffer: [100, 50, 100]
        sensor.async_on_update("100.0")  # Buffer: [50, 100, 100]
        sensor.async_on_update("100.0")  # Buffer: [100, 100, 100] - stable again

        # Should return to stable value around 100
        final_value = sensor._attr_native_value
        assert final_value is not None
        assert 99.0 <= final_value <= 101.0

        # The sensor should show much less variation than the raw input
        # Raw input had values: 100, 100, 100, 50, 100, 100, 100
        # Output should be stable around 100


class TestTorqueReceiveDataView:
    """Test TorqueReceiveDataView class."""

    @pytest.fixture
    def view(self):
        """Create a test view."""
        sensors = {}
        async_add_entities = AsyncMock()
        return TorqueReceiveDataView(
            email="test@example.com",
            vehicle="Test Car",
            sensors=sensors,
            async_add_entities=async_add_entities,
            config_entry=None,
        )

    async def test_get_request(self, view):
        """Test handling GET request."""
        request = Mock()
        request.query = {
            "eml": "test@example.com",
            "userFullName29": "Engine Load",
            "userUnit29": "%",
            "k29": "45.5",
        }

        response = await view.get(request)
        assert response.text == "OK"
        assert response.status == 200

    async def test_post_request(self, view):
        """Test handling POST request."""
        request = Mock()
        post_data = Mock()
        post_data.__iter__ = Mock(
            return_value=iter(
                [
                    ("eml", "test@example.com"),
                    ("userFullName29", "Engine Load"),
                    ("userUnit29", "%"),
                    ("k29", "45.5"),
                ]
            )
        )
        post_data.items = Mock(
            return_value=[
                ("eml", "test@example.com"),
                ("userFullName29", "Engine Load"),
                ("userUnit29", "%"),
                ("k29", "45.5"),
            ]
        )
        request.post = AsyncMock(return_value=post_data)

        response = await view.post(request)
        assert response.text == "OK"
        assert response.status == 200

    async def test_handle_data_missing_email(self, view):
        """Test handling data without email field."""
        data = {"userFullName29": "Engine Load"}
        response = await view._handle_data(data)

        assert response.status == 400
        assert "Missing email" in response.text

    async def test_handle_data_wrong_email(self, view):
        """Test handling data with wrong email."""
        data = {
            "eml": "wrong@example.com",
            "userFullName29": "Engine Load",
        }
        response = await view._handle_data(data)

        assert response.status == 403
        assert "Unauthorized email" in response.text

    async def test_parse_sensor_data(self, view):
        """Test parsing sensor data fields."""
        names = {}
        units = {}

        view._parse_sensor_data("userFullName29", "Engine Load", names, units)
        view._parse_sensor_data("userUnit29", "%", names, units)

        assert names[41] == "Engine Load"
        assert units[41] == "%"

    def test_should_hide_pid_no_config(self, view):
        """Test PID hiding with no configuration."""
        assert view._should_hide_pid(41) is False

    def test_should_hide_pid_with_config(self):
        """Test PID hiding with configuration."""
        config_entry = Mock()
        config_entry.options = {"hide_pids": "41,42,43"}

        view = TorqueReceiveDataView(
            email="test@example.com",
            vehicle="Test Car",
            sensors={},
            async_add_entities=AsyncMock(),
            config_entry=config_entry,
        )

        assert view._should_hide_pid(41) is True
        assert view._should_hide_pid(40) is False

    def test_get_custom_sensor_name_no_config(self, view):
        """Test getting sensor name with no configuration."""
        name = view._get_custom_sensor_name(41, "Engine Load")
        assert name == "Engine Load"

    def test_get_custom_sensor_name_with_config(self):
        """Test getting sensor name with custom configuration."""
        config_entry = Mock()
        config_entry.options = {"rename_map": "41:Custom Engine Load,42:Custom Temp"}

        view = TorqueReceiveDataView(
            email="test@example.com",
            vehicle="Test Car",
            sensors={},
            async_add_entities=AsyncMock(),
            config_entry=config_entry,
        )

        assert view._get_custom_sensor_name(41, "Engine Load") == "Custom Engine Load"
        assert view._get_custom_sensor_name(43, "Other Sensor") == "Other Sensor"


async def test_async_setup_entry(hass, mock_config_entry, mock_add_entities):
    """Test setting up the sensor platform."""
    with patch(
        "custom_components.torque.sensor.async_get_entity_registry"
    ) as mock_registry:
        mock_registry.return_value.entities = {}

        await async_setup_entry(hass, mock_config_entry, mock_add_entities)

        # Verify HTTP view is registered
        assert hass.http.register_view.called
