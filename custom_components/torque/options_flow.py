"""Options flow for Torque integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
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
        })
        return self.async_show_form(step_id="init", data_schema=options_schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TorqueOptionsFlowHandler(config_entry)
