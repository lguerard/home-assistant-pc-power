import asyncio
import logging
from asyncio.subprocess import PIPE

import wakeonlan
from homeassistant.components.switch import SwitchEntity

from .const import (
    DEFAULT_SSH_TIMEOUT,
    DOMAIN,
    MONITOR_TIMEOUT_CHECK_COMMAND,
    MONITOR_TIMEOUT_DISABLED_COMMAND,
    MONITOR_TIMEOUT_ENABLED_COMMAND,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up PC Power Control switches."""
    data = config_entry.data

    # Create main power switch
    power_switch = PCPowerSwitch(
        data["name"],
        data["host"],
        data["mac"],
        data["username"],
        data["password"],
        data.get("ssh_port", 22),
        data.get("ssh_timeout", DEFAULT_SSH_TIMEOUT),
    )

    # Create monitor timeout switch
    monitor_switch = PCMonitorTimeoutSwitch(
        data["name"],
        data["host"],
        data["username"],
        data["password"],
        data.get("ssh_port", 22),
        data.get("ssh_timeout", DEFAULT_SSH_TIMEOUT),
        power_switch,  # Pass reference to power switch
    )

    async_add_entities([power_switch, monitor_switch])

    # Store switch reference for domain service
    hass.data[DOMAIN].setdefault("switches", {})
    hass.data[DOMAIN]["switches"][data["name"]] = power_switch


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
        # Persistent SSH client to reduce connection overhead for repeated commands
        self._ssh_client = None

    @property
    def is_on(self):
        # Implement logic to check actual PC state
        return self._attr_is_on

    async def async_turn_on(self, **kwargs):
        _LOGGER.info("Sending Wake-on-LAN to MAC %s", self._mac)
        wakeonlan.send_magic_packet(self._mac)
        self._attr_is_on = True
        # Update HA state immediately so Developer Tools / UI reflect change
        try:
            self.async_write_ha_state()
        except Exception:
            # Not critical if writing state fails
            pass

    async def async_turn_off(self, **kwargs):
        """Turn off the PC by sending a shutdown command via SSH."""
        try:
            _LOGGER.info("Sending shutdown command to %s via SSH", self._host)
            result = await self._execute_ssh_command("shutdown -s -f -t 0")
            # consider success only when command returned exit code 0
            if result and result.get("return_code") == 0:
                self._attr_is_on = False
                _LOGGER.info("Shutdown command executed successfully")
                try:
                    self.async_write_ha_state()
                except Exception:
                    pass
            else:
                _LOGGER.error("Failed to execute shutdown command: %s", result)
        except Exception as e:
            _LOGGER.error("Failed to shut down PC: %s", e)

    async def async_will_remove_from_hass(self) -> None:
        """Clean up resources when entity is removed from Home Assistant."""
        await self.async_close_ssh()

    async def async_close_ssh(self) -> None:
        """Close any persistent SSH client (runs in executor)."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._close_ssh_sync)

    def _close_ssh_sync(self) -> None:
        """Synchronous close helper for SSH client."""
        try:
            if getattr(self, "_ssh_client", None):
                try:
                    self._ssh_client.close()
                except Exception:
                    pass
        finally:
            self._ssh_client = None

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

        # Consider success only if we got a result and the return code is 0
        success = bool(result and result.get("return_code") == 0)

        # Return the result for service response
        return {
            "success": success,
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

        # Reuse a persistent SSH client where possible to avoid reconnecting
        try:
            ssh = None
            try:
                # Try to reuse existing client
                if getattr(self, "_ssh_client", None):
                    transport = self._ssh_client.get_transport()
                    if transport and transport.is_active():
                        ssh = self._ssh_client
                    else:
                        try:
                            self._ssh_client.close()
                        except Exception:
                            pass
                        self._ssh_client = None

                if ssh is None:
                    # Establish a new client and keep it for reuse
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(
                        self._host,
                        port=self._ssh_port,
                        username=self._username,
                        password=self._password,
                        timeout=timeout,
                    )
                    self._ssh_client = ssh

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
                # On error, drop the persistent client so future attempts reconnect
                _LOGGER.debug("SSH execution error, dropping client: %s", e)
                try:
                    if getattr(self, "_ssh_client", None):
                        self._ssh_client.close()
                except Exception:
                    pass
                self._ssh_client = None
                _LOGGER.error("SSH connection/execution error: %s", e)
                return None
        finally:
            # Do not close the client here; keep it for reuse
            pass


class PCMonitorTimeoutSwitch(SwitchEntity):
    """Monitor Timeout Control Switch Entity."""

    def __init__(
        self,
        pc_name: str,
        host: str,
        username: str,
        password: str,
        ssh_port: int = 22,
        ssh_timeout: int = DEFAULT_SSH_TIMEOUT,
        power_switch: PCPowerSwitch = None,
    ):
        """Initialize the Monitor Timeout Switch.

        Parameters
        ----------
        pc_name : str
            The name of the PC for entity naming.
        host : str
            The IP address or hostname of the remote PC.
        username : str
            SSH username for remote PC access.
        password : str
            SSH password for remote PC access.
        ssh_port : int, optional
            SSH port number (default is 22).
        ssh_timeout : int, optional
            SSH connection timeout in seconds (default is 30).
        power_switch : PCPowerSwitch, optional
            Reference to the main power switch for status checking.
        """
        self._host = host
        self._username = username
        self._password = password
        self._ssh_port = ssh_port
        self._ssh_timeout = ssh_timeout
        self._power_switch = power_switch
        self._pc_name = pc_name

        self._attr_name = f"{pc_name} Monitor Timeout"
        self._attr_should_poll = True
        self._attr_is_on = None  # Unknown initially
        self._attr_unique_id = f"pc_monitor_timeout_{host.replace('.', '_')}"
        self._attr_icon = "mdi:monitor-off"
        self._attr_device_class = None

    @property
    def available(self) -> bool:
        """Return if entity is available.

        The monitor timeout switch is only available when the PC is online.
        """
        if self._power_switch:
            return self._power_switch.is_on
        return True  # Fallback if no power switch reference

    @property
    def is_on(self) -> bool:
        """Return true if monitor timeout is enabled (30 minutes)."""
        return self._attr_is_on

    async def async_turn_on(self, **kwargs):
        """Turn on monitor timeout (set to 30 minutes)."""
        try:
            _LOGGER.info("Enabling monitor timeout (30 min) on %s", self._host)
            if not self._power_switch:
                _LOGGER.error("No power switch reference available to run SSH commands")
                return

            result = await self._power_switch.async_send_ssh_command(
                MONITOR_TIMEOUT_ENABLED_COMMAND, timeout=self._ssh_timeout
            )

            if result.get("success") and result.get("return_code") == 0:
                self._attr_is_on = True
                _LOGGER.info("Monitor timeout enabled successfully")
                # Write state immediately for faster UI feedback
                self.async_write_ha_state()
            else:
                _LOGGER.error(
                    "Failed to enable monitor timeout: %s",
                    result.get("stderr", "Unknown error"),
                )
        except Exception as e:
            _LOGGER.error("Failed to enable monitor timeout: %s", e)

    async def async_turn_off(self, **kwargs):
        """Turn off monitor timeout (disable - never timeout)."""
        try:
            _LOGGER.info("Disabling monitor timeout on %s", self._host)
            if not self._power_switch:
                _LOGGER.error("No power switch reference available to run SSH commands")
                return

            result = await self._power_switch.async_send_ssh_command(
                MONITOR_TIMEOUT_DISABLED_COMMAND, timeout=self._ssh_timeout
            )

            if result.get("success") and result.get("return_code") == 0:
                self._attr_is_on = False
                _LOGGER.info("Monitor timeout disabled successfully")
                # Write state immediately for faster UI feedback
                self.async_write_ha_state()
            else:
                _LOGGER.error(
                    "Failed to disable monitor timeout: %s",
                    result.get("stderr", "Unknown error"),
                )
        except Exception as e:
            _LOGGER.error("Failed to disable monitor timeout: %s", e)

    async def async_update(self):
        """Update the current monitor timeout state."""
        if not self.available:
            self._attr_is_on = None
            return

        try:
            # Query current monitor timeout setting via power switch helper to reuse SSH connection
            if not self._power_switch:
                _LOGGER.debug("No power switch reference available to query monitor timeout")
                return

            result = await self._power_switch.async_send_ssh_command(
                MONITOR_TIMEOUT_CHECK_COMMAND, timeout=self._ssh_timeout
            )
            if result and result.get("return_code") == 0:
                output = result.get("stdout", "")
                # Parse the output to determine current timeout
                # powercfg output shows timeout in seconds (0x00000000 = disabled, 0x00000708 = 30 min = 1800 seconds)
                if "0x00000000" in output:
                    self._attr_is_on = False  # Timeout disabled
                elif "0x00000708" in output or "1800" in output:
                    self._attr_is_on = True  # 30 minute timeout
                else:
                    # Try to extract timeout value and determine if it's enabled
                    import re

                    hex_match = re.search(r"0x([0-9a-fA-F]+)", output)
                    if hex_match:
                        timeout_seconds = int(hex_match.group(1), 16)
                        self._attr_is_on = timeout_seconds > 0
                    else:
                        _LOGGER.debug(
                            "Could not parse monitor timeout output: %s", output
                        )
            else:
                _LOGGER.debug("Failed to query monitor timeout status")
        except Exception as e:
            _LOGGER.debug("Error updating monitor timeout status: %s", e)
        # Monitor switch uses the main power switch's SSH helper; nothing else to do here.
