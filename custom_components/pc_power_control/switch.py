import logging
from homeassistant.components.switch import SwitchEntity
import wakeonlan
import asyncio
import paramiko
from asyncio.subprocess import PIPE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    data = config_entry.data
    async_add_entities([
        PCPowerSwitch(data["name"], data["host"], data["mac"], data["username"], data["password"])
    ])

class PCPowerSwitch(SwitchEntity):
    def __init__(self, name, host, mac, username, password):
        self._host = host
        self._mac = mac
        self._username = username
        self._password = password

        self._attr_name = name
        self._attr_should_poll = True
        self._attr_is_on = False
        self._attr_unique_id = f"pc_power_{mac.replace(':', '').lower()}"
        self._attr_icon = "mdi:desktop-classic"

    @property
    def is_on(self):
        # Implement logic to check actual PC state
        return self._attr_is_on

    async def async_turn_on(self, **kwargs):
        _LOGGER.info("Sending Wake-on-LAN to MAC %s", self._mac)
        wakeonlan.send_magic_packet(self._mac)
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs):
        try:
            _LOGGER.info("Sending shutdown command to %s via SSH", self._host)
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self._host, username=self._username, password=self._password)
            stdin, stdout, stderr = ssh.exec_command("shutdown -s -f -t 0")
            _LOGGER.info("Shutdown stdout: %s", stdout.read().decode())
            _LOGGER.info("Shutdown stderr: %s", stderr.read().decode())
            ssh.close()
            self._attr_is_on = False
        except Exception as e:
            _LOGGER.error("Failed to shut down PC: %s", e)

    async def async_update(self):
        proc = await asyncio.create_subprocess_exec(
            "ping", "-c", "1", "-W", "1", self._host,
            stdout=PIPE, stderr=PIPE
        )
        await proc.communicate()
        self._attr_is_on = proc.returncode == 0
