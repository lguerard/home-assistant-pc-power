DOMAIN = "pc_power_control"

# Services
SERVICE_SEND_COMMAND = "send_ssh_command"

# Service attributes
ATTR_COMMAND = "command"
ATTR_TIMEOUT = "timeout"

# Default values
DEFAULT_SSH_TIMEOUT = 30

# Monitor timeout switch
MONITOR_TIMEOUT_ENABLED_COMMAND = "powercfg -change -monitor-timeout-ac 30"
MONITOR_TIMEOUT_DISABLED_COMMAND = "powercfg -change -monitor-timeout-ac 0"
MONITOR_TIMEOUT_CHECK_COMMAND = "powercfg -query SCHEME_CURRENT SUB_VIDEO VIDEOIDLE"
