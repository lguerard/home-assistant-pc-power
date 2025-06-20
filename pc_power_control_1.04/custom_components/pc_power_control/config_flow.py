from homeassistant import config_entries
import voluptuous as vol
from homeassistant.core import callback
from .const import DOMAIN

CONFIG_SCHEMA = vol.Schema({
    vol.Required("name"): str,
    vol.Required("host"): str,
    vol.Required("mac"): str,
    vol.Required("username"): str,
    vol.Required("password"): str,
})

class PCPowerControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input["mac"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
                options=user_input,
            )

        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        from .options_flow import PCPowerControlOptionsFlowHandler
        return PCPowerControlOptionsFlowHandler(config_entry)
