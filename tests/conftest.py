
"""Test fixtures for Torque integration tests."""
from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_NAME
from homeassistant.core import HomeAssistant

from custom_components.torque.const import DOMAIN


@pytest.fixture
def mock_config_entry():
    """Return a mock config entry."""
    return ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Test Vehicle",
        data={
            CONF_EMAIL: "test@example.com",
            CONF_NAME: "Test Vehicle",
        },
        options={
            "hide_pids": "",
            "rename_map": "",
            "unit_system": "metric",
        },
        source="user",
        entry_id="test_entry_id",
    )


@pytest.fixture
def mock_hass():
    """Return a mock Home Assistant instance."""
    hass = AsyncMock(spec=HomeAssistant)
    hass.data = {}
    hass.config_entries = AsyncMock()
    hass.http = AsyncMock()
    return hass


@pytest.fixture
def mock_add_entities():
    """Return a mock add_entities callback."""
    return AsyncMock()


@pytest.fixture
def mock_entity_registry():
    """Return a mock entity registry."""
    registry = Mock()
    registry.entities = {}
    return registry
