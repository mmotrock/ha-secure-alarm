# Secure Alarm System - Documentation

Complete documentation for the Secure Alarm System Home Assistant integration.

## 📚 Documentation Index

### Getting Started
- **[Installation Guide](INSTALLATION.md)** - Step-by-step installation instructions for HACS and manual installation
- **[Hardware Guide](HARDWARE.md)** - ESP32 wiring, sensor setup, and GPIO expansion
- **[Quick Start](#quick-start)** - Get up and running in 10 minutes

### Configuration
- **[Configuration Guide](CONFIGURATION.md)** - All configuration options and settings
- **[API Reference](API.md)** - Services, events, entities, and database schema
- **[Lovelace Card](../www/secure-alarm-card/README.md)** - Custom card installation and configuration

### Support
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions
- **[FAQ](#frequently-asked-questions)** - Quick answers to common questions
- **[Getting Help](#getting-help)** - Where to find additional support

## Quick Start

### 1. Install Integration
```bash
# Via HACS
1. HACS → Integrations → Explore & Download
2. Search "Secure Alarm System"
3. Click Install
4. Restart Home Assistant

# Or Manual
cd /config
git clone https://github.com/mmotrock/ha-secure-alarm.git
cp -r ha-secure-alarm/custom_components/secure_alarm custom_components/
```

### 2. Add Integration
1. Settings → Devices & Services
2. Click "+ Add Integration"
3. Search "Secure Alarm System"
4. Create admin account:
   - Name: Admin
   - PIN: 6-8 digits (e.g., 123456)
   - Confirm PIN

### 3. Setup Hardware (ESP32)
```yaml
# Flash ESPHome configuration
esphome:
  name: security-panel
  platform: ESP32
  board: esp32-poe

# Wire sensors to GPIO pins
GPIO32 → Front Door
GPIO25 → Back Door
GPIO26 → Garage Door
# etc...
```

See [HARDWARE.md](HARDWARE.md) for complete wiring guide.

### 4. Register Zones
```yaml
service: python_script.register_alarm_zone
data:
  entity_id: binary_sensor.front_door
  zone_type: entry
  enabled_away: true
  enabled_home: false
```

### 5. Add Users
```yaml
service: secure_alarm.add_user
data:
  name: "Family Member"
  pin: "654321"
  admin_pin: "123456"
```

### 6. Install Card
```yaml
type: custom:secure-alarm-card
entity: alarm_control_panel.secure_alarm
entry_points:
  - entity_id: lock.front_door
    name: Front Door
    type: door
    battery_entity: sensor.front_door_battery
```

That's it! You now have a fully functional alarm system.

## Documentation Structure

```
docs/
├── README.md                    # This file - documentation index
├── INSTALLATION.md              # Installation instructions
├── CONFIGURATION.md             # Configuration options
├── HARDWARE.md                  # Hardware setup and wiring
├── API.md                       # Services, events, entities
├── TROUBLESHOOTING.md           # Common issues and fixes
└── images/                      # Screenshots and diagrams
    ├── alarm-badge.png
    ├── arm-options.png
    ├── disarm-keypad.png
    └── wiring-diagram.png
```

## Key Concepts

### Security Architecture

**Authentication**
- Separate from Home Assistant users
- 6-8 digit PIN codes
- Bcrypt encryption (never plaintext)
- Rate limiting (5 attempts / 5 minutes)

**Authorization**
- Admin vs regular users
- Admin: Can manage users and config
- Regular: Can arm/disarm only

**Audit Trail**
- All events logged to database
- Includes: user, timestamp, state changes
- Queryable via SQL or Developer Tools

### Alarm States

```
disarmed → arming → armed_away
                  ↘ armed_home
                  
armed_* → pending → triggered
        ↘ disarmed
```

**disarmed**: System off, ready to arm
**arming**: Exit delay countdown (armed_away only)
**armed_home**: Perimeter sensors active
**armed_away**: All sensors active
**pending**: Entry delay countdown
**triggered**: Alarm sounding

### Zone Types

**Entry Zones**
- Front door, back door, garage
- Allow entry delay before triggering
- Used for main access points

**Perimeter Zones**
- Windows, side doors, basement
- Trigger immediately when opened
- No entry delay

**Interior Zones**
- Motion detectors, glass break
- Only active in armed_away mode
- Ignored in armed_home

### User Types

**Admin Users**
- Create/delete other users
- Change system configuration
- Bypass zones
- View audit logs
- Full access

**Regular Users**
- Arm/disarm system
- View current state
- No configuration access

**Duress Codes**
- Special user type
- Appears to disarm normally
- Sends silent alert
- For emergency situations

## Frequently Asked Questions

### General

**Q: Is this a replacement for professional alarm systems?**
A: It's a DIY alternative with professional features. For critical security, consider professional monitoring.

**Q: Can I use wireless sensors?**
A: Yes! Any binary_sensor in Home Assistant works (Zigbee, Z-Wave, WiFi).

**Q: How many zones can I have?**
A: Start with 6 (ESP32 GPIO), expand to 128+ with GPIO expanders. No software limit.

**Q: Does this work with existing alarm sensors?**
A: Yes! Most wired sensors are standard NC (normally closed) contacts.

### Security

**Q: How secure are the PINs?**
A: Bcrypt encrypted with salt, never stored in plaintext. Industry standard security.

**Q: What if someone cuts power?**
A: Add battery backup to ESP32. Integration survives Home Assistant restarts.

**Q: Can PINs be brute-forced?**
A: No. Rate limiting (5 attempts) and lockout (5 minutes) prevent brute force attacks.

**Q: What's a duress code?**
A: A special PIN that appears to work normally but sends a silent alert. For coercion situations.

### Hardware

**Q: What ESP32 board should I use?**
A: Olimex ESP32-POE recommended (built-in Ethernet + PoE). WT32-ETH01 also works.

**Q: Can I use ESP8266?**
A: Yes, but ESP32 recommended for more GPIO pins and better performance.

**Q: Do I need PoE?**
A: No, but recommended. Can use USB power or 5V adapter instead.

**Q: My sensors are NO (Normally Open), will they work?**
A: Yes, but NC (Normally Closed) preferred for security. Set `inverted: false` in ESPHome.

### Configuration

**Q: How do I change entry delay?**
A: Use `secure_alarm.update_config` service with `entry_delay` parameter.

**Q: Can different zones have different delays?**
A: Entry zones use configured delay. Perimeter zones are instant. Interior zones depend on arm mode.

**Q: How do I reset admin PIN?**
A: Delete `/config/secure_alarm.db` and re-add integration. All data will be lost.

**Q: Can I backup the database?**
A: Yes! Include `/config/secure_alarm.db` in your backups.

### Troubleshooting

**Q: Zones not triggering?**
A: Check zone is registered, ESPHome device online, entity IDs match.

**Q: Card not showing?**
A: Verify resource added, clear browser cache, check browser console for errors.

**Q: Integration won't load?**
A: Check logs, verify bcrypt installed, ensure Home Assistant 2024.1+.

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

## Common Tasks

### Add a New Zone
```yaml
service: python_script.register_alarm_zone
data:
  entity_id: binary_sensor.new_window
  zone_type: perimeter
  enabled_away: true
  enabled_home: true
```

### Change Entry Delay
```yaml
service: secure_alarm.update_config
data:
  admin_pin: "ADMIN_PIN"
  entry_delay: 45
```

### Bypass Zone Temporarily
```yaml
service: secure_alarm.bypass_zone
data:
  zone_entity_id: binary_sensor.garage_door
  pin: "YOUR_PIN"
  bypass: true
```

### Enable SMS Notifications
```yaml
service: secure_alarm.update_config
data:
  admin_pin: "ADMIN_PIN"
  notification_sms: true
  sms_numbers: "+15551234567"
```

### View Audit Log
```sql
sqlite3 /config/secure_alarm.db "SELECT * FROM alarm_events ORDER BY timestamp DESC LIMIT 20;"
```

### Create Guest Code (48 hour)
```yaml
service: secure_alarm.add_user
data:
  name: "Weekend Guest"
  pin: "888888"
  admin_pin: "ADMIN_PIN"
  
# Delete after 48 hours with automation
```

## Architecture Overview

```
┌─────────────────────────────────────┐
│     Home Assistant Frontend         │
│  ┌──────────────────────────────┐   │
│  │  Custom Lovelace Card        │   │
│  │  (Badge + Entry Points)      │   │
│  └──────────────────────────────┘   │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│   Secure Alarm Integration          │
│  ┌────────────┐  ┌──────────────┐   │
│  │ Coordinator│  │   Database   │   │
│  │(State      │◄─┤(SQLite)      │   │
│  │ Machine)   │  │- Users       │   │
│  └─────┬──────┘  │- Config      │   │
│        │         │- Events      │   │
│        │         │- Zones       │   │
│  ┌─────▼──────┐  └──────────────┘   │
│  │  Services  │                     │
│  │- arm_away  │                     │
│  │- disarm    │                     │
│  │- add_user  │                     │
│  └────────────┘                     │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│   Hardware Layer                    │
│  ┌────────────┐  ┌──────────────┐   │
│  │ ESPHome    │  │ Z-Wave/      │   │
│  │ (ESP32)    │  │ Zigbee       │   │
│  │- 6 GPIO    │  │- Wireless    │   │
│  │- Siren     │  │  Sensors     │   │
│  └────────────┘  └──────────────┘   │
└─────────────────────────────────────┘
```

## Best Practices

### Security
1. Use strong PINs (avoid 123456, 111111)
2. Limit admin users (only trusted people)
3. Review audit logs regularly
4. Set up duress code
5. Include database in backups

### Reliability
1. Use PoE for stable power
2. Test all sensors monthly
3. Check battery levels weekly
4. Keep Home Assistant updated
5. Monitor ESPHome device uptime

### Usability
1. Entry delay: 30s (enough time to disarm)
2. Exit delay: 60s (enough time to leave)
3. Arm home: No interior sensors
4. Arm away: All sensors
5. Clear zone names

### Automation
1. Auto-arm when leaving
2. Auto-disarm when arriving (optional)
3. Bedtime arm home
4. Morning disarm
5. Vacation mode

## Performance Notes

- **Database size**: ~1MB per 10,000 events
- **Memory usage**: ~50MB typical
- **CPU usage**: <1% idle, <5% during events
- **Network**: Minimal (local only)
- **Response time**: <100ms PIN validation

Clean old events periodically:
```sql
DELETE FROM alarm_events WHERE timestamp < date('now', '-90 days');
VACUUM;
```

## Getting Help

### Documentation
- Read relevant docs in this folder
- Check [Troubleshooting](TROUBLESHOOTING.md) first
- Review [API Reference](API.md) for details

### Community Support
- [GitHub Discussions](https://github.com/mmotrock/ha-secure-alarm/discussions) - Questions and ideas
- [Home Assistant Forum](https://community.home-assistant.io/) - General HA help
- [GitHub Issues](https://github.com/mmotrock/ha-secure-alarm/issues) - Bug reports only

### Before Asking
1. Check documentation
2. Search existing issues/discussions
3. Enable debug logging
4. Gather error messages
5. Try troubleshooting steps

### Reporting Bugs
Include:
- Home Assistant version
- Integration version
- Error messages from logs
- Steps to reproduce
- Expected vs actual behavior

### Feature Requests
- Search existing requests first
- Explain use case clearly
- Describe expected behavior
- Consider submitting PR

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Code style guide
- Development setup
- Testing requirements
- PR process

## License

MIT License - see [LICENSE](../LICENSE)

---

**Need help? Start with [INSTALLATION.md](INSTALLATION.md) or [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**