from homeassistant import config_entries
import voluptuous as vol
from homeassistant.core import callback

from .const import DOMAIN

class PCPowerControlOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        data = {**self.config_entry.data, **self.config_entry.options}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name", default=data.get("name", "")): str,
                vol.Required("host", default=data.get("host", "")): str,
                vol.Required("mac", default=data.get("mac", "")): str,
                vol.Required("username", default=data.get("username", "")): str,
                vol.Required("password", default=data.get("password", "")): str,
            })
        )
