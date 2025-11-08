"""Alarm coordinator for managing alarm state and logic."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Callable

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_point_in_time, async_call_later
from homeassistant.util import dt as dt_util
from homeassistant.const import (
    STATE_ALARM_DISARMED,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_PENDING,
    STATE_ALARM_TRIGGERED,
)

from .const import (
    DOMAIN,
    EVENT_ALARM_ARMED,
    EVENT_ALARM_DISARMED,
    EVENT_ALARM_TRIGGERED,
    EVENT_ALARM_DURESS,
    STATE_ARMING,
    ZONE_TYPE_ENTRY,
)
from .database import AlarmDatabase

_LOGGER = logging.getLogger(__name__)

class AlarmCoordinator:
    """Coordinator for managing alarm system state and logic."""
    
    def __init__(self, hass: HomeAssistant, database: AlarmDatabase):
        """Initialize the coordinator."""
        self.hass = hass
        self.database = database
        self._state = STATE_ALARM_DISARMED
        self._previous_state = None
        self._triggered_by = None
        self._changed_by = None
        self._entry_timer = None
        self._exit_timer = None
        self._alarm_timer = None
        self._listeners: List[Callable] = []
        self._bypassed_zones: set = set()
        
    @property
    def state(self) -> str:
        """Return current alarm state."""
        return self._state
    
    @property
    def changed_by(self) -> Optional[str]:
        """Return who last changed the alarm state."""
        return self._changed_by
    
    @property
    def triggered_by(self) -> Optional[str]:
        """Return what triggered the alarm."""
        return self._triggered_by
    
    def add_listener(self, listener: Callable) -> None:
        """Add a state change listener."""
        self._listeners.append(listener)
    
    def remove_listener(self, listener: Callable) -> None:
        """Remove a state change listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    async def _notify_listeners(self) -> None:
        """Notify all listeners of state change."""
        for listener in self._listeners:
            await listener()
    
    async def _set_state(self, new_state: str, changed_by: Optional[str] = None) -> None:
        """Set alarm state and notify listeners."""
        old_state = self._state
        self._previous_state = old_state
        self._state = new_state
        
        if changed_by:
            self._changed_by = changed_by
        
        # Log state change
        await self.hass.async_add_executor_job(
            self.database.log_event,
            "state_change",
            None,
            changed_by,
            old_state,
            new_state
        )
        
        # Fire event
        self.hass.bus.async_fire(f"{DOMAIN}_state_changed", {
            "state": new_state,
            "previous_state": old_state,
            "changed_by": changed_by,
        })
        
        await self._notify_listeners()
        
        _LOGGER.info(f"Alarm state changed: {old_state} -> {new_state}")
    
    async def _authenticate(self, pin: str, user_code: Optional[str] = None) -> Optional[Dict]:
        """Authenticate user with PIN."""
        user = await self.hass.async_add_executor_job(
            self.database.authenticate_user,
            pin,
            user_code
        )
        
        if user:
            # Clear failed attempts on successful auth
            await self.hass.async_add_executor_job(
                self.database.clear_failed_attempts
            )
            
            # Check for duress code
            if user['is_duress']:
                _LOGGER.warning(f"DURESS CODE USED by {user['name']}")
                self.hass.bus.async_fire(EVENT_ALARM_DURESS, {
                    "user_name": user['name'],
                    "user_id": user['id'],
                    "timestamp": datetime.now().isoformat(),
                })
                
                # Send silent notification
                await self._send_duress_notification(user['name'])
        
        return user
    
    async def arm_away(self, pin: str, user_code: Optional[str] = None) -> Dict[str, Any]:
        """Arm the system in away mode."""
        user = await self._authenticate(pin, user_code)
        
        if not user:
            return {"success": False, "message": "Invalid PIN"}
        
        if self._state in [STATE_ALARM_ARMED_AWAY, STATE_ARMING]:
            return {"success": False, "message": "System already arming or armed"}
        
        # Start exit delay
        config = await self.hass.async_add_executor_job(self.database.get_config)
        exit_delay = config.get('exit_delay', 60)
        
        await self._set_state(STATE_ARMING, user['name'])
        
        # Cancel any existing timers
        self._cancel_timers()
        
        # Set exit timer
        self._exit_timer = async_call_later(
            self.hass,
            exit_delay,
            self._complete_arming_away
        )
        
        # Execute arming actions (lock doors, close garage)
        await self._execute_arming_actions()
        
        _LOGGER.info(f"Arming away initiated by {user['name']}, {exit_delay}s delay")
        
        return {
            "success": True,
            "message": f"Arming away in {exit_delay} seconds",
            "delay": exit_delay
        }
    
    async def arm_home(self, pin: str, user_code: Optional[str] = None) -> Dict[str, Any]:
        """Arm the system in home mode."""
        user = await self._authenticate(pin, user_code)
        
        if not user:
            return {"success": False, "message": "Invalid PIN"}
        
        if self._state == STATE_ALARM_ARMED_HOME:
            return {"success": False, "message": "System already armed home"}
        
        # Cancel any existing timers
        self._cancel_timers()
        
        # Arm home has no exit delay (you're already home)
        await self._set_state(STATE_ALARM_ARMED_HOME, user['name'])
        
        # Fire armed event
        self.hass.bus.async_fire(EVENT_ALARM_ARMED, {
            "mode": "armed_home",
            "changed_by": user['name'],
        })
        
        _LOGGER.info(f"Armed home by {user['name']}")
        
        return {"success": True, "message": "Armed home"}
    
    async def disarm(self, pin: str, user_code: Optional[str] = None) -> Dict[str, Any]:
        """Disarm the system."""
        user = await self._authenticate(pin, user_code)
        
        if not user:
            return {"success": False, "message": "Invalid PIN"}
        
        # Cancel all timers
        self._cancel_timers()
        
        # If duress code, appear to disarm but alert
        if user['is_duress']:
            await self._set_state(STATE_ALARM_DISARMED, user['name'])
            # Duress notification already sent in _authenticate
        else:
            await self._set_state(STATE_ALARM_DISARMED, user['name'])
        
        self._triggered_by = None
        self._bypassed_zones.clear()
        
        # Fire disarmed event
        self.hass.bus.async_fire(EVENT_ALARM_DISARMED, {
            "changed_by": user['name'],
        })
        
        _LOGGER.info(f"Disarmed by {user['name']}")
        
        return {"success": True, "message": "Disarmed"}
    
    async def _complete_arming_away(self, _now: datetime = None) -> None:
        """Complete the arming process after exit delay."""
        await self._set_state(STATE_ALARM_ARMED_AWAY, self._changed_by)
        
        # Fire armed event
        self.hass.bus.async_fire(EVENT_ALARM_ARMED, {
            "mode": "armed_away",
            "changed_by": self._changed_by,
        })
        
        _LOGGER.info("Armed away complete")
    
    async def zone_triggered(self, zone_entity_id: str, zone_name: str) -> None:
        """Handle zone trigger."""
        # Ignore if disarmed or already triggered
        if self._state in [STATE_ALARM_DISARMED, STATE_ALARM_TRIGGERED]:
            return
        
        # Check if zone is bypassed
        if zone_entity_id in self._bypassed_zones:
            _LOGGER.info(f"Zone {zone_name} triggered but bypassed")
            return
        
        # Get zone info
        zones = await self.hass.async_add_executor_job(
            self.database.get_zones,
            self._state
        )
        
        zone_info = next((z for z in zones if z['entity_id'] == zone_entity_id), None)
        
        if not zone_info:
            _LOGGER.warning(f"Unknown zone triggered: {zone_entity_id}")
            return
        
        # If it's an entry zone and we're armed, start entry delay
        if zone_info['zone_type'] == ZONE_TYPE_ENTRY and self._state in [STATE_ALARM_ARMED_AWAY, STATE_ALARM_ARMED_HOME]:
            if self._state != STATE_ALARM_PENDING:
                await self._start_entry_delay(zone_entity_id, zone_name)
        else:
            # Instant trigger for non-entry zones
            await self._trigger_alarm(zone_entity_id, zone_name)
    
    async def _start_entry_delay(self, zone_entity_id: str, zone_name: str) -> None:
        """Start entry delay timer."""
        config = await self.hass.async_add_executor_job(self.database.get_config)
        entry_delay = config.get('entry_delay', 30)
        
        await self._set_state(STATE_ALARM_PENDING, self._changed_by)
        self._triggered_by = zone_name
        
        # Cancel existing entry timer if any
        if self._entry_timer:
            self._entry_timer()
        
        # Set new entry timer
        self._entry_timer = async_call_later(
            self.hass,
            entry_delay,
            lambda _: asyncio.create_task(self._trigger_alarm(zone_entity_id, zone_name))
        )
        
        _LOGGER.warning(f"Entry delay started: {zone_name}, {entry_delay}s to disarm")
    
    async def _trigger_alarm(self, zone_entity_id: str, zone_name: str) -> None:
        """Trigger the alarm."""
        if self._state == STATE_ALARM_TRIGGERED:
            return
        
        self._triggered_by = zone_name
        await self._set_state(STATE_ALARM_TRIGGERED, self._changed_by)
        
        # Log trigger
        await self.hass.async_add_executor_job(
            self.database.log_event,
            "alarm_triggered",
            None,
            None,
            self._previous_state,
            STATE_ALARM_TRIGGERED,
            zone_entity_id
        )
        
        # Fire triggered event
        self.hass.bus.async_fire(EVENT_ALARM_TRIGGERED, {
            "zone": zone_name,
            "zone_entity_id": zone_entity_id,
        })
        
        # Send notifications
        await self._send_alarm_notification(zone_name)
        
        # Set alarm duration timer
        config = await self.hass.async_add_executor_job(self.database.get_config)
        alarm_duration = config.get('alarm_duration', 300)
        
        self._alarm_timer = async_call_later(
            self.hass,
            alarm_duration,
            self._alarm_timeout
        )
        
        _LOGGER.critical(f"ALARM TRIGGERED by {zone_name}")
    
    async def _alarm_timeout(self, _now: datetime = None) -> None:
        """Handle alarm timeout (stays triggered but stops siren)."""
        _LOGGER.info("Alarm timeout reached")
        # You could implement siren shutoff here
    
    def _cancel_timers(self) -> None:
        """Cancel all active timers."""
        if self._entry_timer:
            self._entry_timer()
            self._entry_timer = None
        
        if self._exit_timer:
            self._exit_timer()
            self._exit_timer = None
        
        if self._alarm_timer:
            self._alarm_timer()
            self._alarm_timer = None
    
    async def _execute_arming_actions(self) -> None:
        """Execute actions when arming (lock doors, close garage)."""
        # Call service to lock all doors
        await self.hass.services.async_call(
            'lock',
            'lock',
            {'entity_id': 'all'},
            blocking=False
        )
        
        # Call service to close garage doors
        await self.hass.services.async_call(
            'cover',
            'close_cover',
            {'entity_id': 'all'},
            blocking=False
        )
        
        _LOGGER.info("Arming actions executed (doors locked, garage closed)")
    
    async def _send_alarm_notification(self, zone_name: str) -> None:
        """Send alarm trigger notifications."""
        config = await self.hass.async_add_executor_job(self.database.get_config)
        
        message = f"🚨 ALARM TRIGGERED: {zone_name}"
        
        # Mobile notification
        if config.get('notification_mobile', True):
            await self.hass.services.async_call(
                'notify',
                'mobile_app_all',
                {
                    'message': message,
                    'title': 'Security Alert',
                    'data': {
                        'priority': 'high',
                        'ttl': 0,
                        'channel': 'alarm',
                    }
                },
                blocking=False
            )
        
        # SMS notification
        if config.get('notification_sms', False):
            sms_numbers = config.get('sms_numbers', '')
            if sms_numbers:
                for number in sms_numbers.split(','):
                    await self._send_sms(number.strip(), message)
    
    async def _send_duress_notification(self, user_name: str) -> None:
        """Send silent duress code notification."""
        message = f"⚠️ DURESS CODE USED by {user_name}"
        
        await self.hass.services.async_call(
            'notify',
            'mobile_app_all',
            {
                'message': message,
                'title': 'Security Alert - Silent',
                'data': {
                    'priority': 'high',
                    'ttl': 0,
                    'channel': 'duress',
                }
            },
            blocking=False
        )
    
    async def _send_sms(self, phone_number: str, message: str) -> None:
        """Send SMS notification."""
        # This requires SMS integration to be set up (Twilio, etc.)
        try:
            await self.hass.services.async_call(
                'notify',
                'sms',
                {
                    'target': phone_number,
                    'message': message,
                },
                blocking=False
            )
        except Exception as e:
            _LOGGER.error(f"Failed to send SMS: {e}")
    
    async def add_user(self, name: str, pin: str, admin_pin: str,
                      is_admin: bool = False, is_duress: bool = False) -> Dict[str, Any]:
        """Add a new user."""
        # Verify admin PIN
        admin_user = await self._authenticate(admin_pin)
        
        if not admin_user or not admin_user['is_admin']:
            return {"success": False, "message": "Admin authentication required"}
        
        # Validate PIN length
        if len(pin) < 6 or len(pin) > 8:
            return {"success": False, "message": "PIN must be 6-8 characters"}
        
        # Add user
        user_id = await self.hass.async_add_executor_job(
            self.database.add_user,
            name,
            pin,
            is_admin,
            is_duress
        )
        
        if user_id:
            return {"success": True, "message": f"User {name} added", "user_id": user_id}
        else:
            return {"success": False, "message": "Failed to add user"}
    
    async def remove_user(self, user_id: int, admin_pin: str) -> Dict[str, Any]:
        """Remove a user."""
        # Verify admin PIN
        admin_user = await self._authenticate(admin_pin)
        
        if not admin_user or not admin_user['is_admin']:
            return {"success": False, "message": "Admin authentication required"}
        
        success = await self.hass.async_add_executor_job(
            self.database.remove_user,
            user_id
        )
        
        if success:
            return {"success": True, "message": "User removed"}
        else:
            return {"success": False, "message": "Failed to remove user"}
    
    async def bypass_zone(self, zone_entity_id: str, pin: str,
                         bypass: bool = True) -> Dict[str, Any]:
        """Bypass or unbypass a zone."""
        user = await self._authenticate(pin)
        
        if not user:
            return {"success": False, "message": "Invalid PIN"}
        
        if bypass:
            self._bypassed_zones.add(zone_entity_id)
        else:
            self._bypassed_zones.discard(zone_entity_id)
        
        success = await self.hass.async_add_executor_job(
            self.database.set_zone_bypass,
            zone_entity_id,
            bypass
        )
        
        if success:
            return {"success": True, "message": f"Zone {'bypassed' if bypass else 'unbypassed'}"}
        else:
            return {"success": False, "message": "Failed to update zone"}
    
    async def update_config(self, admin_pin: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update alarm configuration."""
        admin_user = await self._authenticate(admin_pin)
        
        if not admin_user or not admin_user['is_admin']:
            return {"success": False, "message": "Admin authentication required"}
        
        success = await self.hass.async_add_executor_job(
            self.database.update_config,
            updates
        )
        
        if success:
            return {"success": True, "message": "Configuration updated"}
        else:
            return {"success": False, "message": "Failed to update configuration"}