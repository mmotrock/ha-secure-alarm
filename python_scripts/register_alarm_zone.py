"""
Python script to register zones with the Secure Alarm System
Place in: config/python_scripts/register_alarm_zone.py

Requires python_script integration to be enabled in configuration.yaml:
python_script:
"""

# Get the secure_alarm integration
domain = "secure_alarm"

# Get parameters from service call
entity_id = data.get('entity_id')
zone_type = data.get('zone_type', 'perimeter')
enabled_away = data.get('enabled_away', True)
enabled_home = data.get('enabled_home', True)

if not entity_id:
    logger.error("No entity_id provided to register_alarm_zone")
else:
    # Get the database from the integration
    integration_data = hass.data.get(domain, {})
    
    if integration_data:
        # Get the first config entry
        entry_id = list(integration_data.keys())[0]
        database = integration_data[entry_id].get('database')
        
        if database:
            # Get entity state to determine zone name
            state = hass.states.get(entity_id)
            zone_name = state.attributes.get('friendly_name', entity_id) if state else entity_id
            
            # Add zone to database
            success = database.add_zone(
                entity_id=entity_id,
                zone_name=zone_name,
                zone_type=zone_type,
                enabled_away=enabled_away,
                enabled_home=enabled_home
            )
            
            if success:
                logger.info(f"Registered zone: {zone_name} ({entity_id}) as {zone_type}")
            else:
                logger.error(f"Failed to register zone: {entity_id}")
        else:
            logger.error("Could not find database in secure_alarm integration")
    else:
        logger.error(f"Integration {domain} not found in hass.data")