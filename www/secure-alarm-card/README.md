# Secure Alarm Badge Card

Custom Lovelace card for the Secure Alarm System integration featuring a beautiful badge-style interface with tap-to-interact controls.

## Features

- 🎨 **Badge-Style Display** - Large, glowing badge shows alarm status at a glance
- 🎯 **Tap to Interact** - Simple tap to arm or disarm
- 🚪 **Entry Point Controls** - Lock/unlock doors and open/close garage from the card
- 🔋 **Battery Monitoring** - Visual battery levels for smart locks
- ⏰ **Smart Timestamps** - Shows when each entry point was last used
- 📱 **Mobile Responsive** - Perfect on any screen size
- ✨ **Smooth Animations** - Polished transitions and glow effects

## Installation

### Method 1: HACS (Future)
1. HACS → Frontend → Custom repositories
2. Add this repository
3. Search "Secure Alarm Badge Card"
4. Install

### Method 2: Manual
1. Copy `secure-alarm-card.js` to `/config/www/`
2. Add resource to Lovelace:
   - Settings → Dashboards → Resources
   - Click "+ Add Resource"
   - URL: `/local/secure-alarm-card.js`
   - Type: JavaScript Module
3. Clear browser cache (Ctrl+Shift+R)

## Basic Configuration

```yaml
type: custom:secure-alarm-card
entity: alarm_control_panel.secure_alarm
```

## Full Configuration

```yaml
type: custom:secure-alarm-card
entity: alarm_control_panel.secure_alarm
entry_points:
  - entity_id: lock.front_door
    name: Front Door
    type: door
    battery_entity: sensor.front_door_battery
  
  - entity_id: lock.back_door
    name: Back Door
    type: door
    battery_entity: sensor.back_door_battery
  
  - entity_id: cover.garage_door
    name: Garage Door
    type: garage
    # No battery for hardwired garage
  
  - entity_id: lock.side_door
    name: Side Door
    type: door
    battery_entity: sensor.side_door_battery
```

## Configuration Options

### Card Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `type` | string | Yes | - | Must be `custom:secure-alarm-card` |
| `entity` | string | Yes | - | Alarm control panel entity ID |
| `entry_points` | list | No | `[]` | List of entry point configurations |

### Entry Point Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `entity_id` | string | Yes | - | Lock or cover entity ID |
| `name` | string | Yes | - | Display name |
| `type` | string | Yes | - | `door` or `garage` |
| `battery_entity` | string | No | - | Battery sensor entity ID |

## Entry Point Types

### Door (`type: door`)
- Shows lock icon
- States: Locked / Unlocked
- Click to lock/unlock
- Green when locked, red when unlocked

### Garage (`type: garage`)
- Shows garage icon
- States: Closed / Open
- Click to open/close
- Green when closed, red when open

## States & Colors

The badge changes color based on alarm state:

| State | Color | Description |
|-------|-------|-------------|
| Disarmed | 🟢 Green | System off, ready to arm |
| Armed Home | 🔵 Blue | Perimeter armed |
| Armed Away | 🔴 Red | Fully armed |
| Arming | 🟡 Yellow | Exit delay in progress |
| Pending | 🟠 Orange | Entry delay active |
| Triggered | 🔴 Red (pulse) | Alarm sounding |

## User Interface

### Badge View (Default)
- Large circular badge with alarm icon
- Current state and description
- "Tap to arm/disarm" indicator
- Entry points list (if configured)
- Each entry point shows:
  - Icon (lock or garage)
  - Name
  - Battery level (if configured)
  - Current state
  - Time since last change

### When Disarmed - Tap Badge
Shows arm options:
- **Arm Home** button (blue)
- **Arm Away** button (red)
- Each shows description

### When Armed - Tap Badge
Shows PIN keypad:
- Number pad (0-9)
- Clear button (X)
- Enter button (✓)
- PIN dots display
- Digit counter

### Entry Point Controls
Click any entry point to toggle:
- Doors: Lock ↔ Unlock
- Garage: Close ↔ Open

## Styling

The card uses CSS variables from your Home Assistant theme:

```css
--card-background-color    /* Card background */
--primary-text-color       /* Main text */
--secondary-text-color     /* Subtitles */
--disabled-text-color      /* Hints */
```

Custom colors based on state:
- Green: Safe/Secure (disarmed, locked, closed)
- Red: Alert/Unsecured (armed away, unlocked, open)
- Blue: Home mode (armed home)
- Yellow: Transitioning (arming)
- Orange: Warning (entry delay)

## Examples

### Minimal Configuration
```yaml
type: custom:secure-alarm-card
entity: alarm_control_panel.secure_alarm
```

### With Entry Points
```yaml
type: custom:secure-alarm-card
entity: alarm_control_panel.secure_alarm
entry_points:
  - entity_id: lock.front_door
    name: Front Door
    type: door
    battery_entity: sensor.front_door_battery
```

### Multiple Cards
You can add the card to multiple dashboards:

```yaml
# Living Room Dashboard
type: custom:secure-alarm-card
entity: alarm_control_panel.secure_alarm
entry_points:
  - entity_id: lock.front_door
    name: Front Door
    type: door

# Bedroom Dashboard
type: custom:secure-alarm-card
entity: alarm_control_panel.secure_alarm
entry_points:
  - entity_id: lock.bedroom_door
    name: Bedroom Door
    type: door
```

## Troubleshooting

### Card Not Showing
1. **Check resource is added**
   - Settings → Dashboards → Resources
   - Verify `/local/secure-alarm-card.js` exists

2. **Clear browser cache**
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Or use private/incognito window

3. **Check browser console**
   - Press F12
   - Look for JavaScript errors
   - Common: "Failed to load module"

### Entry Points Not Working
1. **Verify entity IDs**
   - Developer Tools → States
   - Check entity exists and is available

2. **Test entity directly**
   ```yaml
   service: lock.lock
   target:
     entity_id: lock.front_door
   ```

3. **Check entity domain**
   - Doors must be `lock.*` entities
   - Garages must be `cover.*` entities

### Battery Not Showing
1. **Check battery entity exists**
   - Developer Tools → States
   - Search for battery sensor

2. **Verify entity returns number**
   - State should be numeric (e.g., "85")
   - Not string like "85%" or "Good"

### PIN Pad Not Responding
1. **Check alarm entity**
   - Must be `alarm_control_panel.*` entity
   - Must support arm/disarm services

2. **Verify services available**
   - Developer Tools → Services
   - Search for `secure_alarm.disarm`

## Advanced Customization

### Hiding Entry Points
Simply don't add `entry_points` to configuration.

### Custom Icons
Icons are determined by `type`:
- `door`: Lock icon
- `garage`: Garage/house icon

To use different types, modify the card JavaScript.

### Multiple Entry Point Lists
Create separate cards for different areas:

```yaml
# Main Floor
type: custom:secure-alarm-card
entity: alarm_control_panel.secure_alarm
entry_points:
  - entity_id: lock.front_door
    name: Front Door
    type: door

# Upstairs (separate card)
type: custom:secure-alarm-card
entity: alarm_control_panel.secure_alarm
entry_points:
  - entity_id: lock.bedroom_door
    name: Bedroom
    type: door
```

## Browser Compatibility

Tested and working on:
- ✅ Chrome/Edge 90+
- ✅ Firefox 90+
- ✅ Safari 14+
- ✅ Home Assistant iOS app
- ✅ Home Assistant Android app

## Performance

- Lightweight: ~15KB minified
- No external dependencies
- Updates only on state changes
- Smooth 60fps animations

## Accessibility

- Keyboard navigable
- ARIA labels for screen readers
- High contrast mode compatible
- Touch-friendly tap targets (44px minimum)

## Security Notes

- PINs are sent to backend for validation
- No PIN storage in browser
- Failed attempts tracked server-side
- Lockout enforced by integration

## Updates

Check for updates:
1. HACS → Frontend → Secure Alarm Badge Card
2. Click "Update" if available
3. Clear browser cache after update

## Support

- **Issues**: [GitHub Issues](https://github.com/mmotrock/ha-secure-alarm/issues)
- **Feature Requests**: [Discussions](https://github.com/mmotrock/ha-secure-alarm/discussions)
- **Community**: [Home Assistant Forum](https://community.home-assistant.io/)

## Contributing

Pull requests welcome! See [CONTRIBUTING.md](../../CONTRIBUTING.md).

## License

MIT License - see [LICENSE](../../LICENSE)

---

**Part of the Secure Alarm System integration**