"""Test the Torque sensor platform."""
from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch
import pytest

from aiohttp import web
from homeassistant.core import HomeAssistant

from custom_components.torque.sensor import (
    TorqueReceiveDataView,
    TorqueSensor,
    async_setup_entry,
    convert_pid,
)
from custom_components.torque.const import DOMAIN


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
            name="Engine RPM",
            unit="rpm",
            pid=12,
            vehicle="Test Car",
            options={}
        )
        
        assert sensor.name == "Engine RPM"
        assert sensor._pid == 12
        assert sensor._vehicle == "Test Car"
        assert sensor.unique_id == f"{DOMAIN}_test car_12"

    def test_determine_unit_temperature(self):
        """Test unit determination for temperature sensors."""
        sensor = TorqueSensor("Coolant Temp", "°F", 5, "Test", {})
        assert sensor._attr_native_unit_of_measurement == "°C"

    def test_determine_unit_speed(self):
        """Test unit determination for speed sensors."""
        sensor = TorqueSensor("Vehicle Speed", "mph", 13, "Test", {})
        assert sensor._attr_native_unit_of_measurement == "km/h"

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

    def test_should_update_value_significant_change(self):
        """Test update on significant value change."""
        sensor = TorqueSensor("Test", "unit", 1, "Test", {})
        sensor._last_reported_value = 50.0
        sensor._last_update = 0.0
        
        # Significant change should trigger update
        assert sensor._should_update_value(51.0, 20.0) is True
        
        # Small change should not trigger update
        assert sensor._should_update_value(50.005, 20.0) is False

    async def test_async_on_update_valid_value(self):
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
        post_data.__iter__ = Mock(return_value=iter([
            ("eml", "test@example.com"),
            ("userFullName29", "Engine Load"),
            ("userUnit29", "%"),
            ("k29", "45.5"),
        ]))
        post_data.items = Mock(return_value=[
            ("eml", "test@example.com"),
            ("userFullName29", "Engine Load"),
            ("userUnit29", "%"),
            ("k29", "45.5"),
        ])
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