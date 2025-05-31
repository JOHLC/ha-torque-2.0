"""Options flow for Torque integration."""
import voluptuous as vol # type: ignore
from homeassistant import config_entries # type: ignore
from homeassistant.core import callback # type: ignore
from .const import DOMAIN

class TorqueOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Example: allow user to hide PIDs (by PID number, comma separated)
        options_schema = vol.Schema({
            vol.Optional("hide_pids", default=self.config_entry.options.get("hide_pids", "")): str,
            vol.Optional("rename_map", default=self.config_entry.options.get("rename_map", "")): str,
            vol.Optional(
                "unit_system",
                default=self.config_entry.options.get("unit_system", "metric")
            ): vol.In(["metric", "imperial"]),
        })
        return self.async_show_form(step_id="init", data_schema=options_schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TorqueOptionsFlowHandler(config_entry)
