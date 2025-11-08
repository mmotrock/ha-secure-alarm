# Installation Guide

## Prerequisites

- Home Assistant 2024.1.0 or newer
- HACS installed (recommended) or manual installation capability
- ESP32 device with PoE support (Olimex ESP32-POE or WT32-ETH01)
- PoE+ switch or injector
- Wired door/window sensors

## Method 1: HACS Installation (Recommended)

1. **Open HACS**
   - Navigate to HACS in Home Assistant
   - Click on "Integrations"

2. **Add Custom Repository** (if not in default HACS)
   - Click the three dots menu (⋮)
   - Select "Custom repositories"
   - Add repository URL: `https://github.com/mmotrock/ha-secure-alarm`
   - Category: Integration
   - Click "Add"

3. **Install Integration**
   - Search for "Secure Alarm System"
   - Click "Download"
   - Restart Home Assistant

4. **Add Integration**
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "Secure Alarm System"
   - Follow setup wizard

## Method 2: Manual Installation

1. **Download Files**
   ```bash
   cd /config
   wget https://github.com/mmotrock/ha-secure-alarm/releases/latest/download/secure_alarm.zip
   unzip secure_alarm.zip
   ```

2. **Copy Integration**
   ```bash
   cp -r secure_alarm/custom_components/secure_alarm /config/custom_components/
   ```

3. **Restart Home Assistant**

4. **Add Integration**
   - Settings → Devices & Services → Add Integration
   - Search "Secure Alarm System"

## Hardware Setup

### ESP32-POE Configuration

1. **Install ESPHome**
   - Settings → Add-ons → Add-on Store
   - Install "ESPHome"
   - Start and enable "Start on boot"

2. **Create Device**
   - Open ESPHome dashboard
   - Click "+ New Device"
   - Name: "Security Panel"
   - Copy provided `security-panel.yaml` configuration

3. **Configure Secrets**
   ```bash
   cp esphome/secrets.yaml.example config/esphome/secrets.yaml
   nano config/esphome/secrets.yaml
   ```
   
   Generate API key:
   ```bash
   openssl rand -base64 32
   ```

4. **Flash Device**
   - First time: Connect via USB
   - Click "Install" → "Plug into this computer"
   - After initial flash, use OTA updates

### Sensor Wiring

Connect sensors to GPIO pins as specified in ESPHome config:

**Direct GPIO (ESP32):**
- GPIO32: Zone 1 (Front Door)
- GPIO25: Zone 2 (Back Door)
- GPIO26: Zone 3 (Garage Door)
- GPIO27: Zone 4 (Living Room Window)
- GPIO14: Zone 5 (Bedroom Window)
- GPIO13: Zone 6 (Kitchen Window)

**Wiring Instructions:**
- NC (Normally Closed) sensors: Connect one wire to GPIO, other to GND
- NO (Normally Open) sensors: Set `inverted: false` in ESPHome config
- Use 22AWG wire for sensor connections
- Keep wire runs under 100ft to prevent voltage drop

### Siren/Strobe (Optional)

- GPIO15: Siren output (12V relay)
- GPIO4: Strobe output (12V relay)

Use solid-state relays rated for your siren/strobe voltage.

## Initial Configuration

### 1. Create Admin Account

During first setup:
- Enter administrator name
- Create 6-8 digit PIN
- Confirm PIN
- Click "Submit"

### 2. Configure Zones

**Option A: Using Blueprint**
1. Settings → Automations & Scenes → Blueprints
2. Import zone configuration blueprint
3. Create automation from blueprint
4. Map sensor entities to zones
5. Set zone types (entry/perimeter/interior)
6. Enable/disable for home/away modes

**Option B: Manual Registration**
```yaml
service: python_script.register_alarm_zone
data:
  entity_id: binary_sensor.front_door
  zone_type: entry
  enabled_away: true
  enabled_home: false
```

### 3. Add Users

```yaml
service: secure_alarm.add_user
data:
  name: "Family Member"
  pin: "654321"
  admin_pin: "YOUR_ADMIN_PIN"
  is_admin: false
  is_duress: false
```

### 4. Install Lovelace Card

1. **Copy Card File**
   ```bash
   mkdir -p /config/www
   cp www/secure-alarm-card.js /config/www/
   ```

2. **Add Resource**
   - Settings → Dashboards → Resources
   - Click "+ Add Resource"
   - URL: `/local/secure-alarm-card.js`
   - Type: JavaScript Module

3. **Add Card**
   ```yaml
   type: custom:secure-alarm-card
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

## Optional Features

### SMS Notifications

1. **Install Twilio Integration**
   ```yaml
   # configuration.yaml
   notify:
     - platform: twilio_sms
       name: sms
       account_sid: !secret twilio_account_sid
       auth_token: !secret twilio_auth_token
       from_number: !secret twilio_from_number
   ```

2. **Enable in Alarm Config**
   ```yaml
   service: secure_alarm.update_config
   data:
     admin_pin: "YOUR_ADMIN_PIN"
     notification_sms: true
     sms_numbers: "+15551234567,+15559876543"
   ```

### Professional Monitoring

```yaml
# configuration.yaml
secure_alarm:
  monitoring:
    enabled: true
    protocol: contact_id
    endpoint: "monitoring.example.com:5000"
    account_id: "1234"
    api_key: "your-api-key"
```

## Verification

### Test Checklist

- [ ] Integration loads without errors
- [ ] Admin account created successfully
- [ ] All zones registered and visible
- [ ] Entry delay works correctly
- [ ] Exit delay works correctly
- [ ] Doors lock when arming
- [ ] Garage closes when arming
- [ ] Mobile notifications received
- [ ] Failed PIN attempts trigger lockout
- [ ] Audit log records events
- [ ] Lovelace card displays correctly
- [ ] Entry points toggle correctly

### Test Duress Code

```yaml
service: secure_alarm.add_user
data:
  name: "Duress Code"
  pin: "999999"
  admin_pin: "YOUR_ADMIN_PIN"
  is_duress: true
```

Test by using duress PIN to disarm - should disarm but send silent alert.

## Troubleshooting

### Integration Won't Load

Check logs:
```bash
tail -f /config/home-assistant.log | grep secure_alarm
```

Common issues:
- Missing bcrypt dependency: `pip install bcrypt==4.0.1`
- Database permissions: `chmod 644 /config/secure_alarm.db`
- Syntax errors in configuration

### Zones Not Triggering

1. Check ESPHome device is online
2. Verify GPIO pin assignments match physical wiring
3. Test sensor with multimeter (should be closed circuit)
4. Check entity IDs match in zone configuration

### Card Not Displaying

1. Verify resource is added to Lovelace
2. Clear browser cache
3. Check browser console for JavaScript errors
4. Ensure card file is in `/config/www/`

### Can't Add Users

- Verify admin PIN is correct
- Check for lockout status
- Ensure PIN is 6-8 digits numeric only

## Backup

Include these files in backups:
- `/config/custom_components/secure_alarm/`
- `/config/secure_alarm.db`
- `/config/esphome/security-panel.yaml`
- `/config/esphome/secrets.yaml`

## Support

- GitHub Issues: Report bugs and request features
- Home Assistant Community: Ask questions in forum
- Documentation: Read full docs in `/docs/`