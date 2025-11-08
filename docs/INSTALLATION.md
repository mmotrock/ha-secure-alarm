\# Installation Guide



\## Prerequisites



\- Home Assistant 2024.1.0 or newer

\- HACS installed (recommended) or manual installation capability

\- ESP32 device with PoE support (Olimex ESP32-POE or WT32-ETH01)

\- PoE+ switch or injector

\- Wired door/window sensors



\## Method 1: HACS Installation (Recommended)



1\. \*\*Open HACS\*\*

&nbsp;  - Navigate to HACS in Home Assistant

&nbsp;  - Click on "Integrations"



2\. \*\*Add Custom Repository\*\* (if not in default HACS)

&nbsp;  - Click the three dots menu (⋮)

&nbsp;  - Select "Custom repositories"

&nbsp;  - Add repository URL: `https://github.com/yourusername/ha-secure-alarm`

&nbsp;  - Category: Integration

&nbsp;  - Click "Add"



3\. \*\*Install Integration\*\*

&nbsp;  - Search for "Secure Alarm System"

&nbsp;  - Click "Download"

&nbsp;  - Restart Home Assistant



4\. \*\*Add Integration\*\*

&nbsp;  - Go to Settings → Devices \& Services

&nbsp;  - Click "+ Add Integration"

&nbsp;  - Search for "Secure Alarm System"

&nbsp;  - Follow setup wizard



\## Method 2: Manual Installation



1\. \*\*Download Files\*\*

&nbsp;  ```bash

&nbsp;  cd /config

&nbsp;  wget https://github.com/yourusername/ha-secure-alarm/releases/latest/download/secure\_alarm.zip

&nbsp;  unzip secure\_alarm.zip

&nbsp;  ```



2\. \*\*Copy Integration\*\*

&nbsp;  ```bash

&nbsp;  cp -r secure\_alarm/custom\_components/secure\_alarm /config/custom\_components/

&nbsp;  ```



3\. \*\*Restart Home Assistant\*\*



4\. \*\*Add Integration\*\*

&nbsp;  - Settings → Devices \& Services → Add Integration

&nbsp;  - Search "Secure Alarm System"



\## Hardware Setup



\### ESP32-POE Configuration



1\. \*\*Install ESPHome\*\*

&nbsp;  - Settings → Add-ons → Add-on Store

&nbsp;  - Install "ESPHome"

&nbsp;  - Start and enable "Start on boot"



2\. \*\*Create Device\*\*

&nbsp;  - Open ESPHome dashboard

&nbsp;  - Click "+ New Device"

&nbsp;  - Name: "Security Panel"

&nbsp;  - Copy provided `security-panel.yaml` configuration



3\. \*\*Configure Secrets\*\*

&nbsp;  ```bash

&nbsp;  cp esphome/secrets.yaml.example config/esphome/secrets.yaml

&nbsp;  nano config/esphome/secrets.yaml

&nbsp;  ```

&nbsp;  

&nbsp;  Generate API key:

&nbsp;  ```bash

&nbsp;  openssl rand -base64 32

&nbsp;  ```



4\. \*\*Flash Device\*\*

&nbsp;  - First time: Connect via USB

&nbsp;  - Click "Install" → "Plug into this computer"

&nbsp;  - After initial flash, use OTA updates



\### Sensor Wiring



Connect sensors to GPIO pins as specified in ESPHome config:



\*\*Direct GPIO (ESP32):\*\*

\- GPIO32: Zone 1 (Front Door)

\- GPIO25: Zone 2 (Back Door)

\- GPIO26: Zone 3 (Garage Door)

\- GPIO27: Zone 4 (Living Room Window)

\- GPIO14: Zone 5 (Bedroom Window)

\- GPIO13: Zone 6 (Kitchen Window)



\*\*Wiring Instructions:\*\*

\- NC (Normally Closed) sensors: Connect one wire to GPIO, other to GND

\- NO (Normally Open) sensors: Set `inverted: false` in ESPHome config

\- Use 22AWG wire for sensor connections

\- Keep wire runs under 100ft to prevent voltage drop



\### Siren/Strobe (Optional)



\- GPIO15: Siren output (12V relay)

\- GPIO4: Strobe output (12V relay)



Use solid-state relays rated for your siren/strobe voltage.



\## Initial Configuration



\### 1. Create Admin Account



During first setup:

\- Enter administrator name

\- Create 6-8 digit PIN

\- Confirm PIN

\- Click "Submit"



\### 2. Configure Zones



\*\*Option A: Using Blueprint\*\*

1\. Settings → Automations \& Scenes → Blueprints

2\. Import zone configuration blueprint

3\. Create automation from blueprint

4\. Map sensor entities to zones

5\. Set zone types (entry/perimeter/interior)

6\. Enable/disable for home/away modes



\*\*Option B: Manual Registration\*\*

```yaml

service: python\_script.register\_alarm\_zone

data:

&nbsp; entity\_id: binary\_sensor.front\_door

&nbsp; zone\_type: entry

&nbsp; enabled\_away: true

&nbsp; enabled\_home: false

```



\### 3. Add Users



```yaml

service: secure\_alarm.add\_user

data:

&nbsp; name: "Family Member"

&nbsp; pin: "654321"

&nbsp; admin\_pin: "YOUR\_ADMIN\_PIN"

&nbsp; is\_admin: false

&nbsp; is\_duress: false

```



\### 4. Install Lovelace Card



1\. \*\*Copy Card File\*\*

&nbsp;  ```bash

&nbsp;  mkdir -p /config/www

&nbsp;  cp www/secure-alarm-card.js /config/www/

&nbsp;  ```



2\. \*\*Add Resource\*\*

&nbsp;  - Settings → Dashboards → Resources

&nbsp;  - Click "+ Add Resource"

&nbsp;  - URL: `/local/secure-alarm-card.js`

&nbsp;  - Type: JavaScript Module



3\. \*\*Add Card\*\*

&nbsp;  ```yaml

&nbsp;  type: custom:secure-alarm-card

&nbsp;  entity: alarm\_control\_panel.secure\_alarm

&nbsp;  entry\_points:

&nbsp;    - entity\_id: lock.front\_door

&nbsp;      name: Front Door

&nbsp;      type: door

&nbsp;      battery\_entity: sensor.front\_door\_battery

&nbsp;    - entity\_id: cover.garage\_door

&nbsp;      name: Garage Door

&nbsp;      type: garage

&nbsp;  ```



\## Optional Features



\### SMS Notifications



1\. \*\*Install Twilio Integration\*\*

&nbsp;  ```yaml

&nbsp;  # configuration.yaml

&nbsp;  notify:

&nbsp;    - platform: twilio\_sms

&nbsp;      name: sms

&nbsp;      account\_sid: !secret twilio\_account\_sid

&nbsp;      auth\_token: !secret twilio\_auth\_token

&nbsp;      from\_number: !secret twilio\_from\_number

&nbsp;  ```



2\. \*\*Enable in Alarm Config\*\*

&nbsp;  ```yaml

&nbsp;  service: secure\_alarm.update\_config

&nbsp;  data:

&nbsp;    admin\_pin: "YOUR\_ADMIN\_PIN"

&nbsp;    notification\_sms: true

&nbsp;    sms\_numbers: "+15551234567,+15559876543"

&nbsp;  ```



\### Professional Monitoring



```yaml

\# configuration.yaml

secure\_alarm:

&nbsp; monitoring:

&nbsp;   enabled: true

&nbsp;   protocol: contact\_id

&nbsp;   endpoint: "monitoring.example.com:5000"

&nbsp;   account\_id: "1234"

&nbsp;   api\_key: "your-api-key"

```



\## Verification



\### Test Checklist



\- \[ ] Integration loads without errors

\- \[ ] Admin account created successfully

\- \[ ] All zones registered and visible

\- \[ ] Entry delay works correctly

\- \[ ] Exit delay works correctly

\- \[ ] Doors lock when arming

\- \[ ] Garage closes when arming

\- \[ ] Mobile notifications received

\- \[ ] Failed PIN attempts trigger lockout

\- \[ ] Audit log records events

\- \[ ] Lovelace card displays correctly

\- \[ ] Entry points toggle correctly



\### Test Duress Code



```yaml

service: secure\_alarm.add\_user

data:

&nbsp; name: "Duress Code"

&nbsp; pin: "999999"

&nbsp; admin\_pin: "YOUR\_ADMIN\_PIN"

&nbsp; is\_duress: true

```



Test by using duress PIN to disarm - should disarm but send silent alert.



\## Troubleshooting



\### Integration Won't Load



Check logs:

```bash

tail -f /config/home-assistant.log | grep secure\_alarm

```



Common issues:

\- Missing bcrypt dependency: `pip install bcrypt==4.0.1`

\- Database permissions: `chmod 644 /config/secure\_alarm.db`

\- Syntax errors in configuration



\### Zones Not Triggering



1\. Check ESPHome device is online

2\. Verify GPIO pin assignments match physical wiring

3\. Test sensor with multimeter (should be closed circuit)

4\. Check entity IDs match in zone configuration



\### Card Not Displaying



1\. Verify resource is added to Lovelace

2\. Clear browser cache

3\. Check browser console for JavaScript errors

4\. Ensure card file is in `/config/www/`



\### Can't Add Users



\- Verify admin PIN is correct

\- Check for lockout status

\- Ensure PIN is 6-8 digits numeric only



\## Backup



Include these files in backups:

\- `/config/custom\_components/secure\_alarm/`

\- `/config/secure\_alarm.db`

\- `/config/esphome/security-panel.yaml`

\- `/config/esphome/secrets.yaml`



\## Support



\- GitHub Issues: Report bugs and request features

\- Home Assistant Community: Ask questions in forum

\- Documentation: Read full docs in `/docs/`

