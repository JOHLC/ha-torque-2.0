import voluptuous as vol # type: ignore
from homeassistant import config_entries # type: ignore
from homeassistant.helpers import config_validation as cv # type: ignore
from .const import DOMAIN, DEFAULT_NAME, CONF_EMAIL, CONF_NAME

class TorqueConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_EMAIL].lower())
            self._abort_if_unique_id_configured()
            title = user_input.get(CONF_NAME, DEFAULT_NAME)
            return self.async_create_entry(
                title=title,
                data=user_input,
            )

        data_schema = vol.Schema({
            vol.Required(CONF_EMAIL): cv.string,
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
