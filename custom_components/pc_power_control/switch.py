import asyncio
import logging
from asyncio.subprocess import PIPE

import voluptuous as vol
import wakeonlan
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers import entity_platform

from .const import (
    ATTR_COMMAND,
    ATTR_TIMEOUT,
    DEFAULT_SSH_TIMEOUT,
    SERVICE_SEND_COMMAND,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up PC Power Control switches."""
    data = config_entry.data
    switch = PCPowerSwitch(
        data["name"],
        data["host"],
        data["mac"],
        data["username"],
        data["password"],
        data.get("ssh_port", 22),
        data.get("ssh_timeout", DEFAULT_SSH_TIMEOUT),
    )
    async_add_entities([switch])

    # Register the SSH command service
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SEND_COMMAND,
        {
            vol.Required(ATTR_COMMAND): str,
            vol.Optional(ATTR_TIMEOUT, default=DEFAULT_SSH_TIMEOUT): int,
        },
        "async_send_ssh_command",
    )


class PCPowerSwitch(SwitchEntity):
    """PC Power Control Switch Entity."""

    def __init__(
        self,
        name,
        host,
        mac,
        username,
        password,
        ssh_port=22,
        ssh_timeout=DEFAULT_SSH_TIMEOUT,
    ):
        """Initialize the PC Power Switch.

        Parameters
        ----------
        name : str
            The friendly name for the switch entity.
        host : str
            The IP address or hostname of the remote PC.
        mac : str
            The MAC address of the remote PC for Wake-on-LAN.
        username : str
            SSH username for remote PC access.
        password : str
            SSH password for remote PC access.
        ssh_port : int, optional
            SSH port number (default is 22).
        ssh_timeout : int, optional
            SSH connection timeout in seconds (default is 30).

        Examples
        --------
        >>> switch = PCPowerSwitch("My PC", "192.168.1.100", "aa:bb:cc:dd:ee:ff", "user", "pass")
        """
        self._host = host
        self._mac = mac
        self._username = username
        self._password = password
        self._ssh_port = ssh_port
        self._ssh_timeout = ssh_timeout

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
        """Turn off the PC by sending a shutdown command via SSH."""
        try:
            _LOGGER.info("Sending shutdown command to %s via SSH", self._host)
            result = await self._execute_ssh_command("shutdown -s -f -t 0")
            if result:
                self._attr_is_on = False
                _LOGGER.info("Shutdown command executed successfully")
            else:
                _LOGGER.error("Failed to execute shutdown command")
        except Exception as e:
            _LOGGER.error("Failed to shut down PC: %s", e)

    async def async_update(self):
        """Update the current state of the PC by pinging it."""
        proc = await asyncio.create_subprocess_exec(
            "ping", "-c", "1", "-W", "1", self._host, stdout=PIPE, stderr=PIPE
        )
        await proc.communicate()
        self._attr_is_on = proc.returncode == 0

    async def async_send_ssh_command(self, command: str, timeout: int = None) -> dict:
        """Send a custom SSH command to the remote PC.

        Parameters
        ----------
        command : str
            The command to execute on the remote PC.
        timeout : int, optional
            Command execution timeout in seconds. If None, uses configured timeout.

        Returns
        -------
        dict
            A dictionary containing the command result with keys:
            - 'success': bool indicating if command executed successfully
            - 'stdout': command standard output
            - 'stderr': command standard error output
            - 'return_code': command exit code

        Examples
        --------
        >>> result = await switch.async_send_ssh_command("ls -la /home")
        >>> if result['success']:
        ...     print(f"Command output: {result['stdout']}")
        """
        if timeout is None:
            timeout = self._ssh_timeout

        result = await self._execute_ssh_command(command, timeout)

        # Return the result for service response
        return {
            "success": result is not None,
            "stdout": result.get("stdout", "") if result else "",
            "stderr": result.get("stderr", "") if result else "",
            "return_code": result.get("return_code", -1) if result else -1,
        }

    async def _execute_ssh_command(
        self, command: str, timeout: int = None
    ) -> dict | None:
        """Execute a command on the remote PC via SSH.

        Parameters
        ----------
        command : str
            The command to execute.
        timeout : int, optional
            SSH connection and command timeout in seconds.

        Returns
        -------
        dict | None
            Dictionary with stdout, stderr, and return_code if successful, None if failed.
        """

        if timeout is None:
            timeout = self._ssh_timeout

        try:
            _LOGGER.info("Executing SSH command on %s: %s", self._host, command)

            # Run SSH connection in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._ssh_execute_sync, command, timeout
            )

            if result:
                _LOGGER.info("SSH command executed successfully")
                _LOGGER.debug("Command stdout: %s", result.get("stdout", ""))
                if result.get("stderr"):
                    _LOGGER.warning("Command stderr: %s", result["stderr"])
            else:
                _LOGGER.error("SSH command execution failed")

            return result

        except Exception as e:
            _LOGGER.error("SSH command execution error: %s", e)
            return None

    def _ssh_execute_sync(self, command: str, timeout: int) -> dict | None:
        """Synchronous SSH command execution helper.

        Parameters
        ----------
        command : str
            The command to execute.
        timeout : int
            SSH connection timeout in seconds.

        Returns
        -------
        dict | None
            Dictionary with command results or None if failed.
        """
        import paramiko

        ssh = None
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self._host,
                port=self._ssh_port,
                username=self._username,
                password=self._password,
                timeout=timeout,
            )

            stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)

            # Wait for command completion
            exit_status = stdout.channel.recv_exit_status()

            stdout_text = stdout.read().decode("utf-8", errors="replace").strip()
            stderr_text = stderr.read().decode("utf-8", errors="replace").strip()

            return {
                "stdout": stdout_text,
                "stderr": stderr_text,
                "return_code": exit_status,
            }

        except Exception as e:
            _LOGGER.error("SSH connection/execution error: %s", e)
            return None
        finally:
            if ssh:
                try:
                    ssh.close()
                except Exception:
                    pass
