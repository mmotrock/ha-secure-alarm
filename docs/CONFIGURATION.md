\# Configuration Guide



\## Table of Contents

\- \[Timing Configuration](#timing-configuration)

\- \[Zone Configuration](#zone-configuration)

\- \[User Management](#user-management)

\- \[Notifications](#notifications)

\- \[Entry Points](#entry-points)

\- \[Automations](#automations)



\## Timing Configuration



\### Update Delays



```yaml

service: secure\_alarm.update\_config

data:

&nbsp; admin\_pin: "YOUR\_ADMIN\_PIN"

&nbsp; entry\_delay: 30          # Seconds to disarm after entry

&nbsp; exit\_delay: 60           # Seconds to exit after arming away

&nbsp; alarm\_duration: 300      # Seconds alarm sounds

&nbsp; lock\_delay\_home: 0       # Instant lock when arm home

&nbsp; lock\_delay\_away: 60      # Lock after exit delay

&nbsp; close\_delay\_home: 0      # Instant garage close

&nbsp; close\_delay\_away: 60     # Close after exit delay

```



\*\*Entry Delay\*\*: Time allowed to disarm after opening entry door

\- Recommended: 30 seconds

\- Range: 0-300 seconds

\- Set to 0 for instant trigger



\*\*Exit Delay\*\*: Time to exit before system arms

\- Recommended: 60 seconds  

\- Range: 0-300 seconds

\- Only applies to arm\_away mode



\*\*Alarm Duration\*\*: How long siren sounds

\- Recommended: 300 seconds (5 minutes)

\- Range: 60-3600 seconds

\- Can be stopped early by disarming



\## Zone Configuration



\### Zone Types



\*\*Entry Zones\*\*: Allow entry delay

\- Front door, back door, garage

\- Gives time to disarm before triggering

\- Use for primary entry points



\*\*Perimeter Zones\*\*: Instant trigger

\- Windows, basement doors, side doors

\- No delay when armed

\- Use for points that shouldn't be opened when armed



\*\*Interior Zones\*\*: Motion detectors, glass break

\- Only active in armed\_away mode

\- Ignored in armed\_home mode

\- Instant trigger



\### Register Zone



```yaml

service: python\_script.register\_alarm\_zone

data:

&nbsp; entity\_id: binary\_sensor.front\_door

&nbsp; zone\_type: entry              # entry, perimeter, or interior

&nbsp; enabled\_away: true            # Monitor in away mode

&nbsp; enabled\_home: false           # Don't monitor in home mode

```



\### Zone Blueprint



Use automation blueprint for easier configuration:



1\. Import blueprint from `/blueprints/automation/secure\_alarm/configure\_zones.yaml`

2\. Create automation

3\. Select entities for each zone

4\. Set zone types

5\. Enable/disable for each arm mode



\### Bypass Zone



Temporarily disable a zone:



```yaml

service: secure\_alarm.bypass\_zone

data:

&nbsp; zone\_entity\_id: binary\_sensor.garage\_door

&nbsp; pin: "YOUR\_PIN"

&nbsp; bypass: true    # false to re-enable

```



\*\*Use Cases\*\*:

\- Working in garage while armed

\- Window open for ventilation

\- Sensor maintenance/replacement



\## User Management



\### Add User



```yaml

service: secure\_alarm.add\_user

data:

&nbsp; name: "John Doe"

&nbsp; pin: "123456"              # 6-8 digits

&nbsp; admin\_pin: "ADMIN\_PIN"     # Your admin PIN

&nbsp; is\_admin: false            # Grant admin privileges

&nbsp; is\_duress: false           # Is this a duress code

```



\### Admin vs Regular Users



\*\*Admin Can\*\*:

\- Add/remove users

\- Change configuration

\- Bypass zones

\- View audit logs



\*\*Regular Users Can\*\*:

\- Arm/disarm system

\- Use all arm modes

\- View current status



\### Duress Code



Silent alarm that appears to work normally:



```yaml

service: secure\_alarm.add\_user

data:

&nbsp; name: "Duress - Silent Alert"

&nbsp; pin: "999999"

&nbsp; admin\_pin: "ADMIN\_PIN"

&nbsp; is\_admin: false

&nbsp; is\_duress: true          # This makes it a duress code

```



\*\*When duress code is used\*\*:

\- System appears to disarm normally

\- Silent notification sent to admin

\- Event logged with duress flag

\- No visible indication to intruder



\### Remove User



```yaml

service: secure\_alarm.remove\_user

data:

&nbsp; user\_id: 2               # Get from database or logs

&nbsp; admin\_pin: "ADMIN\_PIN"

```



\## Notifications



\### Mobile Notifications



Enabled by default if Home Assistant Companion app installed.



\*\*Customize\*\*:

```yaml

service: secure\_alarm.update\_config

data:

&nbsp; admin\_pin: "ADMIN\_PIN"

&nbsp; notification\_mobile: true

```



\*\*Notification Events\*\*:

\- System armed/disarmed

\- Alarm triggered

\- Entry delay started

\- Duress code used

\- Failed PIN attempts

\- System locked out



\### SMS Notifications



Requires Twilio or similar SMS integration.



\*\*Setup Twilio\*\*:

```yaml

\# configuration.yaml

notify:

&nbsp; - platform: twilio\_sms

&nbsp;   name: sms

&nbsp;   account\_sid: !secret twilio\_account\_sid

&nbsp;   auth\_token: !secret twilio\_auth\_token

&nbsp;   from\_number: !secret twilio\_from\_number

```



\*\*Enable SMS\*\*:

```yaml

service: secure\_alarm.update\_config

data:

&nbsp; admin\_pin: "ADMIN\_PIN"

&nbsp; notification\_sms: true

&nbsp; sms\_numbers: "+15551234567,+15559876543"

```



\*\*SMS Events\*\*:

\- Alarm triggered

\- Duress code used

\- System armed away (optional)



\### Custom Notifications



Create automations for custom notification logic:



```yaml

automation:

&nbsp; - alias: "Custom Alarm Notification"

&nbsp;   trigger:

&nbsp;     - platform: event

&nbsp;       event\_type: secure\_alarm\_triggered

&nbsp;   action:

&nbsp;     - service: notify.custom\_service

&nbsp;       data:

&nbsp;         title: "Alarm!"

&nbsp;         message: "{{ trigger.event.data.zone }}"

```



\## Entry Points



Configure door locks and garage doors in Lovelace card.



\### Card Configuration



```yaml

type: custom:secure-alarm-card

entity: alarm\_control\_panel.secure\_alarm

entry\_points:

&nbsp; - entity\_id: lock.front\_door

&nbsp;   name: Front Door

&nbsp;   type: door                           # door or garage

&nbsp;   battery\_entity: sensor.front\_door\_battery

&nbsp; 

&nbsp; - entity\_id: lock.back\_door

&nbsp;   name: Back Door

&nbsp;   type: door

&nbsp;   battery\_entity: sensor.back\_door\_battery

&nbsp; 

&nbsp; - entity\_id: cover.garage\_door

&nbsp;   name: Garage Door

&nbsp;   type: garage

&nbsp;   # No battery for hardwired garage

```



\### Entry Point Types



\*\*door\*\*: Lock/unlock icon, shows locked/unlocked state

\*\*garage\*\*: Garage icon, shows open/closed state



\### Battery Monitoring



Optional battery level display:

\- Shows percentage next to entry point

\- Color coded: Green (>50%), Yellow (20-50%), Red (<20%)

\- Omit `battery\_entity` for hardwired devices



\### Last Changed Timestamp



Automatically tracked:

\- Shows "5m ago", "2h ago", "3d ago"

\- Updates when state changes

\- Helps identify unusual activity



\## Automations



\### Auto-Arm on Departure



```yaml

automation:

&nbsp; - alias: "Auto Arm Away"

&nbsp;   trigger:

&nbsp;     - platform: state

&nbsp;       entity\_id: group.all\_persons

&nbsp;       to: "not\_home"

&nbsp;       for: "00:05:00"

&nbsp;   condition:

&nbsp;     - condition: state

&nbsp;       entity\_id: alarm\_control\_panel.secure\_alarm

&nbsp;       state: "disarmed"

&nbsp;   action:

&nbsp;     - service: secure\_alarm.arm\_away

&nbsp;       data:

&nbsp;         pin: !secret alarm\_automation\_pin

```



\### Auto-Disarm on Arrival



```yaml

automation:

&nbsp; - alias: "Auto Disarm"

&nbsp;   trigger:

&nbsp;     - platform: state

&nbsp;       entity\_id: person.john

&nbsp;       to: "home"

&nbsp;   condition:

&nbsp;     - condition: state

&nbsp;       entity\_id: alarm\_control\_panel.secure\_alarm

&nbsp;       state: "armed\_away"

&nbsp;   action:

&nbsp;     - service: secure\_alarm.disarm

&nbsp;       data:

&nbsp;         pin: !secret alarm\_automation\_pin

```



\### Bedtime Arm Home



```yaml

automation:

&nbsp; - alias: "Arm Home at Bedtime"

&nbsp;   trigger:

&nbsp;     - platform: time

&nbsp;       at: "23:00:00"

&nbsp;   condition:

&nbsp;     - condition: state

&nbsp;       entity\_id: alarm\_control\_panel.secure\_alarm

&nbsp;       state: "disarmed"

&nbsp;   action:

&nbsp;     - service: secure\_alarm.arm\_home

&nbsp;       data:

&nbsp;         pin: !secret alarm\_automation\_pin

```



\### Trigger Response



```yaml

automation:

&nbsp; - alias: "Alarm Triggered Actions"

&nbsp;   trigger:

&nbsp;     - platform: event

&nbsp;       event\_type: secure\_alarm\_triggered

&nbsp;   action:

&nbsp;     # Turn on all lights

&nbsp;     - service: light.turn\_on

&nbsp;       target:

&nbsp;         entity\_id: all

&nbsp;       data:

&nbsp;         brightness: 255

&nbsp;     

&nbsp;     # Take camera snapshots

&nbsp;     - service: camera.snapshot

&nbsp;       target:

&nbsp;         entity\_id: camera.front\_door

&nbsp;       data:

&nbsp;         filename: "/config/www/alarm\_{{ now().timestamp() }}.jpg"

&nbsp;     

&nbsp;     # Send notification

&nbsp;     - service: notify.mobile\_app\_all

&nbsp;       data:

&nbsp;         title: "🚨 ALARM!"

&nbsp;         message: "Zone: {{ trigger.event.data.zone }}"

```



\## Advanced Configuration



\### Professional Monitoring



```yaml

\# configuration.yaml

secure\_alarm:

&nbsp; monitoring:

&nbsp;   enabled: true

&nbsp;   protocol: contact\_id    # contact\_id, alarm\_net, sia, webhook

&nbsp;   endpoint: "monitoring.example.com:5000"

&nbsp;   account\_id: "1234"

&nbsp;   api\_key: "your-api-key"

&nbsp;   test\_mode: false

&nbsp;   heartbeat\_enabled: true

&nbsp;   heartbeat\_interval: 3600

```



\### Vacation Mode



```yaml

input\_boolean:

&nbsp; vacation\_mode:

&nbsp;   name: Vacation Mode

&nbsp;   icon: mdi:beach



automation:

&nbsp; - alias: "Vacation Mode Arm"

&nbsp;   trigger:

&nbsp;     - platform: state

&nbsp;       entity\_id: input\_boolean.vacation\_mode

&nbsp;       to: "on"

&nbsp;   action:

&nbsp;     - service: secure\_alarm.arm\_away

&nbsp;       data:

&nbsp;         pin: !secret alarm\_automation\_pin

```



\### Zone-Specific Delays



Different delays per zone not directly supported, but can be achieved with template sensors and automations.



\## Secrets Management



Store sensitive data in `secrets.yaml`:



```yaml

\# secrets.yaml

alarm\_automation\_pin: "123456"

alarm\_admin\_pin: "000000"

emergency\_phone: "+15551234567"

twilio\_account\_sid: "AC..."

twilio\_auth\_token: "..."

twilio\_from\_number: "+15559999999"

```



Reference in configs:

```yaml

pin: !secret alarm\_automation\_pin

```



\## Database Maintenance



\### View Audit Logs



Query database directly:

```sql

sqlite3 /config/secure\_alarm.db "SELECT \* FROM alarm\_events ORDER BY timestamp DESC LIMIT 20;"

```



\### Backup Database



```bash

cp /config/secure\_alarm.db /config/backups/secure\_alarm\_$(date +%Y%m%d).db

```



\### Clean Old Events



Automatically managed by integration. Manual cleanup:

```sql

sqlite3 /config/secure\_alarm.db "DELETE FROM alarm\_events WHERE timestamp < date('now', '-90 days');"

```



\## Troubleshooting Configuration



\### Check Current Config



```yaml

service: python\_script.get\_alarm\_config

```



\### Verify Zone Registration



Check Developer Tools → States for:

\- `sensor.secure\_alarm\_active\_zones`

\- Zone attributes on alarm entity



\### Test Notifications



```yaml

service: notify.mobile\_app\_phone

data:

&nbsp; title: "Test"

&nbsp; message: "Alarm notification test"

```



\### Validate User PINs



Attempt to arm with each user's PIN to verify they work.



\### Reset Configuration



Last resort - remove integration and re-add:

1\. Delete integration from UI

2\. Remove `/config/secure\_alarm.db`

3\. Re-add integration

4\. Reconfigure all settings

