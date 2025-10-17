"""Support for the Torque OBD application."""

from __future__ import annotations

import logging
import re
import time
from re import Pattern
from typing import Any

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.sensor import (
    RestoreSensor,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import (
    async_get as async_get_entity_registry,
)

from .const import (
    API_PATH,
    CONF_EMAIL,
    CONF_NAME,
    DEFAULT_NAME,
    DOMAIN,
    MIN_UPDATE_INTERVAL,
    SENSOR_EMAIL_FIELD,
    SENSOR_NAME_KEY,
    SENSOR_SIGNIFICANT_CHANGES,
    SENSOR_UNIT_KEY,
    SENSOR_VALUE_KEY,
    SIGNIFICANT_CHANGE,
)

_LOGGER = logging.getLogger(__name__)

# Compiled regex patterns for better performance
NAME_KEY: Pattern[str] = re.compile(SENSOR_NAME_KEY)
UNIT_KEY: Pattern[str] = re.compile(SENSOR_UNIT_KEY)
VALUE_KEY: Pattern[str] = re.compile(SENSOR_VALUE_KEY)


def convert_pid(value: str) -> int | None:
    """Convert PID from hex string to integer.

    Args:
        value: Hex string value to convert

    Returns:
        Integer PID value or None if conversion fails
    """
    try:
        _LOGGER.debug("Converting PID from value: %s", value)
        return int(value, 16)
    except (ValueError, TypeError) as exc:
        _LOGGER.warning("Failed to convert PID from value '%s': %s", value, exc)
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Torque sensors from a config entry.

    Args:
        hass: Home Assistant instance
        config_entry: Configuration entry for the integration
        async_add_entities: Callback to add entities
    """
    email = config_entry.data[CONF_EMAIL]
    vehicle = config_entry.data.get(CONF_NAME, DEFAULT_NAME)
    sensors: dict[int, TorqueSensor] = {}

    _LOGGER.info(
        "Setting up Torque entry: email=%s, vehicle=%s, entry_id=%s",
        email,
        vehicle,
        config_entry.entry_id,
    )

    # Restore previously known sensors from the entity registry
    entity_registry = async_get_entity_registry(hass)
    known_entities = [
        entity
        for entity in entity_registry.entities.values()
        if entity.platform == DOMAIN and entity.config_entry_id == config_entry.entry_id
    ]

    new_entities: list[TorqueSensor] = []
    for entity in known_entities:
        # Extract PID from unique_id (assume format: torque_<vehicle>_<pid>)
        parts = entity.unique_id.split("_")
        if len(parts) >= 3 and parts[0] == DOMAIN:
            try:
                pid = int(parts[-1])
                name = entity.original_name or f"PID {pid}"
                unit = getattr(entity, "unit_of_measurement", "") or ""

                sensor = TorqueSensor(
                    name=name,
                    unit=unit,
                    pid=pid,
                    vehicle=vehicle,
                    options=config_entry.options,
                )
                sensors[pid] = sensor
                new_entities.append(sensor)

            except Exception as exc:
                _LOGGER.debug(
                    "Could not restore sensor for entity %s: %s", entity.entity_id, exc
                )

    if new_entities:
        async_add_entities(new_entities, update_before_add=True)
        _LOGGER.info(
            "Restored %d Torque sensors from registry for %s",
            len(new_entities),
            vehicle,
        )

    # Register the HTTP view for receiving Torque data
    hass.http.register_view(
        TorqueReceiveDataView(
            email=email,
            vehicle=vehicle,
            sensors=sensors,
            async_add_entities=async_add_entities,
            config_entry=config_entry,
        )
    )
    _LOGGER.debug("TorqueReceiveDataView registered for API path %s", API_PATH)


class TorqueReceiveDataView(HomeAssistantView):
    """Handle data from Torque HTTP requests."""

    url = API_PATH
    name = "api:torque"
    requires_auth = False

    def __init__(
        self,
        email: str,
        vehicle: str,
        sensors: dict[int, TorqueSensor],
        async_add_entities: AddEntitiesCallback,
        config_entry: ConfigEntry | None = None,
    ) -> None:
        """Initialize a Torque data receiver view.

        Args:
            email: Expected email address for authentication
            vehicle: Vehicle name for this integration instance
            sensors: Dictionary of existing sensors by PID
            async_add_entities: Callback to add new entities
            config_entry: Configuration entry for options access
        """
        self.email = email
        self.vehicle = vehicle
        self.sensors = sensors
        self.async_add_entities = async_add_entities
        self.config_entry = config_entry

        _LOGGER.debug(
            "TorqueReceiveDataView initialized: email=%s, vehicle=%s", email, vehicle
        )

    async def get(self, request: web.Request) -> web.Response:
        """Handle Torque GET requests.

        Args:
            request: HTTP request object

        Returns:
            HTTP response
        """
        _LOGGER.debug("Received GET request: %s", dict(request.query))
        return await self._handle_data(dict(request.query))

    async def post(self, request: web.Request) -> web.Response:
        """Handle Torque POST requests.

        Args:
            request: HTTP request object

        Returns:
            HTTP response
        """
        try:
            data = await request.post()
            _LOGGER.debug("Received POST request: %s", dict(data))
            return await self._handle_data(dict(data))
        except Exception as exc:
            _LOGGER.error("Error processing POST request: %s", exc)
            return web.Response(status=400, text="Invalid request data")

    async def _handle_data(self, data: dict[str, Any]) -> web.Response:
        """Common handler for Torque GET/POST requests.

        Args:
            data: Request data dictionary

        Returns:
            HTTP response
        """
        try:
            _LOGGER.debug("Processing Torque data: %s", data)

            # Validate email field presence
            if SENSOR_EMAIL_FIELD not in data:
                _LOGGER.warning("Missing email field in request")
                return web.Response(status=400, text="Missing email field")

            # Validate email matches configured email
            received_email = data[SENSOR_EMAIL_FIELD]
            if self.email and received_email != self.email:
                _LOGGER.warning(
                    "Ignoring data from unmatched email: %s (expected: %s)",
                    received_email,
                    self.email,
                )
                return web.Response(status=403, text="Unauthorized email")

            # Parse sensor names, units, and values from the data
            names: dict[int, str] = {}
            units: dict[int, str] = {}

            for key, value in data.items():
                self._parse_sensor_data(key, value, names, units)

            # Update existing sensors and create new ones
            await self._process_sensor_updates(data, names, units)

            return web.Response(text="OK")

        except Exception as exc:
            _LOGGER.error("Unexpected error handling Torque data: %s", exc)
            return web.Response(status=500, text="Internal server error")

    def _parse_sensor_data(
        self, key: str, value: str, names: dict[int, str], units: dict[int, str]
    ) -> None:
        """Parse individual sensor data fields.

        Args:
            key: Data field key
            value: Data field value
            names: Dictionary to store parsed names
            units: Dictionary to store parsed units
        """
        # Parse sensor names
        if match := NAME_KEY.match(key):
            pid = convert_pid(match.group(1))
            if pid is not None:
                names[pid] = value
                _LOGGER.debug("Parsed name: pid=%d, name=%s", pid, value)
            else:
                _LOGGER.warning("Skipping name for invalid PID: %s", match.group(1))

        # Parse sensor units
        elif match := UNIT_KEY.match(key):
            pid = convert_pid(match.group(1))
            if pid is not None:
                # Convert degree symbol encoding
                unit = value.replace("\\xC2\\xB0", "°")
                units[pid] = unit
                _LOGGER.debug("Parsed unit: pid=%d, unit=%s", pid, unit)
            else:
                _LOGGER.warning("Skipping unit for invalid PID: %s", match.group(1))

        # Parse and update sensor values
        elif match := VALUE_KEY.match(key):
            pid = convert_pid(match.group(1))
            if pid is not None:
                _LOGGER.debug("Parsed value: pid=%d, value=%s", pid, value)
                if pid in self.sensors:
                    try:
                        self.sensors[pid].async_on_update(value)
                    except Exception as exc:
                        _LOGGER.error("Error updating sensor for PID %d: %s", pid, exc)
            else:
                _LOGGER.warning("Skipping value for invalid PID: %s", match.group(1))

    async def _process_sensor_updates(
        self, data: dict[str, Any], names: dict[int, str], units: dict[int, str]
    ) -> None:
        """Process sensor updates and create new sensors if needed.

        Args:
            data: Raw request data
            names: Parsed sensor names by PID
            units: Parsed sensor units by PID
        """
        new_entities: list[TorqueSensor] = []

        for pid, name in names.items():
            if pid not in self.sensors:
                try:
                    # Check if PID should be hidden
                    if self._should_hide_pid(pid):
                        _LOGGER.info(
                            "PID %d is hidden by options, skipping sensor creation", pid
                        )
                        continue

                    # Apply custom sensor name if configured
                    sensor_name = self._get_custom_sensor_name(pid, name)

                    # Create new sensor
                    sensor = TorqueSensor(
                        name=sensor_name,
                        unit=units.get(pid),
                        pid=pid,
                        vehicle=self.vehicle,
                        options=self.config_entry.options if self.config_entry else {},
                    )

                    self.sensors[pid] = sensor
                    new_entities.append(sensor)

                    _LOGGER.info(
                        "Created new TorqueSensor: name=%s, pid=%d, unit=%s",
                        sensor_name,
                        pid,
                        units.get(pid),
                    )

                except Exception as exc:
                    _LOGGER.error("Could not create sensor for PID %d: %s", pid, exc)

        # Add new entities to Home Assistant
        if new_entities:
            _LOGGER.info(
                "Adding new Torque sensors: %s",
                [sensor.name for sensor in new_entities],
            )
            self.async_add_entities(new_entities)
        else:
            _LOGGER.debug("No new sensors to add")

    def _should_hide_pid(self, pid: int) -> bool:
        """Check if a PID should be hidden based on options.

        Args:
            pid: PID to check

        Returns:
            True if PID should be hidden
        """
        if not self.config_entry or not self.config_entry.options.get("hide_pids"):
            return False

        try:
            hide_pids = [
                int(x.strip())
                for x in self.config_entry.options["hide_pids"].split(",")
                if x.strip().isdigit()
            ]
            return pid in hide_pids
        except Exception as exc:
            _LOGGER.warning("Error parsing hide_pids option: %s", exc)
            return False

    def _get_custom_sensor_name(self, pid: int, default_name: str) -> str:
        """Get custom sensor name if configured.

        Args:
            pid: PID of the sensor
            default_name: Default name from Torque

        Returns:
            Custom name if configured, otherwise default name
        """
        if not self.config_entry or not self.config_entry.options.get("rename_map"):
            return default_name

        try:
            rename_map: dict[int, str] = {}
            for pair in self.config_entry.options["rename_map"].split(","):
                if ":" in pair:
                    key_str, value_str = pair.split(":", 1)
                    try:
                        rename_map[int(key_str.strip())] = value_str.strip()
                    except ValueError:
                        continue

            return rename_map.get(pid, default_name)

        except Exception as exc:
            _LOGGER.warning("Error parsing rename_map option: %s", exc)
            return default_name


class TorqueSensor(RestoreSensor, SensorEntity):
    """Representation of a Torque OBD sensor."""

    # Constants for sensor behavior
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        name: str,
        unit: str | None,
        pid: int,
        vehicle: str,
        options: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the Torque sensor.

        Args:
            name: Sensor name from Torque app
            unit: Unit of measurement from Torque app
            pid: PID identifier
            vehicle: Vehicle name
            options: Configuration options
        """
        self._attr_name = name
        self._pid = pid
        self._vehicle = vehicle
        self._last_update = 0.0
        self._last_reported_value: float | None = None
        self._options = options or {}
        self._original_unit = unit
        self._non_numeric_warning_logged = False

        # Data validation attributes
        self._non_numeric_warning_logged = False

        # Set up sensor properties
        self._attr_unique_id = f"{DOMAIN}_{vehicle.lower()}_{pid}"
        self._attr_native_unit_of_measurement = unit  # Use raw unit from Torque
        self._attr_device_class = None  # Don't guess device class to avoid issues
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = self._determine_icon(name)

        _LOGGER.debug(
            "TorqueSensor initialized: name=%s, pid=%d, unit=%s, unique_id=%s",
            name,
            pid,
            self._attr_native_unit_of_measurement,
            self._attr_unique_id,
        )

    def _determine_icon(self, name: str) -> str | None:
        """Determine appropriate icon for the sensor.

        Args:
            name: Sensor name

        Returns:
            Icon string or None for default
        """
        if not name:
            return None

        name_lower = name.lower()

        # Temperature related
        if any(temp in name_lower for temp in ["temp", "temperature"]):
            if "coolant" in name_lower:
                return "mdi:coolant-temperature"
            elif "air" in name_lower or "intake" in name_lower:
                return "mdi:thermometer"
            else:
                return "mdi:thermometer"

        # Speed related
        elif "speed" in name_lower:
            return "mdi:speedometer"

        # Engine related
        elif any(eng in name_lower for eng in ["rpm", "engine"]):
            return "mdi:engine"

        # Fuel related
        elif "fuel" in name_lower:
            return "mdi:gas-station"

        # Voltage/electrical
        elif any(elec in name_lower for elec in ["volt", "battery"]):
            return "mdi:car-battery"

        return None

    def _get_significant_change_threshold(self) -> float:
        """Get the significant change threshold for this sensor.

        Returns:
            Threshold value for significant changes
        """
        if not self._attr_name:
            return SIGNIFICANT_CHANGE

        name_lower = self._attr_name.lower()

        # Check for sensor-specific thresholds
        for keyword, threshold in SENSOR_SIGNIFICANT_CHANGES.items():
            if keyword in name_lower:
                return threshold

        return SIGNIFICANT_CHANGE

    @callback
    def async_on_update(self, value: str) -> None:
        """Update sensor value from Torque data with minimal processing.

        Args:
            value: New sensor value as string from Torque (raw value)
        """
        now = time.monotonic()

        try:
            new_value = float(value)
            self._non_numeric_warning_logged = False
        except (ValueError, TypeError):
            if not self._non_numeric_warning_logged:
                _LOGGER.warning("Non-numeric value for PID %d: %s", self._pid, value)
                self._non_numeric_warning_logged = True
            return

        # Apply minimal validation - accept all valid numeric values
        if not self._is_value_valid(new_value):
            return

        # Determine if we should update based on significance and time
        should_update = self._should_update_value(new_value, now)

        if should_update:
            self._attr_native_value = new_value
            self._last_reported_value = new_value
            self._last_update = now
            self.async_write_ha_state()

            _LOGGER.debug(
                "TorqueSensor '%s' updated: value=%.2f", self._attr_name, new_value
            )

    def _is_value_valid(self, new_value: float) -> bool:
        """Validate sensor value with minimal filtering.

        Args:
            new_value: New sensor value to validate

        Returns:
            True if value is valid and should be processed
        """
        # Accept all numeric values - let Home Assistant handle any unit conversion
        # and let users see the raw data from Torque
        return True

    def _should_update_value(self, new_value: float, current_time: float) -> bool:
        """Determine if sensor value should be updated.

        Args:
            new_value: New sensor value
            current_time: Current time

        Returns:
            True if value should be updated
        """
        # Always update if we don't have a previous value
        if self._last_reported_value is None:
            return True

        # Check for significant change using sensor-specific threshold
        threshold = self._get_significant_change_threshold()
        is_significant_change = abs(new_value - self._last_reported_value) >= threshold

        # Only accept updates if the change is significant
        # This prevents flip-flopping back to old values when rapid updates arrive
        # Note: Sensor-specific thresholds (e.g., 50 RPM, 1 km/h) are tuned to filter
        # noise while still capturing all meaningful state changes
        if not is_significant_change:
            return False

        # For significant changes, enforce minimum time interval to prevent spam
        time_since_last_update = current_time - self._last_update
        return time_since_last_update >= MIN_UPDATE_INTERVAL

    async def async_added_to_hass(self) -> None:
        """Restore sensor state when added to Home Assistant."""
        await super().async_added_to_hass()

        # Restore last known state
        last_sensor_data = await self.async_get_last_sensor_data()
        if last_sensor_data is not None and last_sensor_data.native_value is not None:
            try:
                restored_value = float(last_sensor_data.native_value)
                if str(restored_value).lower() not in {
                    "none",
                    "unknown",
                    "unavailable",
                }:
                    self._attr_native_value = restored_value
                    _LOGGER.debug(
                        "Restored value for %s: %.2f", self._attr_name, restored_value
                    )
                else:
                    self._attr_native_value = None

            except (ValueError, TypeError):
                self._attr_native_value = None
                _LOGGER.debug(
                    "Could not restore non-numeric value for %s: %s",
                    self._attr_name,
                    last_sensor_data.native_value,
                )
        else:
            _LOGGER.debug("No previous value to restore for %s", self._attr_name)

        self.async_write_ha_state()

    @property
    def suggested_display_precision(self) -> int:
        """Return suggested display precision for this sensor.

        Returns:
            Number of decimal places to display
        """
        return 2

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information for this sensor.

        Returns:
            Device information dictionary
        """
        return {
            "identifiers": {(DOMAIN, self._vehicle)},
            "name": f"Torque {self._vehicle}",
            "manufacturer": "Torque Pro",
            "model": "OBD Vehicle Data",
        }

    def _pick_icon(
        self, name: str, unit: str | None, device_class: str | None
    ) -> str | None:
        """Legacy method for icon selection - kept for compatibility.

        Args:
            name: Sensor name
            unit: Unit of measurement
            device_class: Device class

        Returns:
            Icon string or None
        """
        return self._determine_icon(name)

    def _guess_state_class(self, unit: str | None, name: str | None) -> str | None:
        """Legacy method for state class guessing - kept for compatibility.

        Args:
            unit: Unit of measurement
            name: Sensor name

        Returns:
            State class string
        """
        return SensorStateClass.MEASUREMENT

    def _pick_icon(
        self, name: str | None, unit: str | None, device_class: str | None
    ) -> str | None:
        """Pick an appropriate icon for the sensor based on name and unit."""
        if not name:
            return None

        name_lower = name.lower()

        # Speed sensors
        if "speed" in name_lower:
            return "mdi:speedometer"

        # Temperature sensors
        if any(
            word in name_lower for word in ["temp", "temperature", "coolant", "intake"]
        ):
            return "mdi:thermometer"

        # Fuel related
        if any(
            word in name_lower for word in ["fuel", "gas", "consumption", "mpg", "gal"]
        ):
            return "mdi:gas-station"

        # Engine/RPM
        if any(word in name_lower for word in ["rpm", "engine"]):
            return "mdi:engine"

        # Voltage/Battery
        if any(word in name_lower for word in ["volt", "battery"]):
            return "mdi:car-battery"

        # Pressure
        if "pressure" in name_lower:
            return "mdi:gauge"

        # Distance/Odometer
        if any(word in name_lower for word in ["distance", "odometer", "trip"]):
            return "mdi:map-marker-distance"

        # Default car icon
        return "mdi:car"
