"""
Secure Alarm System Integration for Home Assistant
Custom security system with dedicated authentication and database
"""
import logging
import asyncio
from datetime import timedelta
from typing import Optional

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.service import async_register_admin_service

from .const import DOMAIN, CONF_DB_PATH
from .database import AlarmDatabase
from .alarm_coordinator import AlarmCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["alarm_control_panel", "sensor", "binary_sensor"]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Secure Alarm System component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Secure Alarm System from a config entry."""
    
    # Initialize database
    db_path = hass.config.path(f"{DOMAIN}.db")
    database = AlarmDatabase(db_path)
    
    # Ensure admin user exists
    await hass.async_add_executor_job(_ensure_admin_user, database, entry)
    
    # Initialize coordinator
    coordinator = AlarmCoordinator(hass, database)
    
    # Store in hass.data
    hass.data[DOMAIN][entry.entry_id] = {
        "database": database,
        "coordinator": coordinator,
    }
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services
    await async_setup_services(hass)
    
    _LOGGER.info("Secure Alarm System initialized successfully")
    
    return True

def _ensure_admin_user(database: AlarmDatabase, entry: ConfigEntry) -> None:
    """Ensure admin user exists from config entry."""
    try:
        users = database.get_users()
        _LOGGER.info(f"_ensure_admin_user: Found {len(users)} existing users")
        
        if len(users) == 0:
            admin_name = entry.data.get("admin_name", "Admin")
            admin_pin = entry.data.get("admin_pin", "123456")
            
            _LOGGER.info(f"Creating initial admin user: {admin_name}")
            
            user_id = database.add_user(
                name=admin_name,
                pin=admin_pin,
                is_admin=True,
                is_duress=False
            )
            
            if user_id:
                _LOGGER.info(f"✓ Admin user '{admin_name}' created with ID {user_id}")
            else:
                _LOGGER.error(f"✗ Failed to create admin user!")
        else:
            _LOGGER.info(f"Skipping admin creation - {len(users)} users exist")
    except Exception as e:
        _LOGGER.error(f"Error in _ensure_admin_user: {e}", exc_info=True)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

async def async_setup_services(hass: HomeAssistant) -> None:
    """Register services for the alarm system."""
    
    def get_data():
        """Get database and coordinator."""
        entry_id = list(hass.data[DOMAIN].keys())[0]
        return hass.data[DOMAIN][entry_id]
    
    async def handle_arm_away(call: ServiceCall) -> None:
        """Handle arm away service call."""
        data = get_data()
        coordinator = data["coordinator"]
        
        pin = call.data.get("pin")
        user_code = call.data.get("code")
        
        result = await coordinator.arm_away(pin, user_code)
        
        if not result["success"]:
            _LOGGER.warning(f"Arm away failed: {result['message']}")
    
    async def handle_arm_home(call: ServiceCall) -> None:
        """Handle arm home service call."""
        data = get_data()
        coordinator = data["coordinator"]
        
        pin = call.data.get("pin")
        user_code = call.data.get("code")
        
        result = await coordinator.arm_home(pin, user_code)
        
        if not result["success"]:
            _LOGGER.warning(f"Arm home failed: {result['message']}")
    
    async def handle_disarm(call: ServiceCall) -> None:
        """Handle disarm service call."""
        data = get_data()
        coordinator = data["coordinator"]
        
        pin = call.data.get("pin")
        user_code = call.data.get("code")
        
        result = await coordinator.disarm(pin, user_code)
        
        if not result["success"]:
            _LOGGER.warning(f"Disarm failed: {result['message']}")
    
    async def handle_add_user(call: ServiceCall) -> None:
        """Handle add user service call."""
        data = get_data()
        coordinator = data["coordinator"]
        
        name = call.data.get("name")
        pin = call.data.get("pin")
        admin_pin = call.data.get("admin_pin")
        is_admin = call.data.get("is_admin", False)
        is_duress = call.data.get("is_duress", False)
        phone = call.data.get("phone")
        email = call.data.get("email")
        has_separate_lock_pin = call.data.get("has_separate_lock_pin", False)
        lock_pin = call.data.get("lock_pin")
        
        _LOGGER.info(f"Service: add_user called for {name}")
        
        result = await coordinator.add_user(
            name, pin, admin_pin, is_admin, is_duress,
            phone, email, has_separate_lock_pin, lock_pin
        )
        
        if result["success"]:
            _LOGGER.info(f"✓ User {name} added successfully")
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "message": f"User '{name}' added successfully",
                    "title": "User Added",
                },
            )
        else:
            _LOGGER.warning(f"✗ Add user failed: {result['message']}")
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "message": f"Failed to add user: {result['message']}",
                    "title": "Add User Failed",
                },
            )
    
    async def handle_remove_user(call: ServiceCall) -> None:
        """Handle remove user service call."""
        data = get_data()
        coordinator = data["coordinator"]
        
        user_id = call.data.get("user_id")
        admin_pin = call.data.get("admin_pin")
        
        result = await coordinator.remove_user(user_id, admin_pin)
        
        if result["success"]:
            _LOGGER.info(f"User {user_id} removed successfully")
        else:
            _LOGGER.warning(f"Remove user failed: {result['message']}")
    
    async def handle_get_users(call: ServiceCall) -> None:
        """Handle get users service call."""
        data = get_data()
        database = data["database"]
        
        users = await hass.async_add_executor_job(database.get_users)
        
        _LOGGER.info(f"Retrieved {len(users)} users")
        
        # Fire event with users
        hass.bus.async_fire(f"{DOMAIN}_users_response", {
            "users": users
        })
    
    async def handle_update_user(call: ServiceCall) -> None:
        """Handle update user service call."""
        data = get_data()
        coordinator = data["coordinator"]
        
        user_id = call.data.get("user_id")
        name = call.data.get("name")
        pin = call.data.get("pin")
        phone = call.data.get("phone")
        email = call.data.get("email")
        is_admin = call.data.get("is_admin", False)
        has_separate_lock_pin = call.data.get("has_separate_lock_pin", False)
        lock_pin = call.data.get("lock_pin")
        admin_pin = call.data.get("admin_pin")
        
        result = await coordinator.update_user(
            user_id, name, pin, phone, email, is_admin,
            has_separate_lock_pin, lock_pin, admin_pin
        )
        
        if result["success"]:
            _LOGGER.info(f"User {user_id} updated successfully")
        else:
            _LOGGER.warning(f"Update user failed: {result['message']}")
    
    async def handle_bypass_zone(call: ServiceCall) -> None:
        """Handle bypass zone service call."""
        data = get_data()
        coordinator = data["coordinator"]
        
        zone_entity_id = call.data.get("zone_entity_id")
        pin = call.data.get("pin")
        bypass = call.data.get("bypass", True)
        
        result = await coordinator.bypass_zone(zone_entity_id, pin, bypass)
        
        if result["success"]:
            _LOGGER.info(f"Zone {zone_entity_id} bypass set to {bypass}")
        else:
            _LOGGER.warning(f"Bypass zone failed: {result['message']}")
    
    async def handle_update_config(call: ServiceCall) -> None:
        """Handle update configuration service call."""
        data = get_data()
        coordinator = data["coordinator"]
        
        admin_pin = call.data.get("admin_pin")
        config_updates = {
            k: v for k, v in call.data.items()
            if k not in ["admin_pin"]
        }
        
        result = await coordinator.update_config(admin_pin, config_updates)
        
        if result["success"]:
            _LOGGER.info("Configuration updated successfully")
        else:
            _LOGGER.warning(f"Update config failed: {result['message']}")
    
    async def handle_authenticate_admin(call: ServiceCall) -> None:
        """Authenticate admin PIN and fire result event."""
        data = get_data()
        database = data["database"]
        
        pin = call.data.get("pin")
        
        _LOGGER.info(f"Admin authentication attempt with PIN length {len(pin)}")
        
        # Authenticate the user directly
        user = await hass.async_add_executor_job(
            database.authenticate_user,
            pin,
            None
        )
        
        success = user is not None and user.get('is_admin', False)
        
        _LOGGER.info(f"Admin auth result: success={success}, user={user.get('name') if user else None}, is_admin={user.get('is_admin') if user else False}")
        
        # Fire event with result
        hass.bus.async_fire(f"{DOMAIN}_auth_result", {
            "success": success,
            "is_admin": user.get('is_admin', False) if user else False,
            "user_name": user.get('name') if user else None
        })
    
    
    async def handle_bootstrap_admin(call: ServiceCall) -> None:
        """Bootstrap admin user - emergency use only."""
        data = get_data()
        database = data["database"]
        
        users = await hass.async_add_executor_job(database.get_users)
        
        admin_name = call.data.get("name", "Admin")
        admin_pin = call.data.get("pin", "123456")
        
        _LOGGER.info(f"Bootstrap admin called - {len(users)} users exist")
        
        user_id = await hass.async_add_executor_job(
            database.add_user,
            admin_name,
            admin_pin,
            True,  # is_admin
            False  # is_duress
        )
        
        if user_id:
            _LOGGER.info(f"✓ Admin '{admin_name}' bootstrapped with ID {user_id}")
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "message": f"Admin user '{admin_name}' created with ID {user_id}",
                    "title": "Bootstrap Success",
                },
            )
        else:
            _LOGGER.error("✗ Bootstrap admin failed")
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "message": "Failed to create admin user",
                    "title": "Bootstrap Failed",
                },
            )

    async def handle_toggle_user_enabled(call: ServiceCall) -> None:
        """Handle toggle user enabled service call."""
        data = get_data()
        database = data["database"]
        
        user_id = call.data.get("user_id")
        enabled = call.data.get("enabled")
        admin_pin = call.data.get("admin_pin")
        
        # Verify admin PIN
        user = await hass.async_add_executor_job(
            database.authenticate_user,
            admin_pin,
            None
        )
        
        if not user or not user.get('is_admin', False):
            _LOGGER.warning("Toggle user enabled failed: Admin authentication required")
            return
        
        success = await hass.async_add_executor_job(
            database.update_user,
            user_id,
            None,  # name
            None,  # pin
            None,  # is_admin
            None,  # phone
            None,  # email
            None,  # has_separate_lock_pin
            None   # lock_pin
        )
        
        # Need to update enabled field directly
        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                UPDATE {TABLE_USERS}
                SET enabled = ?
                WHERE id = ?
            ''', (int(enabled), user_id))
            conn.commit()
            success = True
        except Exception as e:
            _LOGGER.error(f"Error toggling user enabled: {e}")
            success = False
        finally:
            conn.close()
        
        if success:
            _LOGGER.info(f"User {user_id} enabled status set to {enabled}")

    async def handle_set_user_lock_access(call: ServiceCall) -> None:
        """Handle set user lock access service call."""
        data = get_data()
        database = data["database"]
        
        user_id = call.data.get("user_id")
        lock_entity_id = call.data.get("lock_entity_id")
        can_access = call.data.get("can_access")
        admin_pin = call.data.get("admin_pin")
        
        # Verify admin PIN
        user = await hass.async_add_executor_job(
            database.authenticate_user,
            admin_pin,
            None
        )
        
        if not user or not user.get('is_admin', False):
            _LOGGER.warning("Set user lock access failed: Admin authentication required")
            return
        
        success = await hass.async_add_executor_job(
            database.set_user_lock_access,
            user_id,
            lock_entity_id,
            can_access
        )
        
        if success:
            _LOGGER.info(f"User {user_id} lock access updated for {lock_entity_id}")
    
    # Register all services
    hass.services.async_register(
        DOMAIN, "arm_away", handle_arm_away,
        schema=vol.Schema({
            vol.Required("pin"): cv.string,
            vol.Optional("code"): cv.string,
        })
    )
    
    hass.services.async_register(
        DOMAIN, "arm_home", handle_arm_home,
        schema=vol.Schema({
            vol.Required("pin"): cv.string,
            vol.Optional("code"): cv.string,
        })
    )
    
    hass.services.async_register(
        DOMAIN, "disarm", handle_disarm,
        schema=vol.Schema({
            vol.Required("pin"): cv.string,
            vol.Optional("code"): cv.string,
        })
    )
    
    hass.services.async_register(
        DOMAIN, "add_user", handle_add_user,
        schema=vol.Schema({
            vol.Required("name"): cv.string,
            vol.Required("pin"): cv.string,
            vol.Required("admin_pin"): cv.string,
            vol.Optional("is_admin", default=False): cv.boolean,
            vol.Optional("is_duress", default=False): cv.boolean,
            vol.Optional("phone"): cv.string,
            vol.Optional("email"): cv.string,
            vol.Optional("has_separate_lock_pin", default=False): cv.boolean,
            vol.Optional("lock_pin"): cv.string,
        })
    )
    
    hass.services.async_register(
        DOMAIN, "remove_user", handle_remove_user,
        schema=vol.Schema({
            vol.Required("user_id"): cv.positive_int,
            vol.Required("admin_pin"): cv.string,
        })
    )
    
    hass.services.async_register(
        DOMAIN, "get_users", handle_get_users,
        schema=vol.Schema({})
    )
    
    hass.services.async_register(
        DOMAIN, "update_user", handle_update_user,
        schema=vol.Schema({
            vol.Required("user_id"): cv.positive_int,
            vol.Optional("name"): cv.string,
            vol.Optional("pin"): cv.string,
            vol.Optional("phone"): cv.string,
            vol.Optional("email"): cv.string,
            vol.Optional("is_admin"): cv.boolean,
            vol.Optional("has_separate_lock_pin"): cv.boolean,
            vol.Optional("lock_pin"): cv.string,
            vol.Required("admin_pin"): cv.string,
        })
    )
    
    hass.services.async_register(
        DOMAIN, "bypass_zone", handle_bypass_zone,
        schema=vol.Schema({
            vol.Required("zone_entity_id"): cv.entity_id,
            vol.Required("pin"): cv.string,
            vol.Optional("bypass", default=True): cv.boolean,
        })
    )
    
    hass.services.async_register(
        DOMAIN, "update_config", handle_update_config,
        schema=vol.Schema({
            vol.Required("admin_pin"): cv.string,
            vol.Optional("entry_delay"): cv.positive_int,
            vol.Optional("exit_delay"): cv.positive_int,
            vol.Optional("alarm_duration"): cv.positive_int,
            vol.Optional("trigger_doors"): cv.string,
            vol.Optional("notification_mobile"): cv.boolean,
            vol.Optional("notification_sms"): cv.boolean,
            vol.Optional("sms_numbers"): cv.string,
        })
    )
    
    hass.services.async_register(
        DOMAIN, "bootstrap_admin", handle_bootstrap_admin,
        schema=vol.Schema({
            vol.Optional("name", default="Admin"): cv.string,
            vol.Optional("pin", default="123456"): cv.string,
        })
    )
    
    hass.services.async_register(
        DOMAIN, "authenticate_admin", handle_authenticate_admin,
        schema=vol.Schema({
            vol.Required("pin"): cv.string,
        })
    )

    hass.services.async_register(
        DOMAIN, "toggle_user_enabled", handle_toggle_user_enabled,
        schema=vol.Schema({
            vol.Required("user_id"): cv.positive_int,
            vol.Required("enabled"): cv.boolean,
            vol.Required("admin_pin"): cv.string,
        })
    )

    hass.services.async_register(
        DOMAIN, "set_user_lock_access", handle_set_user_lock_access,
        schema=vol.Schema({
            vol.Required("user_id"): cv.positive_int,
            vol.Required("lock_entity_id"): cv.entity_id,
            vol.Required("can_access"): cv.boolean,
            vol.Required("admin_pin"): cv.string,
        })
    )
    
    _LOGGER.info("All services registered successfully")