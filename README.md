# Secure Alarm System for Home Assistant

[![GitHub Release](https://img.shields.io/github/release/mmotrock/ha-secure-alarm.svg?style=for-the-badge)](https://github.com/mmotrock/ha-secure-alarm/releases)
[![License](https://img.shields.io/github/license/mmotrock/ha-secure-alarm.svg?style=for-the-badge)](LICENSE)
[![hacs](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1+-41BDF5.svg?style=for-the-badge)](https://www.home-assistant.io)

A professional-grade, security-focused alarm system integration for Home Assistant featuring dedicated PIN authentication, comprehensive audit logging, and native support for wired sensors via ESP32.

![Alarm Badge Card](docs/images/alarm-badge.png)

## ✨ Features

### 🔐 Security First
- **Dedicated PIN Authentication** - 6-8 digit PINs completely separate from Home Assistant users
- **Bcrypt Encryption** - Military-grade password hashing, zero plaintext storage
- **Duress Codes** - Silent alert codes that appear normal but trigger emergency notifications
- **Rate Limiting** - Automatic 5-minute lockout after 5 failed attempts
- **Complete Audit Trail** - Every action logged with timestamps, user IDs, and details

### 🚨 Professional Alarm Features
- **Multiple Arm Modes** - Away (all zones), Home (perimeter only)
- **Smart Delays** - Configurable entry (30s) and exit (60s) delays
- **Three Zone Types** - Entry (delayed), Perimeter (instant), Interior (motion)
- **Unlimited Zones** - Start with 6, expand to 128+ with GPIO expanders
- **Auto-Secure** - Automatically locks doors and closes garage when arming
- **Zone Bypass** - Temporarily disable sensors with PIN authorization

### 📱 Advanced Notifications
- **Mobile Push** - Native Home Assistant companion app integration
- **SMS Alerts** - Twilio/SMS support for critical events
- **Event Types** - Armed, disarmed, triggered, duress, failed attempts, lockouts
- **Professional Monitoring** - Contact ID, AlarmNet, SIA protocol support

### 👥 Multi-User Management
- **Unlimited Users** - Each with unique PIN codes
- **Admin Hierarchy** - Admin users can manage system and other users
- **Usage Tracking** - Last used timestamps and use counts per user
- **Flexible Permissions** - Admin vs regular user roles

### 🎛️ Beautiful Interface
- **Custom Lovelace Card** - Badge-style interface with tap-to-interact
- **Entry Point Controls** - Lock/unlock doors, open/close garage from card
- **Battery Monitoring** - Visual battery levels for wireless sensors
- **Smart Timestamps** - "5m ago" style timestamps for all entry points
- **Mobile Responsive** - Perfect on phones, tablets, and wall panels

## 📸 Screenshots

| Badge View | Arm Options | Disarm Keypad |
|------------|-------------|---------------|
| ![Badge](docs/images/badge.png) | ![Arm](docs/images/arm.png) | ![Disarm](docs/images/disarm.png) |

| Entry Points | Triggered | Config |
|--------------|-----------|--------|
| ![Entry](docs/images/entry-points.png) | ![Trigger](docs/images/triggered.png) | ![Config](docs/images/config.png) |

## 🚀 Quick Start

### Installation

#### Via HACS (Recommended)
1. Open HACS → Integrations
2. Click ⋮ → Custom repositories
3. Add: `https://github.com/mmotrock/ha-secure-alarm`
4. Search "Secure Alarm System" and install
5. Restart Home Assistant
6. Add integration via Settings → Devices & Services

#### Manual Installation
```bash
cd /config
git clone https://github.com/mmotrock/ha-secure-alarm.git
cp -r ha-secure-alarm/custom_components/secure_alarm custom_components/
```
Then restart Home Assistant and add the integration.

### Hardware Setup

**ESP32-POE (Recommended)**
```yaml
# Flash with ESPHome configuration
esphome:
  name: security-panel
  platform: ESP32
  board: esp32-poe

# 6 wired zones included
# Expandable to 128+ zones
```

See [HARDWARE.md](docs/HARDWARE.md) for complete wiring guide.

### Basic Configuration

1. **Add Integration**
   - Settings → Devices & Services → Add Integration
   - Search "Secure Alarm System"
   - Create admin account (6-8 digit PIN)

2. **Register Zones**
   ```yaml
   service: python_script.register_alarm_zone
   data:
     entity_id: binary_sensor.front_door
     zone_type: entry
     enabled_away: true
     enabled_home: false
   ```

3. **Add Users**
   ```yaml
   service: secure_alarm.add_user
   data:
     name: "Family Member"
     pin: "123456"
     admin_pin: "YOUR_ADMIN_PIN"
   ```

4. **Install Lovelace Card**
   ```yaml
   type: custom:secure-alarm-card
   entity: alarm_control_panel.secure_alarm
   entry_points:
     - entity_id: lock.front_door
       name: Front Door
       type: door
       battery_entity: sensor.front_door_battery
   ```

## 📖 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Step-by-step setup instructions
- **[Configuration Guide](docs/CONFIGURATION.md)** - All configuration options
- **[Hardware Guide](docs/HARDWARE.md)** - ESP32 wiring and expansion
- **[API Reference](docs/API.md)** - Services, events, and entities
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🎯 Use Cases

### Home Security
```yaml
# Auto-arm when everyone leaves
automation:
  - alias: "Auto Arm Away"
    trigger:
      - platform: state
        entity_id: group.all_persons
        to: "not_home"
        for: "00:05:00"
    action:
      - service: secure_alarm.arm_away
        data:
          pin: !secret alarm_automation_pin
```

### Bedtime Routine
```yaml
# Arm home and lock up at bedtime
script:
  bedtime:
    sequence:
      - service: secure_alarm.arm_home
        data:
          pin: !secret alarm_automation_pin
      - service: lock.lock
        target:
          entity_id: all
```

### Professional Monitoring
```yaml
# Forward events to monitoring station
secure_alarm:
  monitoring:
    enabled: true
    protocol: contact_id
    endpoint: "monitoring.example.com:5000"
    account_id: "1234"
```

## 🔧 Services

| Service | Description |
|---------|-------------|
| `secure_alarm.arm_away` | Arm all zones with exit delay |
| `secure_alarm.arm_home` | Arm perimeter only (instant) |
| `secure_alarm.disarm` | Disarm with PIN |
| `secure_alarm.add_user` | Add new user (admin only) |
| `secure_alarm.remove_user` | Remove user (admin only) |
| `secure_alarm.bypass_zone` | Temporarily disable zone |
| `secure_alarm.update_config` | Update system settings |

See [API.md](docs/API.md) for complete reference.

## 📊 Entities

### Alarm Control Panel
- `alarm_control_panel.secure_alarm` - Main alarm entity

### Sensors
- `sensor.secure_alarm_status` - Current status
- `sensor.secure_alarm_failed_login_attempts` - Failed PIN count
- `sensor.secure_alarm_last_changed_by` - Last user
- `sensor.secure_alarm_active_zones` - Active zone count

### Binary Sensors
- `binary_sensor.secure_alarm_armed` - Is armed?
- `binary_sensor.secure_alarm_triggered` - Is triggered?
- `binary_sensor.secure_alarm_locked_out` - Is locked out?

## 🎨 Customization

### Custom Delays
```yaml
service: secure_alarm.update_config
data:
  admin_pin: "ADMIN_PIN"
  entry_delay: 45        # seconds
  exit_delay: 90
  lock_delay_home: 0     # instant
  lock_delay_away: 60    # after exit delay
```

### Notifications
```yaml
service: secure_alarm.update_config
data:
  admin_pin: "ADMIN_PIN"
  notification_mobile: true
  notification_sms: true
  sms_numbers: "+15551234567,+15559876543"
```

## 🔒 Security Features

### Duress Code
Create a PIN that silently alerts authorities:
```yaml
service: secure_alarm.add_user
data:
  name: "Duress Code"
  pin: "999999"
  admin_pin: "ADMIN_PIN"
  is_duress: true
```

When used, system appears to disarm normally but sends silent alert.

### Audit Logging
All events stored in SQLite database:
```sql
SELECT * FROM alarm_events ORDER BY timestamp DESC LIMIT 10;
```

### Rate Limiting
- 5 failed attempts = 5 minute lockout
- All attempts logged with timestamps
- Clears on successful authentication

## 🛠️ Hardware Options

### Basic Setup (6 Zones)
- Olimex ESP32-POE: $30
- PoE injector: $15
- 6× door/window sensors: $15
- **Total: ~$60**

### Expanded Setup (12 Zones)
- Add MCP23017 expander: $1
- 6× additional sensors: $15
- **Total: ~$76**

### With Siren
- Add 12V siren: $25
- 12V power supply: $10
- 2× relays: $10
- **Total: ~$45 more**

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

### Development Setup
```bash
git clone https://github.com/mmotrock/ha-secure-alarm.git
cd ha-secure-alarm
pip install -r requirements_dev.txt
```

### Running Tests
```bash
pytest tests/
```

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

### v1.0.0 (2024-01-15)
- Initial release
- 6-12 zone support
- PIN authentication with bcrypt
- Duress codes
- Entry point controls
- Battery monitoring
- Professional monitoring support

## 🐛 Support

- **Issues**: [GitHub Issues](https://github.com/mmotrock/ha-secure-alarm/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mmotrock/ha-secure-alarm/discussions)
- **Community**: [Home Assistant Forum](https://community.home-assistant.io/)

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Home Assistant community for inspiration and support
- ESPHome for excellent firmware framework
- All contributors and testers

## ⚠️ Disclaimer

This integration is designed to enhance home security but should not be your only security measure. For critical security needs, consider professional monitoring services. The authors are not responsible for any security breaches or failures.

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=mmotrock/ha-secure-alarm&type=Date)](https://star-history.com/#mmotrock/ha-secure-alarm&Date)

---

**Made with ❤️ for the Home Assistant community**