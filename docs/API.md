\# API Reference



\## Services



All services are under the `secure\_alarm` domain.



\### secure\_alarm.arm\_away



Arm the system in away mode (monitors all zones).



\*\*Parameters:\*\*

| Parameter | Type | Required | Description |

|-----------|------|----------|-------------|

| pin | string | Yes | User PIN (6-8 digits) |

| code | string | No | User identifier for logging |



\*\*Example:\*\*

```yaml

service: secure\_alarm.arm\_away

data:

&nbsp; pin: "123456"

&nbsp; code: "automation"

```



\*\*Returns:\*\* None (state change reflected in entity)



\*\*Events Fired:\*\*

\- `secure\_alarm\_armed` with `mode: armed\_away`

\- `secure\_alarm\_state\_changed`



---



\### secure\_alarm.arm\_home



Arm the system in home mode (monitors perimeter only).



\*\*Parameters:\*\*

| Parameter | Type | Required | Description |

|-----------|------|----------|-------------|

| pin | string | Yes | User PIN (6-8 digits) |

| code | string | No | User identifier for logging |



\*\*Example:\*\*

```yaml

service: secure\_alarm.arm\_home

data:

&nbsp; pin: "123456"

```



\*\*Events Fired:\*\*

\- `secure\_alarm\_armed` with `mode: armed\_home`



---



\### secure\_alarm.disarm



Disarm the alarm system.



\*\*Parameters:\*\*

| Parameter | Type | Required | Description |

|-----------|------|----------|-------------|

| pin | string | Yes | User PIN (6-8 digits) |

| code | string | No | User identifier for logging |



\*\*Example:\*\*

```yaml

service: secure\_alarm.disarm

data:

&nbsp; pin: "654321"

&nbsp; code: "john\_doe"

```



\*\*Events Fired:\*\*

\- `secure\_alarm\_disarmed`

\- `secure\_alarm\_duress\_code\_used` (if duress PIN used)



---



\### secure\_alarm.add\_user



Add a new user to the system (admin only).



\*\*Parameters:\*\*

| Parameter | Type | Required | Default | Description |

|-----------|------|----------|---------|-------------|

| name | string | Yes | - | User's display name |

| pin | string | Yes | - | New user's PIN (6-8 digits) |

| admin\_pin | string | Yes | - | Admin PIN for authorization |

| is\_admin | boolean | No | false | Grant admin privileges |

| is\_duress | boolean | No | false | Is this a duress code |



\*\*Example:\*\*

```yaml

service: secure\_alarm.add\_user

data:

&nbsp; name: "Jane Doe"

&nbsp; pin: "789012"

&nbsp; admin\_pin: "000000"

&nbsp; is\_admin: false

&nbsp; is\_duress: false

```



\*\*Returns:\*\* User ID in logs



---



\### secure\_alarm.remove\_user



Remove a user from the system (admin only).



\*\*Parameters:\*\*

| Parameter | Type | Required | Description |

|-----------|------|----------|-------------|

| user\_id | integer | Yes | ID of user to remove |

| admin\_pin | string | Yes | Admin PIN for authorization |



\*\*Example:\*\*

```yaml

service: secure\_alarm.remove\_user

data:

&nbsp; user\_id: 5

&nbsp; admin\_pin: "000000"

```



---



\### secure\_alarm.bypass\_zone



Bypass or unbypass a zone temporarily.



\*\*Parameters:\*\*

| Parameter | Type | Required | Default | Description |

|-----------|------|----------|---------|-------------|

| zone\_entity\_id | string | Yes | - | Entity ID of zone sensor |

| pin | string | Yes | - | User PIN |

| bypass | boolean | No | true | True to bypass, false to restore |



\*\*Example:\*\*

```yaml

service: secure\_alarm.bypass\_zone

data:

&nbsp; zone\_entity\_id: binary\_sensor.garage\_door

&nbsp; pin: "123456"

&nbsp; bypass: true

```



---



\### secure\_alarm.update\_config



Update system configuration (admin only).



\*\*Parameters:\*\*

| Parameter | Type | Required | Description |

|-----------|------|----------|-------------|

| admin\_pin | string | Yes | Admin PIN for authorization |

| entry\_delay | integer | No | Entry delay in seconds (0-300) |

| exit\_delay | integer | No | Exit delay in seconds (0-300) |

| alarm\_duration | integer | No | Alarm duration in seconds (60-3600) |

| lock\_delay\_home | integer | No | Lock delay for arm home (0-60) |

| lock\_delay\_away | integer | No | Lock delay for arm away (0-300) |

| close\_delay\_home | integer | No | Garage close delay for arm home |

| close\_delay\_away | integer | No | Garage close delay for arm away |

| notification\_mobile | boolean | No | Enable mobile notifications |

| notification\_sms | boolean | No | Enable SMS notifications |

| sms\_numbers | string | No | Comma-separated phone numbers |



\*\*Example:\*\*

```yaml

service: secure\_alarm.update\_config

data:

&nbsp; admin\_pin: "000000"

&nbsp; entry\_delay: 45

&nbsp; exit\_delay: 90

&nbsp; notification\_mobile: true

&nbsp; notification\_sms: true

&nbsp; sms\_numbers: "+15551234567,+15559876543"

```



---



\## Events



\### secure\_alarm\_armed



Fired when system is armed.



\*\*Data:\*\*

```yaml

mode: "armed\_away"  # or "armed\_home"

changed\_by: "John Doe"

timestamp: "2024-01-15T10:30:00"

```



---



\### secure\_alarm\_disarmed



Fired when system is disarmed.



\*\*Data:\*\*

```yaml

changed\_by: "Jane Doe"

timestamp: "2024-01-15T18:45:00"

```



---



\### secure\_alarm\_triggered



Fired when alarm is triggered.



\*\*Data:\*\*

```yaml

zone: "Front Door"

zone\_entity\_id: "binary\_sensor.front\_door"

timestamp: "2024-01-15T02:30:00"

```



---



\### secure\_alarm\_duress\_code\_used



Fired when a duress code is used (silent alert).



\*\*Data:\*\*

```yaml

user\_name: "Duress Code"

user\_id: 10

timestamp: "2024-01-15T23:15:00"

```



---



\### secure\_alarm\_failed\_auth



Fired on failed PIN attempts.



\*\*Data:\*\*

```yaml

attempts: 3

locked\_out: false

timestamp: "2024-01-15T14:20:00"

```



---



\### secure\_alarm\_state\_changed



Fired on any state change.



\*\*Data:\*\*

```yaml

state: "armed\_away"

previous\_state: "disarmed"

changed\_by: "Automation"

timestamp: "2024-01-15T08:00:00"

```



---



\## Entities



\### alarm\_control\_panel.secure\_alarm



Main alarm control panel entity.



\*\*States:\*\*

\- `disarmed` - System is off

\- `armed\_home` - Perimeter armed

\- `armed\_away` - All zones armed

\- `arming` - Exit delay in progress

\- `pending` - Entry delay in progress

\- `triggered` - Alarm activated



\*\*Attributes:\*\*

```yaml

changed\_by: "John Doe"

code\_format: "number"

zones\_bypassed: \["Garage Door"]

active\_zones: 6

failed\_attempts: 0

triggered\_by: null

```



---



\### sensor.secure\_alarm\_status



Current alarm status.



\*\*State:\*\* Human-readable status text



\*\*Attributes:\*\*

```yaml

state\_raw: "armed\_away"

changed\_by: "Jane Doe"

triggered\_by: null

```



---



\### sensor.secure\_alarm\_failed\_login\_attempts



Failed PIN attempt counter.



\*\*State:\*\* Number of recent failed attempts



\*\*Unit:\*\* attempts



---



\### sensor.secure\_alarm\_last\_changed\_by



Last user who changed alarm state.



\*\*State:\*\* User name or "Unknown"



---



\### sensor.secure\_alarm\_active\_zones



Number of currently monitored zones.



\*\*State:\*\* Zone count



\*\*Attributes:\*\*

```yaml

total\_zones: 6

bypassed\_zones: \[]

```



---



\### binary\_sensor.secure\_alarm\_armed



Is the system armed (any mode)?



\*\*State:\*\* `on` (armed) or `off` (disarmed)



\*\*Device Class:\*\* safety



---



\### binary\_sensor.secure\_alarm\_triggered



Is the alarm currently triggered?



\*\*State:\*\* `on` (triggered) or `off` (not triggered)



\*\*Device Class:\*\* problem



---



\### binary\_sensor.secure\_alarm\_locked\_out



Is the system locked due to failed attempts?



\*\*State:\*\* `on` (locked) or `off` (not locked)



\*\*Device Class:\*\* lock



---



\## Python Script API



\### register\_alarm\_zone.py



Register a sensor as an alarm zone.



\*\*Parameters:\*\*

```python

entity\_id: str        # Sensor entity ID

zone\_type: str        # "entry", "perimeter", or "interior"

enabled\_away: bool    # Monitor in away mode

enabled\_home: bool    # Monitor in home mode

```



\*\*Example:\*\*

```yaml

service: python\_script.register\_alarm\_zone

data:

&nbsp; entity\_id: binary\_sensor.front\_door

&nbsp; zone\_type: entry

&nbsp; enabled\_away: true

&nbsp; enabled\_home: false

```



---



\## Database Schema



\### Table: alarm\_users



```sql

id INTEGER PRIMARY KEY

name TEXT NOT NULL

pin\_hash TEXT NOT NULL

is\_admin INTEGER DEFAULT 0

is\_duress INTEGER DEFAULT 0

enabled INTEGER DEFAULT 1

created\_at TIMESTAMP

last\_used TIMESTAMP

use\_count INTEGER DEFAULT 0

```



---



\### Table: alarm\_config



```sql

id INTEGER PRIMARY KEY DEFAULT 1

entry\_delay INTEGER DEFAULT 30

exit\_delay INTEGER DEFAULT 60

alarm\_duration INTEGER DEFAULT 300

trigger\_doors TEXT

notification\_mobile INTEGER DEFAULT 1

notification\_sms INTEGER DEFAULT 0

sms\_numbers TEXT

lock\_delay\_home INTEGER DEFAULT 0

lock\_delay\_away INTEGER DEFAULT 60

close\_delay\_home INTEGER DEFAULT 0

close\_delay\_away INTEGER DEFAULT 60

updated\_at TIMESTAMP

```



---



\### Table: alarm\_events



```sql

id INTEGER PRIMARY KEY

event\_type TEXT NOT NULL

user\_id INTEGER

user\_name TEXT

timestamp TIMESTAMP

state\_from TEXT

state\_to TEXT

zone\_entity\_id TEXT

details TEXT

is\_duress INTEGER DEFAULT 0

```



---



\### Table: alarm\_zones



```sql

id INTEGER PRIMARY KEY

entity\_id TEXT UNIQUE NOT NULL

zone\_name TEXT NOT NULL

zone\_type TEXT NOT NULL

enabled\_away INTEGER DEFAULT 1

enabled\_home INTEGER DEFAULT 1

bypassed INTEGER DEFAULT 0

bypass\_until TIMESTAMP

last\_state\_change TIMESTAMP

```



---



\### Table: failed\_attempts



```sql

id INTEGER PRIMARY KEY

timestamp TIMESTAMP

ip\_address TEXT

user\_code TEXT

attempt\_type TEXT

```



---



\## REST API (Via Home Assistant)



All services can be called via Home Assistant REST API:



```bash

curl -X POST \\

&nbsp; http://homeassistant.local:8123/api/services/secure\_alarm/arm\_away \\

&nbsp; -H "Authorization: Bearer YOUR\_TOKEN" \\

&nbsp; -H "Content-Type: application/json" \\

&nbsp; -d '{"pin": "123456"}'

```



---



\## WebSocket API



Subscribe to events via WebSocket:



```javascript

{

&nbsp; "type": "subscribe\_events",

&nbsp; "event\_type": "secure\_alarm\_triggered"

}

```



---



\## Error Codes



| Code | Message | Description |

|------|---------|-------------|

| `pin\_invalid` | Invalid PIN | PIN format incorrect or doesn't exist |

| `pin\_locked` | System locked out | Too many failed attempts |

| `pin\_length` | PIN must be 6-8 digits | PIN length validation failed |

| `admin\_required` | Admin authorization required | Action requires admin PIN |

| `zone\_not\_found` | Zone not found | Zone entity ID doesn't exist |

| `already\_armed` | System already armed | Cannot arm when already armed |

| `database\_error` | Database operation failed | Database query failed |



---



\## Rate Limits



\- \*\*Failed PIN attempts\*\*: 5 attempts per 5 minutes

\- \*\*API calls\*\*: No hard limit (subject to HA limits)

\- \*\*Monitoring heartbeat\*\*: Default 1 per hour



---



\## Versioning



API version follows integration version (v1.0.0).



Breaking changes will increment major version.

