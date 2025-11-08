# Secure Alarm System

[![GitHub Release](https://img.shields.io/github/release/mmotrock/ha-secure-alarm.svg?style=for-the-badge)](https://github.com/mmotrock/ha-secure-alarm/releases)
[![License](https://img.shields.io/github/license/mmotrock/ha-secure-alarm.svg?style=for-the-badge)](LICENSE)
[![hacs](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

Professional-grade security system integration for Home Assistant with dedicated authentication, comprehensive audit logging, and support for wired sensors via ESP32.

## ✨ Key Features

### 🔐 Security First
- **Dedicated PIN Authentication** - 6-8 digit PINs completely separate from Home Assistant users
- **Bcrypt Encryption** - Industry-standard password hashing, never stores plaintext
- **Duress Codes** - Silent alert codes that appear to disarm but notify authorities
- **Rate Limiting** - Automatic lockout after 5 failed attempts (5 minute cooldown)
- **Comprehensive Audit Trail** - Every action logged with timestamps and user identification

### 🚨 Advanced Alarm Features
- **Multiple Arm Modes** - Away (all zones), Home (perimeter only)
- **Configurable Delays** - Entry delay (30s default), Exit delay (60s default)
- **Zone Types** - Entry zones (with delay), Perimeter (instant), Interior
- **6+ Physical Zones** - Easily expandable for additional sensors
- **Auto-Lock & Close** - Automatically secures doors and garage on arming
- **Zone Bypass** - Temporarily disable specific sensors with PIN authorization

### 📱 Smart Notifications
- **Mobile Push Notifications** - Via Home Assistant companion app
- **SMS Alerts** - Configurable phone numbers (requires Twilio/SMS integration)
- **Event Types** - Armed/disarmed, triggers, duress codes, failed attempts
- **Real-time Updates** - Instant notifications on all alarm events

### 👥 User Management
- **Multiple Users** - Each with unique PIN codes
- **Admin Controls** - Separate admin PINs for configuration changes
- **User Permissions** - Admin vs regular user privileges
- **Usage Tracking** - Last used timestamps and usage counts

### 🎛️ Easy Management
- **Beautiful UI** - Custom Lovelace card with badge-style interface
- **Quick Controls** - Lock/unlock doors, open/close garage from alarm card
- **Battery Monitoring** - Track battery levels for wireless sensors
- **Last Changed Timestamps** - See when each door/lock was last used
- **Service Calls** - Full automation support for advanced users

## 🔧 Hardware Support

### Recommended Setup
- **Olimex ESP32-POE** or **WT32-ETH01** (ESP32 with Ethernet)
- PoE+ switch or injector for power
- Wired door/window sensors (Normally Closed recommended)
- Optional: 12V siren and strobe light

### Alternative Hardware
- **Konnected Alarm Panel Pro** - Ready-made solution with PoE
- Any ESP32/ESP8266 board with appropriate GPIO pins
- Wireless sensors (Zigbee, Z-Wave) - coming soon

## 📦 What's Included

- **Custom Integration** - Complete Home Assistant integration
- **ESPHome Configuration** - Pre-configured for ESP32-POE with 6 zones
- **Database Management** - SQLite database for secure storage
- **Custom Lovelace Card** - Beautiful badge-style alarm interface
- **Automation Blueprints** - Easy zone configuration
- **Python Scripts** - Zone registration helpers
- **Complete Documentation** - Installation, configuration, and troubleshooting guides

## 🚀 Quick Start

1. **Install via HACS** (recommended)
   - Open HACS → Integrations
   - Click "Explore & Download Repositories"
   - Search for "Secure Alarm System"
   - Click "Download"
   - Restart Home Assistant

2. **Add Integration**
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Secure Alarm System"
   - Follow setup wizard to create admin account

3. **Configure Hardware**
   - Install ESPHome integration if not already installed
   - Flash ESP32 device with provided configuration
   - Connect wired sensors to GPIO pins

4. **Add Users**
   - Use `secure_alarm.add_user` service to add family members
   - Set up duress codes for emergency situations

5. **Install Custom Card**
   - Copy card files to `/config/www/`
   - Add to Lovelace dashboard

See [full installation guide](https://github.com/mmotrock/ha-secure-alarm/blob/main/README.md) for detailed instructions.

## 📊 Entities Created

- **Alarm Control Panel**: `alarm_control_panel.secure_alarm`
- **Sensors**:
  - `sensor.secure_alarm_status` - Current status
  - `sensor.secure_alarm_failed_login_attempts` - Failed PIN attempts
  - `sensor.secure_alarm_last_changed_by` - Last user who changed state
  - `sensor.secure_alarm_active_zones` - Active zone count
- **Binary Sensors**:
  - `binary_sensor.secure_alarm_armed` - Is system armed?
  - `binary_sensor.secure_alarm_triggered` - Is alarm triggered?
  - `binary_sensor.secure_alarm_locked_out` - Is system locked out?

## 🛠️ Configuration Example

```yaml
# Add users via service call
service: secure_alarm.add_user
data:
  name: "John Doe"
  pin: "123456"
  admin_pin: "000000"  # Your admin PIN
  is_admin: false

# Configure timing
service: secure_alarm.update_config
data:
  admin_pin: "000000"
  entry_delay: 30
  exit_delay: 60
  alarm_duration: 300
  lock_delay_home: 0
  lock_delay_away: 60
```

## 🔔 Notification Setup

### Mobile Notifications (Built-in)
Works automatically with Home Assistant companion app.

### SMS Notifications (Optional)
Requires Twilio or similar SMS integration:

```yaml
# configuration.yaml
notify:
  - platform: twilio_sms
    name: sms
    from_number: !secret twilio_from

# Enable in alarm config
service: secure_alarm.update_config
data:
  admin_pin: "000000"
  notification_sms: true
  sms_numbers: "+15551234567,+15559876543"
```

## 🎨 Custom Lovelace Card

Add the beautiful badge-style alarm card to any dashboard:

```yaml
type: custom:secure-alarm-badge
entity: alarm_control_panel.secure_alarm
entry_points:
  - entity_id: lock.front_door
    name: Front Door
    type: door
    battery_entity: sensor.front_door_battery
  - entity_id: cover.garage_door
    name: Garage Door
    type: garage
```

## 🔒 Security Best Practices

1. **Use Strong PINs** - Avoid sequential (123456) or repeated digits (111111)
2. **Limit Admin Access** - Only trusted individuals should have admin privileges
3. **Review Audit Logs** - Check logs periodically for suspicious activity
4. **Set Up Duress Code** - Create at least one duress code for emergencies
5. **Backup Database** - Include `secure_alarm.db` in your backup routine
6. **Use HTTPS** - Always use HTTPS for remote access to Home Assistant

## 📚 Documentation

- [Installation Guide](https://github.com/mmotrock/ha-secure-alarm/blob/main/docs/INSTALLATION.md)
- [Configuration Guide](https://github.com/mmotrock/ha-secure-alarm/blob/main/docs/CONFIGURATION.md)
- [Hardware Setup](https://github.com/mmotrock/ha-secure-alarm/blob/main/docs/HARDWARE.md)
- [API Reference](https://github.com/mmotrock/ha-secure-alarm/blob/main/docs/API.md)
- [Troubleshooting](https://github.com/mmotrock/ha-secure-alarm/blob/main/docs/TROUBLESHOOTING.md)

## 🐛 Support

- **Issues**: [GitHub Issues](https://github.com/mmotrock/ha-secure-alarm/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mmotrock/ha-secure-alarm/discussions)
- **Community Forum**: [Home Assistant Community](https://community.home-assistant.io/)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](https://github.com/mmotrock/ha-secure-alarm/blob/main/CONTRIBUTING.md) first.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/mmotrock/ha-secure-alarm/blob/main/LICENSE) file for details.

## 🙏 Credits

Developed for the Home Assistant community. Special thanks to all contributors and testers.

---

**Note**: This is a security system integration. While it provides robust features, it should not be your only security measure. Consider professional monitoring for critical security needs.