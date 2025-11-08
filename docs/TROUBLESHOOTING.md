\# Troubleshooting Guide



\## Common Issues



\### Integration Won't Load



\*\*Symptoms:\*\*

\- Integration not found in Add Integration menu

\- Error in Home Assistant logs



\*\*Solutions:\*\*



1\. \*\*Check installation\*\*

&nbsp;  ```bash

&nbsp;  ls /config/custom\_components/secure\_alarm/

&nbsp;  ```

&nbsp;  Should show: `\_\_init\_\_.py`, `manifest.json`, etc.



2\. \*\*Verify dependencies\*\*

&nbsp;  ```bash

&nbsp;  pip install bcrypt==4.0.1

&nbsp;  ```



3\. \*\*Check logs\*\*

&nbsp;  ```bash

&nbsp;  tail -f /config/home-assistant.log | grep secure\_alarm

&nbsp;  ```



4\. \*\*Restart required\*\*

&nbsp;  Settings → System → Restart



5\. \*\*Clear cache\*\*

&nbsp;  - Force refresh browser (Ctrl+Shift+R)

&nbsp;  - Clear HA frontend cache

&nbsp;  - Restart Home Assistant



---



\### PIN Authentication Fails



\*\*Symptoms:\*\*

\- Valid PIN rejected

\- All PINs fail

\- System locks out immediately



\*\*Solutions:\*\*



1\. \*\*Check PIN format\*\*

&nbsp;  - Must be 6-8 digits

&nbsp;  - Numbers only, no letters

&nbsp;  - No leading zeros lost (use quotes in YAML)



2\. \*\*Check lockout status\*\*

&nbsp;  ```yaml

&nbsp;  # Developer Tools → States

&nbsp;  binary\_sensor.secure\_alarm\_locked\_out

&nbsp;  ```

&nbsp;  If locked, wait 5 minutes or restart HA.



3\. \*\*Verify user exists\*\*

&nbsp;  ```sql

&nbsp;  sqlite3 /config/secure\_alarm.db "SELECT id, name, enabled FROM alarm\_users;"

&nbsp;  ```



4\. \*\*Check database permissions\*\*

&nbsp;  ```bash

&nbsp;  ls -la /config/secure\_alarm.db

&nbsp;  chmod 644 /config/secure\_alarm.db

&nbsp;  ```



5\. \*\*Reset admin PIN\*\* (last resort)

&nbsp;  ```bash

&nbsp;  rm /config/secure\_alarm.db

&nbsp;  # Re-add integration, create new admin

&nbsp;  ```



---



\### Zones Not Triggering



\*\*Symptoms:\*\*

\- Sensor opens but alarm doesn't respond

\- Some zones work, others don't

\- Inconsistent triggering



\*\*Solutions:\*\*



1\. \*\*Verify zone registration\*\*

&nbsp;  ```yaml

&nbsp;  service: python\_script.register\_alarm\_zone

&nbsp;  data:

&nbsp;    entity\_id: binary\_sensor.front\_door

&nbsp;    zone\_type: entry

&nbsp;    enabled\_away: true

&nbsp;    enabled\_home: true

&nbsp;  ```



2\. \*\*Check sensor state\*\*

&nbsp;  - Developer Tools → States

&nbsp;  - Find sensor entity

&nbsp;  - Verify state changes when opened/closed



3\. \*\*Check ESPHome device\*\*

&nbsp;  - ESPHome → Devices → Security Panel

&nbsp;  - Check "Online" status

&nbsp;  - View logs for sensor events



4\. \*\*Verify entity ID matches\*\*

&nbsp;  ```sql

&nbsp;  sqlite3 /config/secure\_alarm.db "SELECT entity\_id, zone\_name FROM alarm\_zones;"

&nbsp;  ```



5\. \*\*Check zone bypass status\*\*

&nbsp;  ```yaml

&nbsp;  # Unbypass all zones

&nbsp;  service: secure\_alarm.bypass\_zone

&nbsp;  data:

&nbsp;    zone\_entity\_id: binary\_sensor.front\_door

&nbsp;    pin: "YOUR\_PIN"

&nbsp;    bypass: false

&nbsp;  ```



---



\### Entry/Exit Delays Not Working



\*\*Symptoms:\*\*

\- Alarm triggers immediately

\- No countdown displayed

\- Delays seem random



\*\*Solutions:\*\*



1\. \*\*Check delay configuration\*\*

&nbsp;  ```yaml

&nbsp;  # Check current settings

&nbsp;  # Developer Tools → States → alarm\_control\_panel.secure\_alarm

&nbsp;  # View attributes

&nbsp;  ```



2\. \*\*Update delays\*\*

&nbsp;  ```yaml

&nbsp;  service: secure\_alarm.update\_config

&nbsp;  data:

&nbsp;    admin\_pin: "YOUR\_ADMIN\_PIN"

&nbsp;    entry\_delay: 30

&nbsp;    exit\_delay: 60

&nbsp;  ```



3\. \*\*Verify zone type\*\*

&nbsp;  - Only ENTRY zones use entry delay

&nbsp;  - PERIMETER zones trigger instantly

&nbsp;  - Check zone\_type in database



4\. \*\*Check state transitions\*\*

&nbsp;  - Armed Away → (open entry door) → Pending state

&nbsp;  - If goes straight to Triggered, zone type is wrong



---



\### Lovelace Card Not Displaying



\*\*Symptoms:\*\*

\- Card shows error or blank

\- JavaScript console errors

\- Card not in card picker



\*\*Solutions:\*\*



1\. \*\*Verify resource added\*\*

&nbsp;  - Settings → Dashboards → Resources

&nbsp;  - Should see `/local/secure-alarm-card.js`

&nbsp;  - Type: JavaScript Module



2\. \*\*Check file location\*\*

&nbsp;  ```bash

&nbsp;  ls -la /config/www/secure-alarm-card.js

&nbsp;  ```



3\. \*\*Clear browser cache\*\*

&nbsp;  - Hard refresh: Ctrl+Shift+R (Win) or Cmd+Shift+R (Mac)

&nbsp;  - Or use incognito mode



4\. \*\*Check browser console\*\*

&nbsp;  - F12 → Console tab

&nbsp;  - Look for JavaScript errors

&nbsp;  - Common: "customElements.define" errors



5\. \*\*Verify card config\*\*

&nbsp;  ```yaml

&nbsp;  type: custom:secure-alarm-card

&nbsp;  entity: alarm\_control\_panel.secure\_alarm

&nbsp;  ```



6\. \*\*Test with simple card first\*\*

&nbsp;  ```yaml

&nbsp;  type: entities

&nbsp;  entities:

&nbsp;    - alarm\_control\_panel.secure\_alarm

&nbsp;  ```



---



\### Entry Points Not Toggling



\*\*Symptoms:\*\*

\- Clicking entry point does nothing

\- State doesn't update

\- No error messages



\*\*Solutions:\*\*



1\. \*\*Check entity availability\*\*

&nbsp;  - Developer Tools → States

&nbsp;  - Verify lock/cover entities exist

&nbsp;  - Check they're not "unavailable"



2\. \*\*Test entity directly\*\*

&nbsp;  ```yaml

&nbsp;  service: lock.lock

&nbsp;  target:

&nbsp;    entity\_id: lock.front\_door

&nbsp;  ```



3\. \*\*Verify entity\_id in card config\*\*

&nbsp;  ```yaml

&nbsp;  entry\_points:

&nbsp;    - entity\_id: lock.front\_door  # Must match exactly

&nbsp;      name: Front Door

&nbsp;      type: door

&nbsp;  ```



4\. \*\*Check permissions\*\*

&nbsp;  - Some entities require authentication

&nbsp;  - Test from Developer Tools first



---



\### Notifications Not Received



\*\*Symptoms:\*\*

\- No mobile notifications

\- SMS not sending

\- Some events notify, others don't



\*\*Solutions:\*\*



1\. \*\*Mobile App Notifications\*\*

&nbsp;  

&nbsp;  a. \*\*Verify app installed\*\*

&nbsp;     - Home Assistant Companion app

&nbsp;     - Logged in to correct instance

&nbsp;  

&nbsp;  b. \*\*Check notification settings\*\*

&nbsp;     - App → Settings → Notifications

&nbsp;     - Allow notifications enabled

&nbsp;     - Not in Do Not Disturb

&nbsp;  

&nbsp;  c. \*\*Test notification\*\*

&nbsp;     ```yaml

&nbsp;     service: notify.mobile\_app\_YOUR\_PHONE

&nbsp;     data:

&nbsp;       title: "Test"

&nbsp;       message: "This is a test"

&nbsp;     ```



2\. \*\*SMS Notifications\*\*

&nbsp;  

&nbsp;  a. \*\*Verify Twilio configured\*\*

&nbsp;     ```yaml

&nbsp;     # configuration.yaml

&nbsp;     notify:

&nbsp;       - platform: twilio\_sms

&nbsp;         name: sms

&nbsp;         # Check credentials

&nbsp;     ```

&nbsp;  

&nbsp;  b. \*\*Enable in alarm config\*\*

&nbsp;     ```yaml

&nbsp;     service: secure\_alarm.update\_config

&nbsp;     data:

&nbsp;       admin\_pin: "ADMIN\_PIN"

&nbsp;       notification\_sms: true

&nbsp;       sms\_numbers: "+15551234567"

&nbsp;     ```

&nbsp;  

&nbsp;  c. \*\*Check Twilio console\*\*

&nbsp;     - Login to twilio.com

&nbsp;     - Check message logs

&nbsp;     - Verify phone number format



3\. \*\*Event-specific issues\*\*

&nbsp;  - Check event is actually firing

&nbsp;  - Developer Tools → Events → Listen for event

&nbsp;  - Event type: `secure\_alarm\_triggered`



---



\### Database Errors



\*\*Symptoms:\*\*

\- "Database locked" errors

\- Slow responses

\- Data not saving



\*\*Solutions:\*\*



1\. \*\*Check database file\*\*

&nbsp;  ```bash

&nbsp;  ls -la /config/secure\_alarm.db

&nbsp;  file /config/secure\_alarm.db

&nbsp;  ```



2\. \*\*Test database integrity\*\*

&nbsp;  ```bash

&nbsp;  sqlite3 /config/secure\_alarm.db "PRAGMA integrity\_check;"

&nbsp;  ```



3\. \*\*Backup and recreate\*\*

&nbsp;  ```bash

&nbsp;  cp /config/secure\_alarm.db /config/secure\_alarm.db.backup

&nbsp;  sqlite3 /config/secure\_alarm.db "VACUUM;"

&nbsp;  ```



4\. \*\*Check disk space\*\*

&nbsp;  ```bash

&nbsp;  df -h /config

&nbsp;  ```



---



\### ESPHome Device Offline



\*\*Symptoms:\*\*

\- "Unavailable" in Home Assistant

\- Sensors show "Unknown"

\- Device not in ESPHome dashboard



\*\*Solutions:\*\*



1\. \*\*Check network\*\*

&nbsp;  - Ping ESP32 IP address

&nbsp;  - Verify PoE power (check LED)

&nbsp;  - Check Ethernet cable



2\. \*\*View ESPHome logs\*\*

&nbsp;  - ESPHome dashboard → Device → Logs

&nbsp;  - Look for connection errors

&nbsp;  - Check API key matches



3\. \*\*Verify API key\*\*

&nbsp;  ```yaml

&nbsp;  # esphome/security-panel.yaml

&nbsp;  api:

&nbsp;    encryption:

&nbsp;      key: "YOUR\_KEY\_HERE"

&nbsp;  ```

&nbsp;  Must match Home Assistant integration.



4\. \*\*Reboot device\*\*

&nbsp;  - Power cycle PoE

&nbsp;  - Or: ESPHome dashboard → Device → Restart



5\. \*\*Re-adopt device\*\*

&nbsp;  - ESPHome → Device → Adopt

&nbsp;  - Enter API key

&nbsp;  - Update configuration



---



\### Automation Not Working



\*\*Symptoms:\*\*

\- Alarm doesn't auto-arm/disarm

\- Trigger doesn't execute actions

\- Works manually but not automatically



\*\*Solutions:\*\*



1\. \*\*Check automation enabled\*\*

&nbsp;  - Settings → Automations

&nbsp;  - Ensure toggle is ON



2\. \*\*Test trigger\*\*

&nbsp;  - Automation → ⋮ → Information

&nbsp;  - Check "Last Triggered"

&nbsp;  - View trace if available



3\. \*\*Verify conditions\*\*

&nbsp;  ```yaml

&nbsp;  # Common issue: wrong state name

&nbsp;  condition:

&nbsp;    - condition: state

&nbsp;      entity\_id: alarm\_control\_panel.secure\_alarm

&nbsp;      state: "disarmed"  # Must match exactly

&nbsp;  ```



4\. \*\*Check service call\*\*

&nbsp;  - Developer Tools → Services

&nbsp;  - Test service manually

&nbsp;  - Verify PIN is correct



5\. \*\*View automation traces\*\*

&nbsp;  - Automation → ⋮ → Traces

&nbsp;  - See where it fails

&nbsp;  - Check condition results



---



\### High CPU/Memory Usage



\*\*Symptoms:\*\*

\- Home Assistant slow

\- Integration lagging

\- System unresponsive



\*\*Solutions:\*\*



1\. \*\*Check database size\*\*

&nbsp;  ```bash

&nbsp;  du -h /config/secure\_alarm.db

&nbsp;  ```

&nbsp;  If >100MB, clean old events.



2\. \*\*Clean old events\*\*

&nbsp;  ```sql

&nbsp;  sqlite3 /config/secure\_alarm.db "DELETE FROM alarm\_events WHERE timestamp < date('now', '-90 days');"

&nbsp;  sqlite3 /config/secure\_alarm.db "VACUUM;"

&nbsp;  ```



3\. \*\*Reduce logging\*\*

&nbsp;  ```yaml

&nbsp;  # configuration.yaml

&nbsp;  logger:

&nbsp;    default: warning

&nbsp;    logs:

&nbsp;      custom\_components.secure\_alarm: info

&nbsp;  ```



4\. \*\*Check for loops\*\*

&nbsp;  - Automation triggering itself

&nbsp;  - Rapid state changes

&nbsp;  - Review automation traces



---



\### Professional Monitoring Not Connecting



\*\*Symptoms:\*\*

\- Events not reaching monitoring station

\- Connection errors in logs

\- No heartbeat confirmation



\*\*Solutions:\*\*



1\. \*\*Test connection\*\*

&nbsp;  ```yaml

&nbsp;  service: secure\_alarm.update\_config

&nbsp;  data:

&nbsp;    admin\_pin: "ADMIN\_PIN"

&nbsp;  # Then check logs for connection attempt

&nbsp;  ```



2\. \*\*Verify endpoint\*\*

&nbsp;  - Correct IP/hostname

&nbsp;  - Correct port

&nbsp;  - Firewall allows outbound



3\. \*\*Check protocol\*\*

&nbsp;  ```yaml

&nbsp;  # configuration.yaml

&nbsp;  secure\_alarm:

&nbsp;    monitoring:

&nbsp;      protocol: contact\_id  # Must match monitoring station

&nbsp;      endpoint: "correct.address.here:5000"

&nbsp;  ```



4\. \*\*Test mode\*\*

&nbsp;  Enable test mode to see raw messages:

&nbsp;  ```yaml

&nbsp;  secure\_alarm:

&nbsp;    monitoring:

&nbsp;      test\_mode: true

&nbsp;  ```



5\. \*\*Contact monitoring company\*\*

&nbsp;  - Verify account ID

&nbsp;  - Check protocol compatibility

&nbsp;  - Request test event



---



\## Diagnostic Commands



\### System Status Check

```bash

\# Check HA is running

systemctl status home-assistant@homeassistant



\# Check integration loaded

grep "secure\_alarm" /config/home-assistant.log | tail -20



\# Check database

sqlite3 /config/secure\_alarm.db "SELECT name FROM sqlite\_master WHERE type='table';"



\# Check ESPHome device

ping -c 3 192.168.1.XXX

```



\### Full System Test

```yaml

\# 1. Test authentication

service: secure\_alarm.arm\_away

data:

&nbsp; pin: "YOUR\_PIN"



\# 2. Wait for arming



\# 3. Trigger zone (open door)



\# 4. Verify pending state



\# 5. Disarm

service: secure\_alarm.disarm

data:

&nbsp; pin: "YOUR\_PIN"



\# 6. Check logs

\# 7. Check audit trail

```



---



\## Getting Help



If issues persist:



1\. \*\*Gather information\*\*

&nbsp;  - Home Assistant version

&nbsp;  - Integration version

&nbsp;  - Relevant log entries

&nbsp;  - Configuration (sanitized)



2\. \*\*Check existing issues\*\*

&nbsp;  - GitHub Issues

&nbsp;  - Home Assistant Community Forum

&nbsp;  - Search for similar problems



3\. \*\*Create new issue\*\*

&nbsp;  - GitHub: Include diagnostics

&nbsp;  - Forum: Describe steps taken

&nbsp;  - Provide error messages



4\. \*\*Enable debug logging\*\*

&nbsp;  ```yaml

&nbsp;  # configuration.yaml

&nbsp;  logger:

&nbsp;    default: warning

&nbsp;    logs:

&nbsp;      custom\_components.secure\_alarm: debug

&nbsp;  ```

&nbsp;  Then collect logs and share.



---



\## Known Issues



\### Issue: Bypass doesn't persist through restart

\*\*Workaround:\*\* Bypass zones again after restart



\### Issue: Very long PINs (>8 digits) accepted in some scenarios

\*\*Workaround:\*\* Validate PIN length in automations



\### Issue: SMS not working with some providers

\*\*Workaround:\*\* Use alternative SMS integration (Vonage, MessageBird)



Check GitHub Issues for latest known issues and workarounds.

