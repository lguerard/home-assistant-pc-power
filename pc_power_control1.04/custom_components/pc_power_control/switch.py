from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import wakeonlan
import paramiko

from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    data = config_entry.data
    name = data["name"]
    host = data["host"]
    mac = data["mac"]
    username = data["username"]
    password = data["password"]

    async_add_entities([
        PCPowerSwitch(name, host, mac, username, password)
    ])

class PCPowerSwitch(SwitchEntity):
    @property
    def unique_id(self):
        return f"pc_power_{self._host}"

    @property
    def icon(self):
        return "mdi:desktop-classic"

    @property
    def entity_picture(self):
        return "https://upload.wikimedia.org/wikipedia/commons/3/34/Vintage_computer.jpg"  # Replace with your own if preferred

    def __init__(self, name, host, mac, username, password):
        self._attr_name = name
        self._host = host
        self._mac = mac
        self._username = username
        self._password = password
        self._attr_is_on = False

    def turn_on(self, **kwargs):
        wakeonlan.send_magic_packet(self._mac)
        self._attr_is_on = True

    def turn_off(self, **kwargs):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self._host, username=self._username, password=self._password)
            ssh.exec_command("shutdown /s /t 0")
            ssh.close()
            self._attr_is_on = False
        except Exception as e:
            print(f"Error shutting down: {e}")

    def update(self):
        # Optional: ping or SSH status check
        pass
