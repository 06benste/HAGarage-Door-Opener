"""Constants for the Garage Door Opener integration."""
from __future__ import annotations

DOMAIN = "garage_door_opener"

# Configuration keys
CONF_CLOSED_SENSOR = "closed_sensor"
CONF_CLOSED_SENSOR_STATE = "closed_sensor_state"
CONF_OPEN_SENSOR = "open_sensor"
CONF_OPEN_SENSOR_STATE = "open_sensor_state"
CONF_OPEN_RELAY = "open_relay"
CONF_CLOSE_RELAY = "close_relay"
CONF_OPEN_TIME = "open_time"
CONF_CLOSE_TIME = "close_time"
CONF_COVER_NAME = "cover_name"
CONF_ENABLE_STUCK_NOTIFICATION = "enable_stuck_notification"

# Defaults
DEFAULT_COVER_NAME = "Garage Door"
DEFAULT_CLOSED_SENSOR_STATE = "off"
DEFAULT_OPEN_SENSOR_STATE = "off"
DEFAULT_OPEN_TIME = 20
DEFAULT_CLOSE_TIME = 25
DEFAULT_ENABLE_STUCK_NOTIFICATION = True

