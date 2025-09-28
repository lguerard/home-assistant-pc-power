# Monitor Timeout Automation Examples

Here are some useful automation examples that work with the monitor timeout bubble card:

## Automation 1: Auto-disable timeout during work hours

```yaml
automation:
  - alias: "Disable Monitor Timeout During Work Hours"
    description: "Automatically disable monitor timeout during work hours on weekdays"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.pc_monitor_timeout
      - service: notify.persistent_notification
        data:
          message: "Monitor timeout disabled for work hours"
          title: "PC Settings Updated"

  - alias: "Re-enable Monitor Timeout After Work"
    description: "Re-enable monitor timeout after work hours"
    trigger:
      - platform: time
        at: "18:00:00"
    condition:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.pc_monitor_timeout
      - service: notify.persistent_notification
        data:
          message: "Monitor timeout re-enabled (30 minutes)"
          title: "PC Settings Updated"
```

## Automation 2: Gaming mode (disable timeout when specific apps are running)

```yaml
automation:
  - alias: "Gaming Mode - Disable Monitor Timeout"
    description: "Disable monitor timeout when gaming applications are detected"
    trigger:
      - platform: state
        entity_id: sensor.pc_active_window  # You'd need to create this sensor
    condition:
      - condition: template
        value_template: >
          {{ 'steam' in states('sensor.pc_active_window')|lower or
             'game' in states('sensor.pc_active_window')|lower or
             'epic games' in states('sensor.pc_active_window')|lower }}
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.pc_monitor_timeout
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.gaming_mode

  - alias: "Gaming Mode - Re-enable Monitor Timeout"
    description: "Re-enable monitor timeout when gaming stops"
    trigger:
      - platform: state
        entity_id: input_boolean.gaming_mode
        to: 'off'
        for: "00:05:00"  # 5 minutes after gaming stops
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.pc_monitor_timeout
```

## Automation 3: Presence-based timeout control

```yaml
automation:
  - alias: "Monitor Timeout Based on Presence"
    description: "Adjust monitor timeout based on home presence"
    trigger:
      - platform: state
        entity_id: zone.home
    action:
      - choose:
          - conditions:
              - condition: numeric_state
                entity_id: zone.home
                above: 0  # Someone is home
            sequence:
              - service: switch.turn_on
                target:
                  entity_id: switch.pc_monitor_timeout
        default:
          - service: switch.turn_off
            target:
              entity_id: switch.pc_monitor_timeout
```

## Additional Helper Entities

Add these to your `configuration.yaml` for enhanced functionality:

```yaml
# Gaming mode helper
input_boolean:
  gaming_mode:
    name: "Gaming Mode"
    initial: false

# Custom timeout values
input_number:
  monitor_timeout_minutes:
    name: "Monitor Timeout (Minutes)"
    initial: 30
    min: 1
    max: 120
    step: 1
    unit_of_measurement: "min"

# Template sensor for current timeout status
template:
  - sensor:
      - name: "Monitor Timeout Status"
        unique_id: "monitor_timeout_status"
        state: >
          {% if is_state('input_boolean.monitor_timeout_state', 'on') %}
            {{ states('input_number.monitor_timeout_minutes')|int }} minutes
          {% else %}
            Never
          {% endif %}
        icon: >
          {% if is_state('input_boolean.monitor_timeout_state', 'on') %}
            mdi:monitor-off
          {% else %}
            mdi:monitor
          {% endif %}
```

## Script for Custom Timeout Values

```yaml
script:
  set_custom_monitor_timeout:
    alias: "Set Custom Monitor Timeout"
    fields:
      timeout_minutes:
        description: "Timeout in minutes (0 = never)"
        example: 15
    sequence:
      - service: pc_power_control.send_ssh_command
        target:
          entity_id: switch.your_pc_name  # Replace with your PC entity
        data:
          command: "powercfg -change -monitor-timeout-ac {{ timeout_minutes }}"
          timeout: 10
      - service: input_number.set_value
        target:
          entity_id: input_number.monitor_timeout_minutes
        data:
          value: "{{ timeout_minutes }}"
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.monitor_timeout_state
        condition:
          - condition: template
            value_template: "{{ timeout_minutes|int > 0 }}"
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.monitor_timeout_state
        condition:
          - condition: template
            value_template: "{{ timeout_minutes|int == 0 }}"
```

These automations and helpers will make your monitor timeout control even more powerful and automatic!