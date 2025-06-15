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
🔗 [github.com/Timman70](https://github.com/Timman70)

---

## 🔐 Disclaimer

Use at your own risk. Ensure your PC’s SSH server and network access are securely configured.
