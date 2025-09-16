"""Test the Torque integration setup."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch
import pytest

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.torque import (
    async_setup,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.torque.const import DOMAIN


async def test_async_setup(hass: HomeAssistant) -> None:
    """Test the component setup."""
    config = {}
    result = await async_setup(hass, config)
    assert result is True


async def test_async_setup_entry(hass: HomeAssistant, mock_config_entry: ConfigEntry) -> None:
    """Test setting up the config entry."""
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups"
    ) as mock_forward:
        mock_forward.return_value = True
        
        result = await async_setup_entry(hass, mock_config_entry)
        
        assert result is True
        assert DOMAIN in hass.data
        assert mock_config_entry.entry_id in hass.data[DOMAIN]
        assert mock_forward.called


async def test_async_unload_entry(hass: HomeAssistant, mock_config_entry: ConfigEntry) -> None:
    """Test unloading the config entry."""
    # First set up the entry
    hass.data[DOMAIN] = {mock_config_entry.entry_id: mock_config_entry.data}
    
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_unload_platforms"
    ) as mock_unload:
        mock_unload.return_value = True
        
        result = await async_unload_entry(hass, mock_config_entry)
        
        assert result is True
        assert mock_config_entry.entry_id not in hass.data[DOMAIN]
        assert mock_unload.called


async def test_async_unload_entry_failed(hass: HomeAssistant, mock_config_entry: ConfigEntry) -> None:
    """Test failed unloading of config entry."""
    hass.data[DOMAIN] = {mock_config_entry.entry_id: mock_config_entry.data}
    
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_unload_platforms"
    ) as mock_unload:
        mock_unload.return_value = False
        
        result = await async_unload_entry(hass, mock_config_entry)
        
        assert result is False
        # Data should not be cleaned up if unload failed
        assert mock_config_entry.entry_id in hass.data[DOMAIN]