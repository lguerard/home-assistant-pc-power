# 🖥️ PC Power Control – Home Assistant Integration

Control the power state of a Windows PC from Home Assistant using:
- 🔌 Wake-on-LAN to turn it on
- 🔒 SSH to safely shut it down
- ⚙️ Full configuration from the Home Assistant UI

---

## 🔧 Features

- **Turn on** your PC using Wake-on-LAN
- **Turn off** your PC over SSH with proper shutdown command
- **Status detection** using ping
- Works with Windows PCs (SSH server required)
- Configure and edit PC settings directly from Home Assistant UI
- Supports multiple PCs as separate entries
- Prevents duplicates based on IP and MAC address

---

## 🧰 Installation

You can install this integration using either **HACS** (recommended) or **manual setup**.

---

### ✅ Option 1: Install via HACS (Custom Repository)

1. Open Home Assistant and go to **HACS → Integrations**.
2. Click the **⋮ menu (top right)** → **Custom repositories**.
3. Add this repository:

   ```
   https://github.com/Timman70/home-assistant-pc-power
   ```

4. Set category to **Integration**, then click **Add**.
5. Go back to **HACS → Integrations**, search for **PC Power Control**, and install it.
6. Restart Home Assistant.
7. Go to **Settings → Devices & Services → + Add Integration**, then search for **PC Power Control**.

---

### 🛠 Option 2: Manual Installation

If you don’t use HACS:

1. Download this repository as a ZIP:
   [https://github.com/Timman70/home-assistant-pc-power/archive/refs/heads/main.zip](https://github.com/Timman70/home-assistant-pc-power/archive/refs/heads/main.zip)

2. Extract it.

3. Copy the folder `pc_power_control` to your Home Assistant config:

   ```
   /config/custom_components/pc_power_control/
   ```

   You should now have files like:

   ```
   /config/custom_components/pc_power_control/__init__.py
   /config/custom_components/pc_power_control/manifest.json
   /config/custom_components/pc_power_control/switch.py
   ```

4. Restart Home Assistant.
5. Go to **Settings → Devices & Services → + Add Integration**, then search for **PC Power Control**.

---

## ⚙️ Configuration

When adding the integration, you'll need:

| Field         | Description                       | Default |
| ------------- | --------------------------------- | ------- |
| `Name`        | Friendly name for the PC          |         |
| `Host`        | IP address of the PC              |         |
| `MAC`         | MAC address for Wake-on-LAN       |         |
| `Username`    | Windows user with SSH access      |         |
| `Password`    | SSH password                      |         |
| `SSH Port`    | SSH port number (optional)        | 22      |
| `SSH Timeout` | SSH timeout in seconds (optional) | 30      |

✅ Use `00:11:22:33:44:55` format for MAC address.

---

### ✏️ Editing PC Settings

After setup, click **Configure** on the integration to change:
- IP address
- MAC address
- Username
- Password
- Name

All settings are editable directly in the Home Assistant UI.

---

## 🛠 Requirements on Windows PC

- Enable **Wake-on-LAN** in BIOS and network adapter settings.
- Install and configure **OpenSSH Server**:
  1. Run `Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0` in PowerShell (as Admin)
  2. Start service: `Start-Service sshd`
  3. Run on boot: `Set-Service -Name sshd -StartupType 'Automatic'`
- Allow SSH in Windows Firewall.

---

## 📡 Entity Behavior

The integration creates **two switch entities** for each configured PC:

### 🔌 **Main Power Switch** (`switch.{pc_name}`)
- Reflects real-time power state using **ping**
- Turning **on** uses Wake-on-LAN magic packet
- Turning **off** uses: `C:\Windows\System32\shutdown.exe /s /f /t 0`
- Always available for control

### 🖥️ **Monitor Timeout Switch** (`switch.{pc_name}_monitor_timeout`)
- Controls Windows monitor timeout setting (30 minutes vs never)
- Turning **on** sets: `powercfg -change -monitor-timeout-ac 30`
- Turning **off** sets: `powercfg -change -monitor-timeout-ac 0`
- **Only available when PC is online** (becomes "unavailable" when PC is off)
- Automatically detects current timeout state from Windows

Both switches include logging for success/error debugging.

---

## 🚀 SSH Command Service

The integration provides a service to send custom commands to your PC via SSH:

### Service: `pc_power_control.send_ssh_command`

**Parameters:**
- `command` (required): The command to execute on the remote PC
- `timeout` (optional): Command timeout in seconds (default: configured SSH timeout)

**Examples:**

```yaml
# Check disk space
service: pc_power_control.send_ssh_command
target:
  entity_id: switch.my_pc
data:
  command: "dir C:\\"

# Restart a service
service: pc_power_control.send_ssh_command
target:
  entity_id: switch.my_pc
data:
  command: "net restart spooler"
  timeout: 60

# Get system information
service: pc_power_control.send_ssh_command
target:
  entity_id: switch.my_pc
data:
  command: "systeminfo | findstr /C:\"Total Physical Memory\""
```

**Response:** The service returns a dictionary with:
- `success`: Boolean indicating if the command executed successfully
- `stdout`: Command standard output
- `stderr`: Command error output (if any)
- `return_code`: Command exit code

---

## 🎨 Example Configurations

### Bubble Card for Monitor Timeout Control

Want to create a beautiful UI to control your PC's monitor timeout? Check out the included configuration files:

- **[`bubble-card-monitor-timeout.md`](bubble-card-monitor-timeout.md)** - Complete bubble card setup for toggling monitor timeout between 30 minutes and never
- **[`monitor-timeout-automations.md`](monitor-timeout-automations.md)** - Advanced automations for presence-based and schedule-based monitor control

These examples show how to:
- Create toggle switches for common Windows power settings
- Set up automated monitor timeout based on work hours
- Build presence-based power management
- Use custom bubble cards with beautiful styling

---

## 🧪 Troubleshooting

If you see:

> `Config flow could not be loaded: 500 Internal Server Error`

Make sure:
- You deleted all `__pycache__` folders from `/config/custom_components/pc_power_control/`
- You're using the latest version of the integration
- You restarted Home Assistant fully after installing

---

## 🧼 Uninstall & Cleanup

To fully remove entities:
1. Delete the integration from Home Assistant.
2. Remove any leftover entities from **Settings → Entities**.
3. Or use Developer Tools to disable/hide them.

---

## 📘 Example Automation

```yaml
alias: Shut down PC at night
trigger:
  - platform: time
    at: "23:30:00"
condition: []
action:
  - service: switch.turn_off
    target:
      entity_id: switch.my_pc
mode: single
```

---

## 👤 Developer

Created by **TimCloud**
🔗 [github.com/Timman70](https://github.com/Timman70)

---

## 🔐 Disclaimer

Use at your own risk. Ensure your PC’s SSH server and network access are securely configured.
