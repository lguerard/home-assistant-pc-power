# Monitor Timeout Control - Home Assistant Bubble Card Configuration

This configuration creates a bubble card that allows you to toggle between enabling/disabling monitor timeout on your Windows PC via SSH commands.

## 🎉 **Built-in Switch Available!**

**Good news!** Starting from version 1.05, the PC Power Control integration **automatically creates a monitor timeout switch** for each configured PC. You can use this built-in switch instead of creating custom configuration:

- **Entity**: `switch.{your_pc_name}_monitor_timeout`
- **Automatically available** when PC is online
- **Automatically unavailable** when PC is offline
- **No configuration.yaml changes needed!**

## Prerequisites

1. **PC Power Control Integration**: Make sure you have the PC Power Control integration set up with your Windows PC
2. **Bubble Card**: Install the Bubble Card custom component from HACS
3. **Windows PC**: Ensure your PC has SSH server running and accessible

## 🚀 **Quick Setup (Using Built-in Switch)**

Simply add this bubble card configuration using the automatically created switch:

```yaml
# Simple Bubble Card using Built-in Monitor Timeout Switch
type: custom:bubble-card
card_type: switch
entity: switch.your_pc_name_monitor_timeout  # Replace with your actual PC name
name: Monitor Timeout
icon: mdi:monitor-off
show_state: true
tap_action:
  action: toggle
```

That's it! No need to modify `configuration.yaml` or create helper entities.

## Method 1: Using Template Switch (Recommended)

### Step 1: Add Template Switch to your `configuration.yaml`

```yaml
# Add this to your configuration.yaml
switch:
  - platform: template
    switches:
      pc_monitor_timeout:
        friendly_name: "Monitor Timeout"
        unique_id: "pc_monitor_timeout_switch"
        icon_template: >-
          {% if is_state('input_boolean.monitor_timeout_state', 'on') %}
            mdi:monitor-off
          {% else %}
            mdi:monitor
          {% endif %}
        value_template: "{{ is_state('input_boolean.monitor_timeout_state', 'on') }}"
        turn_on:
          - service: pc_power_control.send_ssh_command
            data:
              command: "powercfg -change -monitor-timeout-ac 30"
              timeout: 10
          - service: input_boolean.turn_on
            target:
              entity_id: input_boolean.monitor_timeout_state
        turn_off:
          - service: pc_power_control.send_ssh_command
            data:
              command: "powercfg -change -monitor-timeout-ac 0"
              timeout: 10
          - service: input_boolean.turn_off
            target:
              entity_id: input_boolean.monitor_timeout_state

# Helper to track state
input_boolean:
  monitor_timeout_state:
    name: "Monitor Timeout State"
    initial: false
```

### Step 2: Add Bubble Card Configuration

Add this to your Lovelace dashboard (either via UI or YAML mode):

```yaml
# Bubble Card Configuration for Monitor Timeout Control
type: custom:bubble-card
card_type: switch
entity: switch.pc_monitor_timeout
name: Monitor Timeout
icon: mdi:monitor
show_state: true
show_attribute: false
show_last_changed: false
tap_action:
  action: toggle
styles: |
  .bubble-button-card-container {
    background: var(--ha-card-background, var(--card-background-color, white));
  }
  .bubble-icon {
    color: var(--primary-color) !important;
  }
  .bubble-name {
    font-weight: 600;
  }
sub_button:
  - name: "30 min"
    icon: mdi:timer-outline
    tap_action:
      action: call-service
      service: switch.turn_on
      target:
        entity_id: switch.pc_monitor_timeout
  - name: "Never"
    icon: mdi:timer-off-outline
    tap_action:
      action: call-service
      service: switch.turn_off
      target:
        entity_id: switch.pc_monitor_timeout
```

## Method 2: Using Scripts (Alternative)

### Step 1: Add Scripts to your `configuration.yaml`

```yaml
# Add this to your configuration.yaml
script:
  enable_monitor_timeout:
    alias: "Enable Monitor Timeout (30 min)"
    icon: mdi:monitor-off
    sequence:
      - service: pc_power_control.send_ssh_command
        data:
          command: "powercfg -change -monitor-timeout-ac 30"
          timeout: 10
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.monitor_timeout_state

  disable_monitor_timeout:
    alias: "Disable Monitor Timeout"
    icon: mdi:monitor
    sequence:
      - service: pc_power_control.send_ssh_command
        data:
          command: "powercfg -change -monitor-timeout-ac 0"
          timeout: 10
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.monitor_timeout_state

# Helper to track state
input_boolean:
  monitor_timeout_state:
    name: "Monitor Timeout State"
    initial: false
```

### Step 2: Bubble Card with Script Buttons

```yaml
# Alternative Bubble Card with Script Buttons
type: custom:bubble-card
card_type: button
entity: input_boolean.monitor_timeout_state
name: Monitor Timeout Control
icon: mdi:monitor-laptop
show_state: true
tap_action:
  action: more-info
sub_button:
  - name: "30 min"
    icon: mdi:timer-outline
    tap_action:
      action: call-service
      service: script.enable_monitor_timeout
    show_background: true
    background_color: "#4CAF50"
  - name: "Never"
    icon: mdi:timer-off-outline
    tap_action:
      action: call-service
      service: script.disable_monitor_timeout
    show_background: true
    background_color: "#FF9800"
```

## Method 3: Advanced Bubble Card with Custom Styling

For a more advanced look with custom styling:

```yaml
type: custom:bubble-card
card_type: button
entity: input_boolean.monitor_timeout_state
name: Monitor Settings
icon: mdi:monitor-dashboard
show_state: true
show_attribute: false
show_last_changed: true
tap_action:
  action: more-info
styles: |
  .bubble-button-card-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 25px;
  }
  .bubble-icon {
    color: white !important;
  }
  .bubble-name, .bubble-state {
    color: white !important;
  }
sub_button:
  - name: "Enable Timeout"
    icon: mdi:timer-sand
    tap_action:
      action: call-service
      service: pc_power_control.send_ssh_command
      service_data:
        command: "powercfg -change -monitor-timeout-ac 30"
        timeout: 10
    show_background: true
    background_color: "#4CAF50"
    styles: |
      .bubble-sub-button {
        border-radius: 15px;
      }
  - name: "Disable Timeout"
    icon: mdi:timer-off
    tap_action:
      action: call-service
      service: pc_power_control.send_ssh_command
      service_data:
        command: "powercfg -change -monitor-timeout-ac 0"
        timeout: 10
    show_background: true
    background_color: "#f44336"
    styles: |
      .bubble-sub-button {
        border-radius: 15px;
      }
```

## Setup Instructions

### 🚀 For Built-in Switch (Recommended):
1. **Install Integration**: Make sure PC Power Control v1.06+ is installed
2. **Find Switch**: Look for `switch.{your_pc_name}_monitor_timeout` entity
3. **Add Bubble Card**: Use the simple bubble card configuration above
4. **Test**: Toggle to control monitor timeout

### 📝 For Custom Template Switch:
1. **Add to Configuration**: Copy the desired method configuration to your `configuration.yaml`
2. **Restart Home Assistant**: Restart to load the new configuration
3. **Add Bubble Card**: Add the bubble card YAML to your dashboard
4. **Test**: Try the buttons to ensure commands work properly

**Note**: The SSH service now automatically uses your PC Power Control integration configuration - no need to specify target entities!

## Troubleshooting

- **Entity not found**: Make sure your PC Power Control integration is set up and the entity name matches
- **SSH commands fail**: Verify SSH access and that PowerShell/CMD has the necessary permissions
- **Bubble card not showing**: Ensure Bubble Card is installed via HACS
- **Commands not working**: Check Home Assistant logs for SSH command errors

## Command Explanations

- `powercfg -change -monitor-timeout-ac 30`: Sets monitor to turn off after 30 minutes when on AC power
- `powercfg -change -monitor-timeout-ac 0`: Disables monitor timeout (never turns off) when on AC power

You can modify the timeout value (30) to any number of minutes you prefer, or use different power schemes by changing `-ac` to `-dc` for battery power settings.