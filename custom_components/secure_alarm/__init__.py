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
from homeassistant.const import (
    STATE_ALARM_DISARMED,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_PENDING,
    STATE_ALARM_TRIGGERED,
    STATE_ALARM_ARMING,
)

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
    await async_setup_services(hass, coordinator)
    
    _LOGGER.info("Secure Alarm System initialized successfully")
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

async def async_setup_services(hass: HomeAssistant, coordinator: AlarmCoordinator) -> None:
    """Register services for the alarm system."""
    
    async def handle_arm_away(call: ServiceCall) -> None:
        """Handle arm away service call."""
        pin = call.data.get("pin")
        user_code = call.data.get("code")  # Optional user identifier
        
        result = await coordinator.arm_away(pin, user_code)
        
        if not result["success"]:
            _LOGGER.warning(f"Arm away failed: {result['message']}")
    
    async def handle_arm_home(call: ServiceCall) -> None:
        """Handle arm home service call."""
        pin = call.data.get("pin")
        user_code = call.data.get("code")
        
        result = await coordinator.arm_home(pin, user_code)
        
        if not result["success"]:
            _LOGGER.warning(f"Arm home failed: {result['message']}")
    
    async def handle_disarm(call: ServiceCall) -> None:
        """Handle disarm service call."""
        pin = call.data.get("pin")
        user_code = call.data.get("code")
        
        result = await coordinator.disarm(pin, user_code)
        
        if not result["success"]:
            _LOGGER.warning(f"Disarm failed: {result['message']}")
    
    async def handle_add_user(call: ServiceCall) -> None:
        """Handle add user service call."""
        name = call.data.get("name")
        pin = call.data.get("pin")
        admin_pin = call.data.get("admin_pin")
        is_admin = call.data.get("is_admin", False)
        is_duress = call.data.get("is_duress", False)
        
        result = await coordinator.add_user(name, pin, admin_pin, is_admin, is_duress)
        
        if result["success"]:
            _LOGGER.info(f"User {name} added successfully")
        else:
            _LOGGER.warning(f"Add user failed: {result['message']}")
    
    async def handle_remove_user(call: ServiceCall) -> None:
        """Handle remove user service call."""
        user_id = call.data.get("user_id")
        admin_pin = call.data.get("admin_pin")
        
        result = await coordinator.remove_user(user_id, admin_pin)
        
        if result["success"]:
            _LOGGER.info(f"User {user_id} removed successfully")
        else:
            _LOGGER.warning(f"Remove user failed: {result['message']}")
    
    async def handle_bypass_zone(call: ServiceCall) -> None:
        """Handle bypass zone service call."""
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
    
    # Register services
    hass.services.async_register(
        DOMAIN,
        "arm_away",
        handle_arm_away,
        schema=vol.Schema({
            vol.Required("pin"): cv.string,
            vol.Optional("code"): cv.string,
        })
    )
    
    hass.services.async_register(
        DOMAIN,
        "arm_home",
        handle_arm_home,
        schema=vol.Schema({
            vol.Required("pin"): cv.string,
            vol.Optional("code"): cv.string,
        })
    )
    
    hass.services.async_register(
        DOMAIN,
        "disarm",
        handle_disarm,
        schema=vol.Schema({
            vol.Required("pin"): cv.string,
            vol.Optional("code"): cv.string,
        })
    )
    
    hass.services.async_register(
        DOMAIN,
        "add_user",
        handle_add_user,
        schema=vol.Schema({
            vol.Required("name"): cv.string,
            vol.Required("pin"): cv.string,
            vol.Required("admin_pin"): cv.string,
            vol.Optional("is_admin", default=False): cv.boolean,
            vol.Optional("is_duress", default=False): cv.boolean,
        })
    )
    
    hass.services.async_register(
        DOMAIN,
        "remove_user",
        handle_remove_user,
        schema=vol.Schema({
            vol.Required("user_id"): cv.positive_int,
            vol.Required("admin_pin"): cv.string,
        })
    )
    
    hass.services.async_register(
        DOMAIN,
        "bypass_zone",
        handle_bypass_zone,
        schema=vol.Schema({
            vol.Required("zone_entity_id"): cv.entity_id,
            vol.Required("pin"): cv.string,
            vol.Optional("bypass", default=True): cv.boolean,
        })
    )
    
    hass.services.async_register(
        DOMAIN,
        "update_config",
        handle_update_config,
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