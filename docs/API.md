# API Reference

## Services

All services are under the `secure_alarm` domain.

### secure_alarm.arm_away

Arm the system in away mode (monitors all zones).

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| pin | string | Yes | User PIN (6-8 digits) |
| code | string | No | User identifier for logging |

**Example:**
```yaml
service: secure_alarm.arm_away
data:
  pin: "123456"
  code: "automation"
```

**Returns:** None (state change reflected in entity)

**Events Fired:**
- `secure_alarm_armed` with `mode: armed_away`
- `secure_alarm_state_changed`

---

### secure_alarm.arm_home

Arm the system in home mode (monitors perimeter only).

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| pin | string | Yes | User PIN (6-8 digits) |
| code | string | No | User identifier for logging |

**Example:**
```yaml
service: secure_alarm.arm_home
data:
  pin: "123456"
```

**Events Fired:**
- `secure_alarm_armed` with `mode: armed_home`

---

### secure_alarm.disarm

Disarm the alarm system.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| pin | string | Yes | User PIN (6-8 digits) |
| code | string | No | User identifier for logging |

**Example:**
```yaml
service: secure_alarm.disarm
data:
  pin: "654321"
  code: "john_doe"
```

**Events Fired:**
- `secure_alarm_disarmed`
- `secure_alarm_duress_code_used` (if duress PIN used)

---

### secure_alarm.add_user

Add a new user to the system (admin only).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| name | string | Yes | - | User's display name |
| pin | string | Yes | - | New user's PIN (6-8 digits) |
| admin_pin | string | Yes | - | Admin PIN for authorization |
| is_admin | boolean | No | false | Grant admin privileges |
| is_duress | boolean | No | false | Is this a duress code |

**Example:**
```yaml
service: secure_alarm.add_user
data:
  name: "Jane Doe"
  pin: "789012"
  admin_pin: "000000"
  is_admin: false
  is_duress: false
```

**Returns:** User ID in logs

---

### secure_alarm.remove_user

Remove a user from the system (admin only).

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | ID of user to remove |
| admin_pin | string | Yes | Admin PIN for authorization |

**Example:**
```yaml
service: secure_alarm.remove_user
data:
  user_id: 5
  admin_pin: "000000"
```

---

### secure_alarm.bypass_zone

Bypass or unbypass a zone temporarily.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| zone_entity_id | string | Yes | - | Entity ID of zone sensor |
| pin | string | Yes | - | User PIN |
| bypass | boolean | No | true | True to bypass, false to restore |

**Example:**
```yaml
service: secure_alarm.bypass_zone
data:
  zone_entity_id: binary_sensor.garage_door
  pin: "123456"
  bypass: true
```

---

### secure_alarm.update_config

Update system configuration (admin only).

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| admin_pin | string | Yes | Admin PIN for authorization |
| entry_delay | integer | No | Entry delay in seconds (0-300) |
| exit_delay | integer | No | Exit delay in seconds (0-300) |
| alarm_duration | integer | No | Alarm duration in seconds (60-3600) |
| lock_delay_home | integer | No | Lock delay for arm home (0-60) |
| lock_delay_away | integer | No | Lock delay for arm away (0-300) |
| close_delay_home | integer | No | Garage close delay for arm home |
| close_delay_away | integer | No | Garage close delay for arm away |
| notification_mobile | boolean | No | Enable mobile notifications |
| notification_sms | boolean | No | Enable SMS notifications |
| sms_numbers | string | No | Comma-separated phone numbers |

**Example:**
```yaml
service: secure_alarm.update_config
data:
  admin_pin: "000000"
  entry_delay: 45
  exit_delay: 90
  notification_mobile: true
  notification_sms: true
  sms_numbers: "+15551234567,+15559876543"
```

---

## Events

### secure_alarm_armed

Fired when system is armed.

**Data:**
```yaml
mode: "armed_away"  # or "armed_home"
changed_by: "John Doe"
timestamp: "2024-01-15T10:30:00"
```

---

### secure_alarm_disarmed

Fired when system is disarmed.

**Data:**
```yaml
changed_by: "Jane Doe"
timestamp: "2024-01-15T18:45:00"
```

---

### secure_alarm_triggered

Fired when alarm is triggered.

**Data:**
```yaml
zone: "Front Door"
zone_entity_id: "binary_sensor.front_door"
timestamp: "2024-01-15T02:30:00"
```

---

### secure_alarm_duress_code_used

Fired when a duress code is used (silent alert).

**Data:**
```yaml
user_name: "Duress Code"
user_id: 10
timestamp: "2024-01-15T23:15:00"
```

---

### secure_alarm_failed_auth

Fired on failed PIN attempts.

**Data:**
```yaml
attempts: 3
locked_out: false
timestamp: "2024-01-15T14:20:00"
```

---

### secure_alarm_state_changed

Fired on any state change.

**Data:**
```yaml
state: "armed_away"
previous_state: "disarmed"
changed_by: "Automation"
timestamp: "2024-01-15T08:00:00"
```

---

## Entities

### alarm_control_panel.secure_alarm

Main alarm control panel entity.

**States:**
- `disarmed` - System is off
- `armed_home` - Perimeter armed
- `armed_away` - All zones armed
- `arming` - Exit delay in progress
- `pending` - Entry delay in progress
- `triggered` - Alarm activated

**Attributes:**
```yaml
changed_by: "John Doe"
code_format: "number"
zones_bypassed: ["Garage Door"]
active_zones: 6
failed_attempts: 0
triggered_by: null
```

---

### sensor.secure_alarm_status

Current alarm status.

**State:** Human-readable status text

**Attributes:**
```yaml
state_raw: "armed_away"
changed_by: "Jane Doe"
triggered_by: null
```

---

### sensor.secure_alarm_failed_login_attempts

Failed PIN attempt counter.

**State:** Number of recent failed attempts

**Unit:** attempts

---

### sensor.secure_alarm_last_changed_by

Last user who changed alarm state.

**State:** User name or "Unknown"

---

### sensor.secure_alarm_active_zones

Number of currently monitored zones.

**State:** Zone count

**Attributes:**
```yaml
total_zones: 6
bypassed_zones: []
```

---

### binary_sensor.secure_alarm_armed

Is the system armed (any mode)?

**State:** `on` (armed) or `off` (disarmed)

**Device Class:** safety

---

### binary_sensor.secure_alarm_triggered

Is the alarm currently triggered?

**State:** `on` (triggered) or `off` (not triggered)

**Device Class:** problem

---

### binary_sensor.secure_alarm_locked_out

Is the system locked due to failed attempts?

**State:** `on` (locked) or `off` (not locked)

**Device Class:** lock

---

## Python Script API

### register_alarm_zone.py

Register a sensor as an alarm zone.

**Parameters:**
```python
entity_id: str        # Sensor entity ID
zone_type: str        # "entry", "perimeter", or "interior"
enabled_away: bool    # Monitor in away mode
enabled_home: bool    # Monitor in home mode
```

**Example:**
```yaml
service: python_script.register_alarm_zone
data:
  entity_id: binary_sensor.front_door
  zone_type: entry
  enabled_away: true
  enabled_home: false
```

---

## Database Schema

### Table: alarm_users

```sql
id INTEGER PRIMARY KEY
name TEXT NOT NULL
pin_hash TEXT NOT NULL
is_admin INTEGER DEFAULT 0
is_duress INTEGER DEFAULT 0
enabled INTEGER DEFAULT 1
created_at TIMESTAMP
last_used TIMESTAMP
use_count INTEGER DEFAULT 0
```

---

### Table: alarm_config

```sql
id INTEGER PRIMARY KEY DEFAULT 1
entry_delay INTEGER DEFAULT 30
exit_delay INTEGER DEFAULT 60
alarm_duration INTEGER DEFAULT 300
trigger_doors TEXT
notification_mobile INTEGER DEFAULT 1
notification_sms INTEGER DEFAULT 0
sms_numbers TEXT
lock_delay_home INTEGER DEFAULT 0
lock_delay_away INTEGER DEFAULT 60
close_delay_home INTEGER DEFAULT 0
close_delay_away INTEGER DEFAULT 60
updated_at TIMESTAMP
```

---

### Table: alarm_events

```sql
id INTEGER PRIMARY KEY
event_type TEXT NOT NULL
user_id INTEGER
user_name TEXT
timestamp TIMESTAMP
state_from TEXT
state_to TEXT
zone_entity_id TEXT
details TEXT
is_duress INTEGER DEFAULT 0
```

---

### Table: alarm_zones

```sql
id INTEGER PRIMARY KEY
entity_id TEXT UNIQUE NOT NULL
zone_name TEXT NOT NULL
zone_type TEXT NOT NULL
enabled_away INTEGER DEFAULT 1
enabled_home INTEGER DEFAULT 1
bypassed INTEGER DEFAULT 0
bypass_until TIMESTAMP
last_state_change TIMESTAMP
```

---

### Table: failed_attempts

```sql
id INTEGER PRIMARY KEY
timestamp TIMESTAMP
ip_address TEXT
user_code TEXT
attempt_type TEXT
```

---

## REST API (Via Home Assistant)

All services can be called via Home Assistant REST API:

```bash
curl -X POST \
  http://homeassistant.local:8123/api/services/secure_alarm/arm_away \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pin": "123456"}'
```

---

## WebSocket API

Subscribe to events via WebSocket:

```javascript
{
  "type": "subscribe_events",
  "event_type": "secure_alarm_triggered"
}
```

---

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| `pin_invalid` | Invalid PIN | PIN format incorrect or doesn't exist |
| `pin_locked` | System locked out | Too many failed attempts |
| `pin_length` | PIN must be 6-8 digits | PIN length validation failed |
| `admin_required` | Admin authorization required | Action requires admin PIN |
| `zone_not_found` | Zone not found | Zone entity ID doesn't exist |
| `already_armed` | System already armed | Cannot arm when already armed |
| `database_error` | Database operation failed | Database query failed |

---

## Rate Limits

- **Failed PIN attempts**: 5 attempts per 5 minutes
- **API calls**: No hard limit (subject to HA limits)
- **Monitoring heartbeat**: Default 1 per hour

---

## Versioning

API version follows integration version (v1.0.0).

Breaking changes will increment major version.