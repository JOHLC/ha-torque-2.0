"""Options flow for Torque integration.

This file is now integrated into config_flow.py to follow Home Assistant best practices.
The options flow functionality is handled by the TorqueOptionsFlow class in config_flow.py.
"""

from __future__ import annotations

        # Allow user to hide PIDs (by PID number, comma separated) and rename sensors
        options_schema = vol.Schema({
            vol.Optional("hide_pids", default=self.config_entry.options.get("hide_pids", "")): str,
            vol.Optional("rename_map", default=self.config_entry.options.get("rename_map", "")): str,
        })
        return self.async_show_form(step_id="init", data_schema=options_schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TorqueOptionsFlowHandler(config_entry)

