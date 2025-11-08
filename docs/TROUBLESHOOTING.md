# Troubleshooting Guide

## Common Issues

### Integration Won't Load

**Symptoms:**
- Integration not found in Add Integration menu
- Error in Home Assistant logs

**Solutions:**

1. **Check installation**
   ```bash
   ls /config/custom_components/secure_alarm/
   ```
   Should show: `__init__.py`, `manifest.json`, etc.

2. **Verify dependencies**
   ```bash
   pip install bcrypt==4.0.1
   ```

3. **Check logs**
   ```bash
   tail -f /config/home-assistant.log | grep secure_alarm
   ```

4. **Restart required**
   Settings → System → Restart

5. **Clear cache**
   - Force refresh browser (Ctrl+Shift+R)
   - Clear HA frontend cache
   - Restart Home Assistant

---

### PIN Authentication Fails

**Symptoms:**
- Valid PIN rejected
- All PINs fail
- System locks out immediately

**Solutions:**

1. **Check PIN format**
   - Must be 6-8 digits
   - Numbers only, no letters
   - No leading zeros lost (use quotes in YAML)

2. **Check lockout status**
   ```yaml
   # Developer Tools → States
   binary_sensor.secure_alarm_locked_out
   ```
   If locked, wait 5 minutes or restart HA.

3. **Verify user exists**
   ```sql
   sqlite3 /config/secure_alarm.db "SELECT id, name, enabled FROM alarm_users;"
   ```

4. **Check database permissions**
   ```bash
   ls -la /config/secure_alarm.db
   chmod 644 /config/secure_alarm.db
   ```

5. **Reset admin PIN** (last resort)
   ```bash
   rm /config/secure_alarm.db
   # Re-add integration, create new admin
   ```

---

### Zones Not Triggering

**Symptoms:**
- Sensor opens but alarm doesn't respond
- Some zones work, others don't
- Inconsistent triggering

**Solutions:**

1. **Verify zone registration**
   ```yaml
   service: python_script.register_alarm_zone
   data:
     entity_id: binary_sensor.front_door
     zone_type: entry
     enabled_away: true
     enabled_home: true
   ```

2. **Check sensor state**
   - Developer Tools → States
   - Find sensor entity
   - Verify state changes when opened/closed

3. **Check ESPHome device**
   - ESPHome → Devices → Security Panel
   - Check "Online" status
   - View logs for sensor events

4. **Verify entity ID matches**
   ```sql
   sqlite3 /config/secure_alarm.db "SELECT entity_id, zone_name FROM alarm_zones;"
   ```

5. **Check zone bypass status**
   ```yaml
   # Unbypass all zones
   service: secure_alarm.bypass_zone
   data:
     zone_entity_id: binary_sensor.front_door
     pin: "YOUR_PIN"
     bypass: false
   ```

---

### Entry/Exit Delays Not Working

**Symptoms:**
- Alarm triggers immediately
- No countdown displayed
- Delays seem random

**Solutions:**

1. **Check delay configuration**
   ```yaml
   # Check current settings
   # Developer Tools → States → alarm_control_panel.secure_alarm
   # View attributes
   ```

2. **Update delays**
   ```yaml
   service: secure_alarm.update_config
   data:
     admin_pin: "YOUR_ADMIN_PIN"
     entry_delay: 30
     exit_delay: 60
   ```

3. **Verify zone type**
   - Only ENTRY zones use entry delay
   - PERIMETER zones trigger instantly
   - Check zone_type in database

4. **Check state transitions**
   - Armed Away → (open entry door) → Pending state
   - If goes straight to Triggered, zone type is wrong

---

### Lovelace Card Not Displaying

**Symptoms:**
- Card shows error or blank
- JavaScript console errors
- Card not in card picker

**Solutions:**

1. **Verify resource added**
   - Settings → Dashboards → Resources
   - Should see `/local/secure-alarm-card.js`
   - Type: JavaScript Module

2. **Check file location**
   ```bash
   ls -la /config/www/secure-alarm-card.js
   ```

3. **Clear browser cache**
   - Hard refresh: Ctrl+Shift+R (Win) or Cmd+Shift+R (Mac)
   - Or use incognito mode

4. **Check browser console**
   - F12 → Console tab
   - Look for JavaScript errors
   - Common: "customElements.define" errors

5. **Verify card config**
   ```yaml
   type: custom:secure-alarm-card
   entity: alarm_control_panel.secure_alarm
   ```

6. **Test with simple card first**
   ```yaml
   type: entities
   entities:
     - alarm_control_panel.secure_alarm
   ```

---

### Entry Points Not Toggling

**Symptoms:**
- Clicking entry point does nothing
- State doesn't update
- No error messages

**Solutions:**

1. **Check entity availability**
   - Developer Tools → States
   - Verify lock/cover entities exist
   - Check they're not "unavailable"

2. **Test entity directly**
   ```yaml
   service: lock.lock
   target:
     entity_id: lock.front_door
   ```

3. **Verify entity_id in card config**
   ```yaml
   entry_points:
     - entity_id: lock.front_door  # Must match exactly
       name: Front Door
       type: door
   ```

4. **Check permissions**
   - Some entities require authentication
   - Test from Developer Tools first

---

### Notifications Not Received

**Symptoms:**
- No mobile notifications
- SMS not sending
- Some events notify, others don't

**Solutions:**

1. **Mobile App Notifications**
   
   a. **Verify app installed**
      - Home Assistant Companion app
      - Logged in to correct instance
   
   b. **Check notification settings**
      - App → Settings → Notifications
      - Allow notifications enabled
      - Not in Do Not Disturb
   
   c. **Test notification**
      ```yaml
      service: notify.mobile_app_YOUR_PHONE
      data:
        title: "Test"
        message: "This is a test"
      ```

2. **SMS Notifications**
   
   a. **Verify Twilio configured**
      ```yaml
      # configuration.yaml
      notify:
        - platform: twilio_sms
          name: sms
          # Check credentials
      ```
   
   b. **Enable in alarm config**
      ```yaml
      service: secure_alarm.update_config
      data:
        admin_pin: "ADMIN_PIN"
        notification_sms: true
        sms_numbers: "+15551234567"
      ```
   
   c. **Check Twilio console**
      - Login to twilio.com
      - Check message logs
      - Verify phone number format

3. **Event-specific issues**
   - Check event is actually firing
   - Developer Tools → Events → Listen for event
   - Event type: `secure_alarm_triggered`

---

### Database Errors

**Symptoms:**
- "Database locked" errors
- Slow responses
- Data not saving

**Solutions:**

1. **Check database file**
   ```bash
   ls -la /config/secure_alarm.db
   file /config/secure_alarm.db
   ```

2. **Test database integrity**
   ```bash
   sqlite3 /config/secure_alarm.db "PRAGMA integrity_check;"
   ```

3. **Backup and recreate**
   ```bash
   cp /config/secure_alarm.db /config/secure_alarm.db.backup
   sqlite3 /config/secure_alarm.db "VACUUM;"
   ```

4. **Check disk space**
   ```bash
   df -h /config
   ```

---

### ESPHome Device Offline

**Symptoms:**
- "Unavailable" in Home Assistant
- Sensors show "Unknown"
- Device not in ESPHome dashboard

**Solutions:**

1. **Check network**
   - Ping ESP32 IP address
   - Verify PoE power (check LED)
   - Check Ethernet cable

2. **View ESPHome logs**
   - ESPHome dashboard → Device → Logs
   - Look for connection errors
   - Check API key matches

3. **Verify API key**
   ```yaml
   # esphome/security-panel.yaml
   api:
     encryption:
       key: "YOUR_KEY_HERE"
   ```
   Must match Home Assistant integration.

4. **Reboot device**
   - Power cycle PoE
   - Or: ESPHome dashboard → Device → Restart

5. **Re-adopt device**
   - ESPHome → Device → Adopt
   - Enter API key
   - Update configuration

---

### Automation Not Working

**Symptoms:**
- Alarm doesn't auto-arm/disarm
- Trigger doesn't execute actions
- Works manually but not automatically

**Solutions:**

1. **Check automation enabled**
   - Settings → Automations
   - Ensure toggle is ON

2. **Test trigger**
   - Automation → ⋮ → Information
   - Check "Last Triggered"
   - View trace if available

3. **Verify conditions**
   ```yaml
   # Common issue: wrong state name
   condition:
     - condition: state
       entity_id: alarm_control_panel.secure_alarm
       state: "disarmed"  # Must match exactly
   ```

4. **Check service call**
   - Developer Tools → Services
   - Test service manually
   - Verify PIN is correct

5. **View automation traces**
   - Automation → ⋮ → Traces
   - See where it fails
   - Check condition results

---

### High CPU/Memory Usage

**Symptoms:**
- Home Assistant slow
- Integration lagging
- System unresponsive

**Solutions:**

1. **Check database size**
   ```bash
   du -h /config/secure_alarm.db
   ```
   If >100MB, clean old events.

2. **Clean old events**
   ```sql
   sqlite3 /config/secure_alarm.db "DELETE FROM alarm_events WHERE timestamp < date('now', '-90 days');"
   sqlite3 /config/secure_alarm.db "VACUUM;"
   ```

3. **Reduce logging**
   ```yaml
   # configuration.yaml
   logger:
     default: warning
     logs:
       custom_components.secure_alarm: info
   ```

4. **Check for loops**
   - Automation triggering itself
   - Rapid state changes
   - Review automation traces

---

### Professional Monitoring Not Connecting

**Symptoms:**
- Events not reaching monitoring station
- Connection errors in logs
- No heartbeat confirmation

**Solutions:**

1. **Test connection**
   ```yaml
   service: secure_alarm.update_config
   data:
     admin_pin: "ADMIN_PIN"
   # Then check logs for connection attempt
   ```

2. **Verify endpoint**
   - Correct IP/hostname
   - Correct port
   - Firewall allows outbound

3. **Check protocol**
   ```yaml
   # configuration.yaml
   secure_alarm:
     monitoring:
       protocol: contact_id  # Must match monitoring station
       endpoint: "correct.address.here:5000"
   ```

4. **Test mode**
   Enable test mode to see raw messages:
   ```yaml
   secure_alarm:
     monitoring:
       test_mode: true
   ```

5. **Contact monitoring company**
   - Verify account ID
   - Check protocol compatibility
   - Request test event

---

## Diagnostic Commands

### System Status Check
```bash
# Check HA is running
systemctl status home-assistant@homeassistant

# Check integration loaded
grep "secure_alarm" /config/home-assistant.log | tail -20

# Check database
sqlite3 /config/secure_alarm.db "SELECT name FROM sqlite_master WHERE type='table';"

# Check ESPHome device
ping -c 3 192.168.1.XXX
```

### Full System Test
```yaml
# 1. Test authentication
service: secure_alarm.arm_away
data:
  pin: "YOUR_PIN"

# 2. Wait for arming

# 3. Trigger zone (open door)

# 4. Verify pending state

# 5. Disarm
service: secure_alarm.disarm
data:
  pin: "YOUR_PIN"

# 6. Check logs
# 7. Check audit trail
```

---

## Getting Help

If issues persist:

1. **Gather information**
   - Home Assistant version
   - Integration version
   - Relevant log entries
   - Configuration (sanitized)

2. **Check existing issues**
   - GitHub Issues
   - Home Assistant Community Forum
   - Search for similar problems

3. **Create new issue**
   - GitHub: Include diagnostics
   - Forum: Describe steps taken
   - Provide error messages

4. **Enable debug logging**
   ```yaml
   # configuration.yaml
   logger:
     default: warning
     logs:
       custom_components.secure_alarm: debug
   ```
   Then collect logs and share.

---

## Known Issues

### Issue: Bypass doesn't persist through restart
**Workaround:** Bypass zones again after restart

### Issue: Very long PINs (>8 digits) accepted in some scenarios
**Workaround:** Validate PIN length in automations

### Issue: SMS not working with some providers
**Workaround:** Use alternative SMS integration (Vonage, MessageBird)

Check GitHub Issues for latest known issues and workarounds.