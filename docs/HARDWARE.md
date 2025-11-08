# Hardware Setup Guide

## Supported Hardware

### Recommended Setup
- **Olimex ESP32-POE** or **WT32-ETH01**
- PoE+ switch or injector (802.3af/at)
- Wired door/window sensors (NC preferred)
- 12V siren and strobe (optional)

### Alternative Options
- **Konnected Alarm Panel Pro** (turnkey solution)
- ESP32 with separate PoE adapter
- ESP8266 with Ethernet adapter
- Raspberry Pi with GPIO expansion

---

## ESP32-POE Setup

### Hardware Overview

**Olimex ESP32-POE Specifications:**
- ESP32-WROOM-32 module
- Ethernet 10/100 Mbps
- PoE 802.3af (15.4W)
- 26 GPIO pins available
- I2C, SPI, UART interfaces
- USB programming port

**Power:**
- PoE input: 36-57V DC
- Board output: 5V @ 2A
- GPIO output: 3.3V @ 500mA total

### Pin Assignments

#### Direct GPIO Zones (6 zones)
```
GPIO32 → Zone 1 (Front Door)
GPIO25 → Zone 2 (Back Door)
GPIO26 → Zone 3 (Garage Door)
GPIO27 → Zone 4 (Living Room Window)
GPIO14 → Zone 5 (Bedroom Window)
GPIO13 → Zone 6 (Kitchen Window)
```

#### Outputs
```
GPIO15 → Siren relay
GPIO4  → Strobe relay
GPIO33 → Status LED (built-in)
```

#### Reserved Pins (Don't Use)
```
GPIO12 → PoE power control
GPIO17 → Ethernet CLK
GPIO18 → Ethernet MDIO
GPIO23 → Ethernet MDC
GPIO0  → Boot mode (keep high)
GPIO2  → Boot mode (keep floating)
```

#### Expansion (I2C for MCP23017)
```
GPIO13 → I2C SDA
GPIO16 → I2C SCL
```

---

## Sensor Wiring

### Normally Closed (NC) Sensors

**Recommended for security applications.**

**Wiring:**
```
ESP32 GPIO Pin ----[NC Sensor]---- GND
                     │
                   (Magnet)
```

**Operation:**
- Door closed: Circuit complete (LOW signal)
- Door open: Circuit breaks (HIGH signal)
- Wire cut: Same as open (detected)

**ESPHome Config:**
```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO32
      mode: INPUT_PULLUP
      inverted: true    # NC sensors need inversion
    name: "Front Door"
```

### Normally Open (NO) Sensors

**Less secure - wire cut not detected.**

**Wiring:**
```
ESP32 GPIO Pin ----[NO Sensor]---- GND
                     │
                   (Magnet)
```

**Operation:**
- Door closed: Circuit open (HIGH signal)
- Door open: Circuit complete (LOW signal)
- Wire cut: Same as closed (NOT detected)

**ESPHome Config:**
```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO32
      mode: INPUT_PULLUP
      inverted: false   # NO sensors don't need inversion
    name: "Front Door"
```

### End-of-Line (EOL) Resistors

**Most secure - detects tampering.**

**Wiring:**
```
ESP32 GPIO ----[10kΩ]----+----[NC Sensor]----[10kΩ]---- GND
                         │
                      (Read voltage)
```

**Operation:**
- Normal: ~1.65V (resistor divider)
- Open: ~3.3V (door open)
- Short: 0V (tamper/cut)

Requires ADC pin and custom logic in ESPHome.

---

## Wiring Best Practices

### Wire Selection
- **22 AWG** solid core for permanent installations
- **18 AWG** for long runs (>50ft)
- Stranded wire for flexible connections
- Shielded cable for noisy environments

### Maximum Wire Lengths
- **22 AWG**: 100 feet
- **18 AWG**: 200 feet
- Longer runs require voltage drop compensation

### Color Coding
Suggested standard:
- **Red**: +3.3V (if powering sensor)
- **Black**: Ground
- **White**: Signal
- **Green**: Not used
- **Yellow**: Zone 2 signal
- **Blue**: Zone 3 signal

### Terminal Blocks
Use screw terminals for field wiring:
- 5mm pitch recommended
- 12-22 AWG capacity
- Label each zone clearly

---

## Siren/Strobe Wiring

### Relay Requirements
- Solid state relay (SSR) preferred
- Rating: 12V DC, 2A minimum
- Optoisolated from ESP32

### Circuit Diagram
```
ESP32 GPIO15 → SSR Input (+)
        GND  → SSR Input (-)

12V Power (+) → SSR Output (+)
Siren (+)     → SSR Output (-)
Siren (-)     → 12V Power (-)
```

### Wiring Notes
- Use separate 12V power supply for siren
- Don't power siren from ESP32 (insufficient current)
- Add flyback diode across relay coil
- Fuse 12V circuit appropriately

### Recommended Sirens
- **Piezo sirens**: 110-120dB, low current
- **Electromechanical**: Classic bell sound
- **Electronic**: Programmable tones
- Outdoor rated (IP65+) for exterior use

---

## GPIO Expansion

### Using MCP23017 (16 Additional Pins)

**Hardware:**
- MCP23017 I2C GPIO expander
- I2C address: 0x20-0x27 (jumper selectable)
- Supports up to 8 chips (128 additional GPIOs)

**Connection:**
```
ESP32          MCP23017
GPIO13 (SDA) → SDA
GPIO16 (SCL) → SCL
3.3V         → VDD
GND          → GND, A0, A1, A2 (address 0x20)
```

**ESPHome Config:**
```yaml
i2c:
  sda: GPIO13
  scl: GPIO16
  scan: true

mcp23017:
  - id: mcp23017_hub
    address: 0x20

binary_sensor:
  - platform: gpio
    pin:
      mcp23xxx: mcp23017_hub
      number: 0
      mode: INPUT_PULLUP
      inverted: true
    name: "Zone 7"
```

### PCF8574 Alternative
- 8 GPIO pins per chip
- Simpler than MCP23017
- Lower cost
- Same I2C wiring

---

## Power Supply

### PoE Power Budget
- ESP32-POE: ~2W idle, ~4W peak
- Per zone: ~0.1mA (negligible)
- Status LED: ~20mA
- Total: ~4.5W
- PoE budget: 15.4W (plenty of headroom)

### Backup Power (Optional)
Add battery backup for power outages:
- 18650 Li-ion cells (2S or 3S)
- TP4056 charging module
- AMS1117 3.3V regulator
- Diode isolation from PoE

**Circuit:**
```
PoE 5V → Diode → ESP32 5V
              → TP4056 → Battery → AMS1117 → ESP32 5V
```

---

## Physical Installation

### ESP32 Enclosure
- DIN rail mountable box recommended
- Ventilated for heat dissipation
- Access holes for wiring
- Lockable for security

### Sensor Placement

**Door Sensors:**
- Mount on stationary frame
- Magnet on moving door
- Gap: <10mm when closed
- Avoid metal interference

**Window Sensors:**
- Top or side of frame
- Recessed for concealment
- Wire through frame if possible

**Glass Break:**
- Mount on ceiling or opposite wall
- 20-25 feet maximum range
- Avoid corners (sound distortion)

**Motion Detectors:**
- Corner mount for 90° coverage
- 6-8 feet high
- Avoid heat sources (false triggers)

### Wiring Runs
- Use conduit for exposed runs
- Staple wires every 12 inches in walls
- Avoid parallel runs with AC power (>6" separation)
- Label both ends of each wire

---

## Testing & Commissioning

### Pre-Power Checks
1. Verify all NC sensors show continuity when closed
2. Check for shorts between GPIO and GND
3. Confirm PoE polarity (if using external adapter)
4. Inspect all solder joints and connections

### Initial Power-Up
1. Connect only PoE (no sensors yet)
2. Watch serial output for boot messages
3. Verify Ethernet link LED
4. Check ESPHome logs for connectivity

### Sensor Testing
1. Connect one sensor at a time
2. Open/close and verify in ESPHome logs
3. Check response time (<100ms)
4. Test full open/close cycles (10x)

### System Integration
1. Add sensors to Home Assistant
2. Register as alarm zones
3. Test arming/disarming
4. Verify delays work correctly
5. Test siren activation

---

## Troubleshooting

### No Sensor Readings
- Check GPIO assignment in ESPHome
- Verify INPUT_PULLUP mode enabled
- Test continuity with multimeter
- Check for loose connections

### Intermittent Triggers
- Electrical interference nearby
- Loose sensor mounting
- Weak magnet or large gap
- Wire run too long (add debounce)

### ESP32 Won't Boot
- GPIO0 pulled low (remove sensor)
- Insufficient PoE power
- Damaged ESP32 module
- Brown-out on power-up

### Ethernet Not Working
- Wrong pin assignments for PoE board
- Cable not CAT5e or better
- PoE injector on wrong end
- Switch port not PoE capable

---

## Upgrade Path

### From 6 to 12 Zones
1. Add MCP23017 chip
2. Wire to I2C bus
3. Update ESPHome config
4. Register new zones in HA

### From 12 to 24+ Zones
1. Add second MCP23017 (address 0x21)
2. Chain I2C connection
3. Update ESPHome config
4. No software limit on zone count

### Adding Wireless Sensors
1. Install Zigbee/Z-Wave USB stick
2. Pair wireless sensors
3. Register as zones (no ESPHome needed)
4. Mixed wired/wireless supported

---

## Shopping List

### Basic 6-Zone System
- 1× Olimex ESP32-POE ($30)
- 1× PoE injector 802.3af ($10-20)
- 6× NC door/window sensors ($2-5 each)
- 1× Project enclosure ($10)
- 1× Terminal blocks ($5)
- 50ft 22AWG wire ($10)

**Total: ~$90-120**

### Expanded 12-Zone System
Add:
- 1× MCP23017 chip ($1)
- 6× Additional sensors ($12-30)
- 50ft Additional wire ($10)

**Additional: ~$25-45**

### With Siren/Strobe
Add:
- 1× 12V 2A power supply ($10)
- 1× Piezo siren 120dB ($15-30)
- 1× Strobe light ($10-20)
- 2× Solid state relay ($5 each)

**Additional: ~$45-70**

---

## Safety & Compliance

### Electrical Safety
- Don't exceed GPIO current limits (500mA total)
- Use proper gauge wire for current
- Fuse all 12V circuits
- Isolate high voltage from logic

### Building Codes
- Check local codes for alarm system installation
- Some jurisdictions require licensing
- Outdoor sensors may need weather rating
- Siren placement may be regulated

### Professional Installation
Consider hiring electrician for:
- Running wire through walls
- Connecting to existing alarm wiring
- Outdoor sensor installation
- Code compliance verification