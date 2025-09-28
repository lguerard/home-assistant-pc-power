import voluptuous as vol
from homeassistant.core import ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_COMMAND,
    ATTR_PC_NAME,
    ATTR_TIMEOUT,
    DEFAULT_SSH_TIMEOUT,
    DOMAIN,
    SERVICE_SEND_COMMAND,
)


async def async_setup_entry(hass, config_entry):
    """Set up PC Power Control from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Forward setup to switch platform
    await hass.config_entries.async_forward_entry_setups(config_entry, ["switch"])

    # Register domain-level SSH command service
    async def async_send_ssh_command_service(call: ServiceCall):
        """Handle SSH command service calls."""
        command = call.data.get(ATTR_COMMAND)
        timeout = call.data.get(ATTR_TIMEOUT, DEFAULT_SSH_TIMEOUT)
        pc_name = call.data.get(ATTR_PC_NAME)

        # Find the appropriate switch
        switches = hass.data[DOMAIN].get("switches", {})

        if pc_name:
            # Use specified PC
            switch = switches.get(pc_name)
            if not switch:
                raise ValueError(
                    f"PC '{pc_name}' not found. Available PCs: {list(switches.keys())}"
                )
        else:
            # Use the first (or only) PC if not specified
            if not switches:
                raise ValueError("No PC Power Control switches configured")
            if len(switches) > 1:
                raise ValueError(
                    f"Multiple PCs configured. Please specify pc_name. Available: {list(switches.keys())}"
                )
            switch = next(iter(switches.values()))

        # Execute the command
        result = await switch.async_send_ssh_command(command, timeout)
        return result

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_COMMAND,
        async_send_ssh_command_service,
        schema=vol.Schema(
            {
                vol.Required(ATTR_COMMAND): cv.string,
                vol.Optional(
                    ATTR_TIMEOUT, default=DEFAULT_SSH_TIMEOUT
                ): cv.positive_int,
                vol.Optional(ATTR_PC_NAME): cv.string,
            }
        ),
    )

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    # Remove service
    hass.services.async_remove(DOMAIN, SERVICE_SEND_COMMAND)

    # Clean up stored data
    if DOMAIN in hass.data:
        hass.data[DOMAIN].pop(config_entry.entry_id, None)

    return await hass.config_entries.async_forward_entry_unload(config_entry, "switch")
