# Configuration Guide

## Table of Contents
- [Timing Configuration](#timing-configuration)
- [Zone Configuration](#zone-configuration)
- [User Management](#user-management)
- [Notifications](#notifications)
- [Entry Points](#entry-points)
- [Automations](#automations)

## Timing Configuration

### Update Delays

```yaml
service: secure_alarm.update_config
data:
  admin_pin: "YOUR_ADMIN_PIN"
  entry_delay: 30          # Seconds to disarm after entry
  exit_delay: 60           # Seconds to exit after arming away
  alarm_duration: 300      # Seconds alarm sounds
  lock_delay_home: 0       # Instant lock when arm home
  lock_delay_away: 60      # Lock after exit delay
  close_delay_home: 0      # Instant garage close
  close_delay_away: 60     # Close after exit delay
```

**Entry Delay**: Time allowed to disarm after opening entry door
- Recommended: 30 seconds
- Range: 0-300 seconds
- Set to 0 for instant trigger

**Exit Delay**: Time to exit before system arms
- Recommended: 60 seconds  
- Range: 0-300 seconds
- Only applies to arm_away mode

**Alarm Duration**: How long siren sounds
- Recommended: 300 seconds (5 minutes)
- Range: 60-3600 seconds
- Can be stopped early by disarming

## Zone Configuration

### Zone Types

**Entry Zones**: Allow entry delay
- Front door, back door, garage
- Gives time to disarm before triggering
- Use for primary entry points

**Perimeter Zones**: Instant trigger
- Windows, basement doors, side doors
- No delay when armed
- Use for points that shouldn't be opened when armed

**Interior Zones**: Motion detectors, glass break
- Only active in armed_away mode
- Ignored in armed_home mode
- Instant trigger

### Register Zone

```yaml
service: python_script.register_alarm_zone
data:
  entity_id: binary_sensor.front_door
  zone_type: entry              # entry, perimeter, or interior
  enabled_away: true            # Monitor in away mode
  enabled_home: false           # Don't monitor in home mode
```

### Zone Blueprint

Use automation blueprint for easier configuration:

1. Import blueprint from `/blueprints/automation/secure_alarm/configure_zones.yaml`
2. Create automation
3. Select entities for each zone
4. Set zone types
5. Enable/disable for each arm mode

### Bypass Zone

Temporarily disable a zone:

```yaml
service: secure_alarm.bypass_zone
data:
  zone_entity_id: binary_sensor.garage_door
  pin: "YOUR_PIN"
  bypass: true    # false to re-enable
```

**Use Cases**:
- Working in garage while armed
- Window open for ventilation
- Sensor maintenance/replacement

## User Management

### Add User

```yaml
service: secure_alarm.add_user
data:
  name: "John Doe"
  pin: "123456"              # 6-8 digits
  admin_pin: "ADMIN_PIN"     # Your admin PIN
  is_admin: false            # Grant admin privileges
  is_duress: false           # Is this a duress code
```

### Admin vs Regular Users

**Admin Can**:
- Add/remove users
- Change configuration
- Bypass zones
- View audit logs

**Regular Users Can**:
- Arm/disarm system
- Use all arm modes
- View current status

### Duress Code

Silent alarm that appears to work normally:

```yaml
service: secure_alarm.add_user
data:
  name: "Duress - Silent Alert"
  pin: "999999"
  admin_pin: "ADMIN_PIN"
  is_admin: false
  is_duress: true          # This makes it a duress code
```

**When duress code is used**:
- System appears to disarm normally
- Silent notification sent to admin
- Event logged with duress flag
- No visible indication to intruder

### Remove User

```yaml
service: secure_alarm.remove_user
data:
  user_id: 2               # Get from database or logs
  admin_pin: "ADMIN_PIN"
```

## Notifications

### Mobile Notifications

Enabled by default if Home Assistant Companion app installed.

**Customize**:
```yaml
service: secure_alarm.update_config
data:
  admin_pin: "ADMIN_PIN"
  notification_mobile: true
```

**Notification Events**:
- System armed/disarmed
- Alarm triggered
- Entry delay started
- Duress code used
- Failed PIN attempts
- System locked out

### SMS Notifications

Requires Twilio or similar SMS integration.

**Setup Twilio**:
```yaml
# configuration.yaml
notify:
  - platform: twilio_sms
    name: sms
    account_sid: !secret twilio_account_sid
    auth_token: !secret twilio_auth_token
    from_number: !secret twilio_from_number
```

**Enable SMS**:
```yaml
service: secure_alarm.update_config
data:
  admin_pin: "ADMIN_PIN"
  notification_sms: true
  sms_numbers: "+15551234567,+15559876543"
```

**SMS Events**:
- Alarm triggered
- Duress code used
- System armed away (optional)

### Custom Notifications

Create automations for custom notification logic:

```yaml
automation:
  - alias: "Custom Alarm Notification"
    trigger:
      - platform: event
        event_type: secure_alarm_triggered
    action:
      - service: notify.custom_service
        data:
          title: "Alarm!"
          message: "{{ trigger.event.data.zone }}"
```

## Entry Points

Configure door locks and garage doors in Lovelace card.

### Card Configuration

```yaml
type: custom:secure-alarm-card
entity: alarm_control_panel.secure_alarm
entry_points:
  - entity_id: lock.front_door
    name: Front Door
    type: door                           # door or garage
    battery_entity: sensor.front_door_battery
  
  - entity_id: lock.back_door
    name: Back Door
    type: door
    battery_entity: sensor.back_door_battery
  
  - entity_id: cover.garage_door
    name: Garage Door
    type: garage
    # No battery for hardwired garage
```

### Entry Point Types

**door**: Lock/unlock icon, shows locked/unlocked state
**garage**: Garage icon, shows open/closed state

### Battery Monitoring

Optional battery level display:
- Shows percentage next to entry point
- Color coded: Green (>50%), Yellow (20-50%), Red (<20%)
- Omit `battery_entity` for hardwired devices

### Last Changed Timestamp

Automatically tracked:
- Shows "5m ago", "2h ago", "3d ago"
- Updates when state changes
- Helps identify unusual activity

## Automations

### Auto-Arm on Departure

```yaml
automation:
  - alias: "Auto Arm Away"
    trigger:
      - platform: state
        entity_id: group.all_persons
        to: "not_home"
        for: "00:05:00"
    condition:
      - condition: state
        entity_id: alarm_control_panel.secure_alarm
        state: "disarmed"
    action:
      - service: secure_alarm.arm_away
        data:
          pin: !secret alarm_automation_pin
```

### Auto-Disarm on Arrival

```yaml
automation:
  - alias: "Auto Disarm"
    trigger:
      - platform: state
        entity_id: person.john
        to: "home"
    condition:
      - condition: state
        entity_id: alarm_control_panel.secure_alarm
        state: "armed_away"
    action:
      - service: secure_alarm.disarm
        data:
          pin: !secret alarm_automation_pin
```

### Bedtime Arm Home

```yaml
automation:
  - alias: "Arm Home at Bedtime"
    trigger:
      - platform: time
        at: "23:00:00"
    condition:
      - condition: state
        entity_id: alarm_control_panel.secure_alarm
        state: "disarmed"
    action:
      - service: secure_alarm.arm_home
        data:
          pin: !secret alarm_automation_pin
```

### Trigger Response

```yaml
automation:
  - alias: "Alarm Triggered Actions"
    trigger:
      - platform: event
        event_type: secure_alarm_triggered
    action:
      # Turn on all lights
      - service: light.turn_on
        target:
          entity_id: all
        data:
          brightness: 255
      
      # Take camera snapshots
      - service: camera.snapshot
        target:
          entity_id: camera.front_door
        data:
          filename: "/config/www/alarm_{{ now().timestamp() }}.jpg"
      
      # Send notification
      - service: notify.mobile_app_all
        data:
          title: "🚨 ALARM!"
          message: "Zone: {{ trigger.event.data.zone }}"
```

## Advanced Configuration

### Professional Monitoring

```yaml
# configuration.yaml
secure_alarm:
  monitoring:
    enabled: true
    protocol: contact_id    # contact_id, alarm_net, sia, webhook
    endpoint: "monitoring.example.com:5000"
    account_id: "1234"
    api_key: "your-api-key"
    test_mode: false
    heartbeat_enabled: true
    heartbeat_interval: 3600
```

### Vacation Mode

```yaml
input_boolean:
  vacation_mode:
    name: Vacation Mode
    icon: mdi:beach

automation:
  - alias: "Vacation Mode Arm"
    trigger:
      - platform: state
        entity_id: input_boolean.vacation_mode
        to: "on"
    action:
      - service: secure_alarm.arm_away
        data:
          pin: !secret alarm_automation_pin
```

### Zone-Specific Delays

Different delays per zone not directly supported, but can be achieved with template sensors and automations.

## Secrets Management

Store sensitive data in `secrets.yaml`:

```yaml
# secrets.yaml
alarm_automation_pin: "123456"
alarm_admin_pin: "000000"
emergency_phone: "+15551234567"
twilio_account_sid: "AC..."
twilio_auth_token: "..."
twilio_from_number: "+15559999999"
```

Reference in configs:
```yaml
pin: !secret alarm_automation_pin
```

## Database Maintenance

### View Audit Logs

Query database directly:
```sql
sqlite3 /config/secure_alarm.db "SELECT * FROM alarm_events ORDER BY timestamp DESC LIMIT 20;"
```

### Backup Database

```bash
cp /config/secure_alarm.db /config/backups/secure_alarm_$(date +%Y%m%d).db
```

### Clean Old Events

Automatically managed by integration. Manual cleanup:
```sql
sqlite3 /config/secure_alarm.db "DELETE FROM alarm_events WHERE timestamp < date('now', '-90 days');"
```

## Troubleshooting Configuration

### Check Current Config

```yaml
service: python_script.get_alarm_config
```

### Verify Zone Registration

Check Developer Tools → States for:
- `sensor.secure_alarm_active_zones`
- Zone attributes on alarm entity

### Test Notifications

```yaml
service: notify.mobile_app_phone
data:
  title: "Test"
  message: "Alarm notification test"
```

### Validate User PINs

Attempt to arm with each user's PIN to verify they work.

### Reset Configuration

Last resort - remove integration and re-add:
1. Delete integration from UI
2. Remove `/config/secure_alarm.db`
3. Re-add integration
4. Reconfigure all settings