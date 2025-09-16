"""The Torque integration for Home Assistant."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Torque integration from configuration.yaml (deprecated).

    Args:
        hass: Home Assistant instance
        config: Configuration dictionary

    Returns:
        True if setup is successful
    """
    _LOGGER.debug("Torque integration initialized")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Torque from a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry instance

    Returns:
        True if setup is successful
    """
    _LOGGER.debug("Setting up Torque config entry: %s", entry.entry_id)

    # Initialize storage for this integration
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data


    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info("Torque integration setup complete for entry: %s", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    """Unload a Torque config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry instance

    Returns:
        True if unload is successful
    """
    _LOGGER.debug("Unloading Torque config entry: %s", entry.entry_id)

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Clean up stored data
        hass.data[DOMAIN].pop(entry.entry_id, None)
        _LOGGER.info(
            "Torque integration unloaded successfully for entry: %s", entry.entry_id
        )
    else:
        _LOGGER.error(
            "Failed to unload Torque integration for entry: %s", entry.entry_id
        )

    return unload_ok
