# 🖥️ PC Power Control – Home Assistant Integration

Control the power state of a Windows PC from Home Assistant using:
- 🔌 Wake-on-LAN to turn it on
- 🔒 SSH to safely shut it down

---

## 🔧 Features

- **Turn on** your PC using Wake-on-LAN
- **Turn off** your PC over SSH with proper shutdown command
- **Status detection** using SSH reachability
- Works with Windows PCs (SSH server required)

---

## 📦 Installation

### HACS (recommended)
1. Add this repository as a custom repository in HACS.
2. Install `PC Power Control`.
3. Restart Home Assistant.
4. Configure via **Settings → Devices & Services → Add Integration → PC Power Control**.

### Manual
1. Download or clone this repo.
2. Copy the `pc_power_control` folder to:
   ```
   /config/custom_components/
   ```
3. Restart Home Assistant.
4. Configure via **Settings → Devices & Services**.

---

## ⚙️ Configuration

When adding the integration, you'll need:

| Field     | Description                        |
|-----------|------------------------------------|
| `Name`    | Friendly name for the PC           |
| `Host`    | IP address of the PC               |
| `MAC`     | MAC address for Wake-on-LAN        |
| `Username`| Windows user with SSH access       |
| `Password`| SSH password                       |

✅ Use `00:11:22:33:44:55` format for MAC address.

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

- The switch entity reflects real-time power state using SSH reachability.
- Turning off uses:  
  `C:\Windows\System32\shutdown.exe /s /f /t 0`
- Logging shows success/error for debugging.

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
🔗 [github.com/TimCloud](https://github.com/TimCloud)

---

## 🔐 Disclaimer

Use at your own risk. Ensure your PC’s SSH server and network access are securely configured.
