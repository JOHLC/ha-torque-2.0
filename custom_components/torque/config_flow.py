"""Config flow for Torque integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import CONF_EMAIL, CONF_NAME, DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


class TorqueConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Torque integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step when user initiates a config flow.

        Args:
            user_input: User input from the config form

        Returns:
            FlowResult indicating next step or entry creation
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Normalize email to lowercase for consistency
                email = user_input[CONF_EMAIL].lower().strip()

                # Validate email format (basic validation)
                if not email or "@" not in email:
                    errors[CONF_EMAIL] = "invalid_email"
                else:
                    # Set unique ID based on email to prevent duplicates
                    await self.async_set_unique_id(email)
                    self._abort_if_unique_id_configured()

                    # Get vehicle name or use default
                    vehicle_name = user_input.get(CONF_NAME, DEFAULT_NAME).strip()
                    if not vehicle_name:
                        vehicle_name = DEFAULT_NAME

                    _LOGGER.debug("Creating Torque config entry for %s", email)

                    return self.async_create_entry(
                        title=vehicle_name,
                        data={
                            CONF_EMAIL: email,
                            CONF_NAME: vehicle_name,
                        },
                    )

            except Exception as exc:
                _LOGGER.error("Unexpected error in config flow: %s", exc)
                errors["base"] = "unknown_error"

        # Show the form with any validation errors
        data_schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): cv.string,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "api_path": "/api/torque",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> TorqueOptionsFlow:
        """Create the options flow for this config entry.

        Args:
            config_entry: The config entry for this integration

        Returns:
            TorqueOptionsFlow instance
        """
        return TorqueOptionsFlow(config_entry)


class TorqueOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Torque integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow.

        Args:
            config_entry: The config entry for this integration
        """
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options for Torque integration.

        Args:
            user_input: User input from the options form

        Returns:
            FlowResult indicating completion or form display
        """
        if user_input is not None:
            _LOGGER.debug("Updating Torque options for %s", self.config_entry.entry_id)
            return self.async_create_entry(title="", data=user_input)

        # Get current options with defaults
        current_options = self.config_entry.options

        options_schema = vol.Schema(
            {
                vol.Optional(
                    "hide_pids", default=current_options.get("hide_pids", "")
                ): str,
                vol.Optional(
                    "rename_map", default=current_options.get("rename_map", "")
                ): str,
                vol.Optional(
                    "unit_system", default=current_options.get("unit_system", "metric")
                ): vol.In(["metric", "imperial"]),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            description_placeholders={
                "example_hide": "41,42,43",
                "example_rename": "41:Engine Load,42:Coolant Temp",
            },
        )
