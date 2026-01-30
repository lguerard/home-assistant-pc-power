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
# How long (seconds) to hold the monitor switch state after issuing a change
# to allow the remote OS to apply the setting before re-querying.
DEFAULT_MONITOR_PROPAGATION_GRACE = 10

# Monitor timeout switch
MONITOR_TIMEOUT_ENABLED_COMMAND = "powercfg -change -monitor-timeout-ac 30"
MONITOR_TIMEOUT_DISABLED_COMMAND = "powercfg -change -monitor-timeout-ac 0"
MONITOR_TIMEOUT_CHECK_COMMAND = (
    "powershell -NoProfile -NonInteractive -Command "
    "\"((powercfg -query @((powercfg -getactivescheme) -replace '^.+ \\b([0-9a-f]+-[^ ]+).+', '$1' '7516b95f-f776-4464-8c53-06167f40cc99' '3c0bc021-c8a8-4e07-a973-6b14cbcb2b7e'))[-3] -replace '^.+: ') / 60\""
)

