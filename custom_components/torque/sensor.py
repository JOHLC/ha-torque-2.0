"""Support for the Torque OBD application."""

from __future__ import annotations

import logging
import re
import time

from aiohttp import web
import voluptuous as vol

from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry

from homeassistant.components.sensor import (
    RestoreSensor,
    PLATFORM_SCHEMA as SENSOR_PLATFORM_SCHEMA,
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from .const import CONF_EMAIL, CONF_NAME, DOMAIN, DEFAULT_NAME
from homeassistant.const import DEGREE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
try:
    from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
except ImportError:
    from homeassistant.helpers.entity_registry import async_get_registry as async_get_entity_registry

_LOGGER = logging.getLogger(__name__)

API_PATH = "/api/torque"
DEFAULT_NAME = "vehicle"
DOMAIN = "torque"
ENTITY_NAME_FORMAT = "{0} {1}"

SENSOR_EMAIL_FIELD = "eml"
SENSOR_NAME_KEY = r"userFullName(\w+)"
SENSOR_UNIT_KEY = r"userUnit(\w+)"
SENSOR_VALUE_KEY = r"k(\w+)"

NAME_KEY = re.compile(SENSOR_NAME_KEY)
UNIT_KEY = re.compile(SENSOR_UNIT_KEY)
VALUE_KEY = re.compile(SENSOR_VALUE_KEY)

IMPERIAL_TO_METRIC_UNITS = {
    "mph": "km/h",
    "miles": "km",
    "°F": "°C",
    "F": "°C",
    "mile": "km",
    "Miles": "km",
    "MPH": "km/h",
    "Mile": "km",
    # Add more as needed
}

## PLATFORM_SCHEMA = SENSOR_PLATFORM_SCHEMA.extend({
##    vol.Required(CONF_EMAIL): cv.string,
##    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
## })


def convert_pid(value: str) -> int | None:
    """Convert PID from hex string to integer. Return None if conversion fails."""
    try:
        _LOGGER.debug(f"Converting PID from value: {value}")
        return int(value, 16)
    except (ValueError, TypeError) as e:
        _LOGGER.warning(f"Failed to convert PID from value '{value}': {e}")
        return None


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Torque sensors from a config entry."""
    email = config_entry.data[CONF_EMAIL]
    vehicle = config_entry.data.get(CONF_NAME, DEFAULT_NAME)
    sensors: dict[int, TorqueSensor] = {}
    _LOGGER.info(f"Setting up Torque entry: email={email}, vehicle={vehicle}, entry_id={config_entry.entry_id}")

    # Restore previously known sensors from the entity registry
    entity_registry = async_get_entity_registry(hass)
    known_entities = [
        e for e in entity_registry.entities.values()
        if e.platform == DOMAIN and e.config_entry_id == config_entry.entry_id
    ]
    new_entities = []
    for entity in known_entities:
        # Extract PID from unique_id (assume format: torque_<vehicle>_<pid>)
        parts = entity.unique_id.split("_")
        if len(parts) >= 3 and parts[0] == DOMAIN:
            try:
                pid = int(parts[-1])
                name = entity.original_name or f"PID {pid}"
                unit = getattr(entity, 'unit_of_measurement', '') or ''
                sensor = TorqueSensor(name, unit, pid, vehicle, config_entry.options)
                sensors[pid] = sensor
                new_entities.append(sensor)
            except Exception as ex:
                _LOGGER.debug(f"Could not restore sensor for entity {entity.entity_id}: {ex}")
    if new_entities:
        async_add_entities(new_entities, update_before_add=True)
        _LOGGER.info(f"Restored {len(new_entities)} Torque sensors from registry for {vehicle}")

    hass.http.register_view(
        TorqueReceiveDataView(email, vehicle, sensors, async_add_entities, config_entry)
    )
    _LOGGER.debug("TorqueReceiveDataView registered for API path %s", API_PATH)


class TorqueReceiveDataView(HomeAssistantView):
    """Handle data from Torque requests."""

    url = API_PATH
    name = "api:torque"
    requires_auth = False

    def __init__(
        self,
        email: str,
        vehicle: str,
        sensors: dict[int, TorqueSensor],
        async_add_entities: AddEntitiesCallback,
        config_entry=None,
    ) -> None:
        """Initialize a Torque view."""
        self.email = email
        self.vehicle = vehicle
        self.sensors = sensors
        self.async_add_entities = async_add_entities
        self.config_entry = config_entry
        _LOGGER.debug(f"TorqueReceiveDataView initialized: email={email}, vehicle={vehicle}")

    async def get(self, request: web.Request) -> web.Response:
        """Handle Torque GET requests."""
        _LOGGER.debug(f"Received GET request: {dict(request.query)}")
        _LOGGER.debug(f"Raw GET data: {request.query}")
        return await self._handle_data(request.query)

    async def post(self, request: web.Request) -> web.Response:
        """Handle Torque POST requests."""
        data = await request.post()
        _LOGGER.debug(f"Received POST request: {dict(data)}")
        _LOGGER.debug(f"Raw POST data: {data}")
        return await self._handle_data(data)

    async def _handle_data(self, data: dict) -> web.Response:
        """Common handler for Torque GET/POST requests."""
        _LOGGER.debug(f"Handling data: {data}")
        if SENSOR_EMAIL_FIELD not in data:
            _LOGGER.warning("Missing email field in request")
            return web.Response(status=400, text="Missing email")
        if self.email and data[SENSOR_EMAIL_FIELD] != self.email:
            _LOGGER.warning(f"Ignoring data from unmatched email: {data[SENSOR_EMAIL_FIELD]}")
            return web.Response(text="Unauthorized email", status=403)
        names: dict[int, str] = {}
        units: dict[int, str] = {}
        for key, value in data.items():
            if match := NAME_KEY.match(key):
                pid = convert_pid(match.group(1))
                if pid is not None:
                    names[pid] = value
                    _LOGGER.debug(f"Parsed name: pid={pid}, name={value}")
                else:
                    _LOGGER.warning(f"Skipping name for invalid PID: {match.group(1)}")
            elif match := UNIT_KEY.match(key):
                pid = convert_pid(match.group(1))
                if pid is not None:
                    unit = value.replace("\\xC2\\xB0", DEGREE)
                    unit = IMPERIAL_TO_METRIC_UNITS.get(unit, unit)
                    if unit is None:
                        unit = "km/h"
                    units[pid] = unit
                    _LOGGER.debug(f"Parsed unit: pid={pid}, unit={unit}")
                else:
                    _LOGGER.warning(f"Skipping unit for invalid PID: {match.group(1)}")
            elif match := VALUE_KEY.match(key):
                pid = convert_pid(match.group(1))
                if pid is not None:
                    _LOGGER.debug(f"Parsed value: pid={pid}, value={value}")
                    if pid in self.sensors:
                        try:
                            self.sensors[pid].async_on_update(value)
                        except Exception as ex:
                            _LOGGER.error(f"Error updating sensor for PID {pid}: {ex}")
                else:
                    _LOGGER.warning(f"Skipping value for invalid PID: {match.group(1)}")
        new_entities = []
        for pid, name in names.items():
            if pid not in self.sensors:
                try:
                    hide_pids = []
                    rename_map = {}
                    if self.config_entry and self.config_entry.options.get("hide_pids"):
                        hide_pids = [int(x.strip()) for x in self.config_entry.options["hide_pids"].split(",") if x.strip().isdigit()]
                        if pid in hide_pids:
                            _LOGGER.info(f"PID {pid} is hidden by options, skipping sensor creation.")
                            continue
                    if self.config_entry and self.config_entry.options.get("rename_map"):
                        for pair in self.config_entry.options["rename_map"].split(","):
                            if ":" in pair:
                                k, v = pair.split(":", 1)
                                try:
                                    rename_map[int(k.strip())] = v.strip()
                                except Exception:
                                    pass
                    sensor_name = rename_map.get(pid, name)
                    sensor = TorqueSensor(sensor_name, units.get(pid), pid, self.vehicle, self.config_entry.options if self.config_entry else {})
                    self.sensors[pid] = sensor
                    new_entities.append(sensor)
                    _LOGGER.info(f"Prepared new TorqueSensor: name={sensor_name}, pid={pid}, unit={units.get(pid)}")
                except Exception as ex:
                    _LOGGER.error(f"Could not create sensor for PID {pid}: {ex}")
        if new_entities:
            _LOGGER.info("Adding new Torque sensors: %s", [s.name for s in new_entities])
            self.async_add_entities(new_entities)
        else:
            _LOGGER.debug("No new sensors to add.")
        return web.Response(text="OK")


class TorqueSensor(RestoreSensor, SensorEntity):
    """Representation of a Torque sensor."""

    MIN_UPDATE_INTERVAL = 10  # seconds
    SIGNIFICANT_CHANGE = 0.01  # Only update if value changes by this much (for floats)

    def __init__(self, name: str, unit: str | None, pid: int, vehicle: str, options=None):
        """Initialize the sensor."""
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._pid = pid
        self._vehicle = vehicle
        self._last_update = 0.0
        self._last_reported_value = None
        self._attr_device_class = self._guess_device_class(unit, name)
        self._attr_state_class = self._guess_state_class(unit, name)
        self._options = options or {}
        self._attr_icon = self._pick_icon(name, unit, self._attr_device_class)
        _LOGGER.debug(f"TorqueSensor initialized: name={name}, unit={unit}, pid={pid}, vehicle={vehicle}, device_class={self._attr_device_class}, state_class={self._attr_state_class}, icon={self._attr_icon}")

    def _pick_icon(self, name, unit, device_class):
        n = name.lower() if name else ""
        u = unit.lower() if unit else ""
        # Device class icons
        if device_class == SensorDeviceClass.TEMPERATURE:
            return "mdi:thermometer"
        if device_class == SensorDeviceClass.SPEED:
            return "mdi:speedometer"
        if device_class == SensorDeviceClass.DISTANCE:
            return "mdi:map-marker-distance"
        if device_class == SensorDeviceClass.PRESSURE:
            return "mdi:gauge"
        # Fuel/fuel level/mpg
        if "fuel" in n or "mpg" in n or "miles per gallon" in n or "mpg" in u or "miles per gallon" in u:
            return "mdi:gas-station"
        # Acceleration
        if "acceleration" in n or "g-force" in n or "gforce" in n:
            return "mdi:arrow-up-bold"
        # Battery/voltage
        if "battery" in n or "voltage" in n or "volt" in u:
            return "mdi:car-battery"
        if device_class == SensorDeviceClass.BATTERY:
            # Only use car-battery if it's not fuel
            if not ("fuel" in n or "mpg" in n or "miles per gallon" in n):
                return "mdi:car-battery"
        # Name/unit-based icons
        if "rpm" in n:
            return "mdi:rotate-right"
        if "throttle" in n:
            return "mdi:car-cruise-control"
        if "intake" in n or "air" in n:
            return "mdi:weather-windy"
        if "coolant" in n:
            return "mdi:coolant-temperature"
        if "load" in n:
            return "mdi:engine"
        if "distance" in n:
            return "mdi:map-marker-distance"
        if "pressure" in n or "psi" in u or "bar" in u:
            return "mdi:gauge"
        if "temperature" in n or "temp" in n:
            return "mdi:thermometer"
        if "speed" in n:
            return "mdi:speedometer"
        if "timing" in n:
            return "mdi:clock"
        if "oxygen" in n:
            return "mdi:molecule"
        if "maf" in n:
            return "mdi:weather-windy"
        if "mil" in n or "cel" in n:
            return "mdi:alert"
        # Default
        return "mdi:car"

    def _guess_device_class(self, unit, name):
        if not unit:
            return None
        unit = unit.lower()
        if unit in ("°c", "c", "degc") or "temp" in name.lower():
            return SensorDeviceClass.TEMPERATURE
        if unit in ("km/h", "kph", "m/s", "mph") or "speed" in name.lower():
            return SensorDeviceClass.SPEED
        if unit in ("km", "m", "mile", "miles") or "distance" in name.lower():
            return SensorDeviceClass.DISTANCE
        if unit in ("%",) and "fuel" in name.lower():
            return SensorDeviceClass.BATTERY
        if unit in ("bar", "kpa", "psi", "hpa") or "pressure" in name.lower():
            return SensorDeviceClass.PRESSURE
        return None

    def _guess_state_class(self, unit, name):
        # Most OBD sensors are measurements, but some (like odometer) are totals
        if unit and unit.lower() in ("km", "mile", "miles"):
            return SensorStateClass.TOTAL
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return a unique ID for this sensor."""
        return f"torque_{self._vehicle}_{self._pid}"

    @property
    def device_info(self):
        """Group sensors under a single device per vehicle."""
        return {
            "identifiers": {(DOMAIN, self._vehicle)},
            "name": f"Torque - {self._vehicle}",
            "manufacturer": "Torque OBD",
            "model": "Torque Sensor",
            "entry_type": "service",
        }

    @callback
    def async_on_update(self, value: str) -> None:
        """Update the sensor value, throttled."""
        now = time.monotonic()
        try:
            new_value = float(value)
        except (ValueError, TypeError):
            _LOGGER.warning(f"Non-numeric value for PID {self._pid}: {value}")
            return
        # Only update if enough time has passed or value changed significantly
        should_update = False
        if self._last_reported_value is None:
            should_update = True
        elif isinstance(new_value, float) and isinstance(self._last_reported_value, float):
            if abs(new_value - self._last_reported_value) > self.SIGNIFICANT_CHANGE:
                should_update = True
        elif new_value != self._last_reported_value:
            should_update = True
        if should_update and (now - self._last_update) >= self.MIN_UPDATE_INTERVAL:
            self._attr_native_value = new_value
            self._last_reported_value = new_value
            self._last_update = now
            self.async_write_ha_state()
            _LOGGER.debug(f"TorqueSensor '{self._attr_name}' updated: value={new_value}")
        else:
            _LOGGER.debug(f"TorqueSensor '{self._attr_name}' throttled: value={new_value}")

    async def async_added_to_hass(self):
        """Restore state on restart using native_value from RestoreSensor."""
        await super().async_added_to_hass()
        last_sensor_data = await self.async_get_last_sensor_data()
        if last_sensor_data is not None:
            native_value = last_sensor_data.native_value
            if native_value not in (None, "unknown", "unavailable", "None"):
                try:
                    self._attr_native_value = float(native_value)
                    _LOGGER.debug(f"Restoring native_value for {self._attr_name}: {native_value}")
                except (ValueError, TypeError):
                    self._attr_native_value = None
                    _LOGGER.debug(f"Not restoring non-numeric native_value for {self._attr_name}: {native_value}")
            else:
                self._attr_native_value = None
                _LOGGER.debug(f"Not restoring invalid native_value for {self._attr_name}: {native_value}")
        else:
            _LOGGER.debug(f"No previous native_value to restore for {self._attr_name}")
        self.async_write_ha_state()

    @property
    def suggested_display_precision(self) -> int:
        """Suggest the display precision for this sensor."""
        return 2
