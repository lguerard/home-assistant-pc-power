from .const import DOMAIN

async def async_setup_entry(hass, config_entry):
    hass.data.setdefault(DOMAIN, {})
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(config_entry, ["switch"])
    )
    return True

async def async_unload_entry(hass, config_entry):
    return await hass.config_entries.async_forward_entry_unload(config_entry, "switch")
