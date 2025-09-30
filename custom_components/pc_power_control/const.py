DOMAIN = "pc_power_control"

# Services
SERVICE_SEND_COMMAND = "send_ssh_command"

# Service attributes
ATTR_COMMAND = "command"
ATTR_TIMEOUT = "timeout"
ATTR_PC_NAME = "pc_name"

# Default values
DEFAULT_SSH_TIMEOUT = 30
# Number of seconds to consider the PC "booting" after a Wake-on-LAN packet
# During this window, the integration will treat the PC as ON to avoid a
# premature ping-based off state while the machine boots.
DEFAULT_BOOT_GRACE = 60

# Monitor timeout switch
MONITOR_TIMEOUT_ENABLED_COMMAND = "powercfg -change -monitor-timeout-ac 30"
MONITOR_TIMEOUT_DISABLED_COMMAND = "powercfg -change -monitor-timeout-ac 0"
MONITOR_TIMEOUT_CHECK_COMMAND = "powercfg -query SCHEME_CURRENT SUB_VIDEO VIDEOIDLE"
