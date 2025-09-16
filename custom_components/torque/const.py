"""Constants for the Torque integration."""

from __future__ import annotations

from typing import Final

# Integration domain and API
DOMAIN: Final[str] = "torque"
API_PATH: Final[str] = "/api/torque"

# Configuration keys
CONF_EMAIL: Final[str] = "email"
CONF_NAME: Final[str] = "name"

# Default values
DEFAULT_NAME: Final[str] = "vehicle"

# Sensor field keys from Torque app
SENSOR_EMAIL_FIELD: Final[str] = "eml"
SENSOR_NAME_KEY: Final[str] = r"userFullName(\w+)"
SENSOR_UNIT_KEY: Final[str] = r"userUnit(\w+)"
SENSOR_VALUE_KEY: Final[str] = r"k(\w+)"

# Entity naming
ENTITY_NAME_FORMAT: Final[str] = "{0} {1}"

# Update intervals and thresholds
MIN_UPDATE_INTERVAL: Final[int] = 10  # seconds
SIGNIFICANT_CHANGE: Final[float] = 0.01  # Only update if value changes by this much
