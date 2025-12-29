"""Cover platform for Garage Door Opener integration."""
from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CONF_CLOSED_SENSOR,
    CONF_CLOSED_SENSOR_STATE,
    CONF_CLOSE_RELAY,
    CONF_CLOSE_TIME,
    CONF_COVER_NAME,
    CONF_ENABLE_STUCK_NOTIFICATION,
    CONF_OPEN_RELAY,
    CONF_OPEN_SENSOR,
    CONF_OPEN_SENSOR_STATE,
    CONF_OPEN_TIME,
    DOMAIN,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the cover platform."""
    config = entry.data
    async_add_entities([GarageDoorCoverEntity(hass, config, entry.entry_id)])


class GarageDoorCoverEntity(CoverEntity, RestoreEntity):
    """Representation of a Garage Door Cover."""

    _attr_device_class = CoverDeviceClass.GARAGE
    _attr_supported_features = (
        CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
    )

    def __init__(self, hass: HomeAssistant, config: dict[str, Any], entry_id: str):
        """Initialize the cover."""
        self.hass = hass
        self._config = config
        self._entry_id = entry_id
        self._attr_name = config[CONF_COVER_NAME]
        self._attr_unique_id = f"garage_door_{entry_id.replace('-', '_')}"
        
        # Store sensor and relay entities
        self._closed_sensor = config[CONF_CLOSED_SENSOR]
        self._closed_sensor_state = config[CONF_CLOSED_SENSOR_STATE]
        self._open_sensor = config[CONF_OPEN_SENSOR]
        self._open_sensor_state = config[CONF_OPEN_SENSOR_STATE]
        self._open_relay = config[CONF_OPEN_RELAY]
        self._close_relay = config[CONF_CLOSE_RELAY]
        self._open_time = config[CONF_OPEN_TIME]
        self._close_time = config[CONF_CLOSE_TIME]
        self._enable_stuck_notification = config.get(CONF_ENABLE_STUCK_NOTIFICATION, True)
        
        self._state = None
        self._movement_task: asyncio.Task | None = None

    @property
    def current_cover_position(self) -> int | None:
        """Return current position of cover."""
        return None

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed."""
        if self._state == "closed":
            return True
        if self._state == "open":
            return False
        return None

    @property
    def is_opening(self) -> bool:
        """Return if the cover is opening."""
        return self._state == "opening"

    @property
    def is_closing(self) -> bool:
        """Return if the cover is closing."""
        return self._state == "closing"

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        if self._state == "closed":
            # Cancel any existing movement task
            if self._movement_task and not self._movement_task.done():
                self._movement_task.cancel()
            
            # Turn on open relay
            await self.hass.services.async_call(
                "switch", "turn_on", {"entity_id": self._open_relay}
            )
            # Wait 0.5 seconds
            await asyncio.sleep(0.5)
            # Turn off open relay
            await self.hass.services.async_call(
                "switch", "turn_off", {"entity_id": self._open_relay}
            )
            
            # Set state to opening
            self._state = "opening"
            self.async_write_ha_state()
            
            # Start movement timeout task
            self._movement_task = asyncio.create_task(
                self._async_movement_timeout("opening", self._open_time)
            )

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        if self._state == "open":
            # Cancel any existing movement task
            if self._movement_task and not self._movement_task.done():
                self._movement_task.cancel()
            
            # Turn on close relay
            await self.hass.services.async_call(
                "switch", "turn_on", {"entity_id": self._close_relay}
            )
            # Wait 0.5 seconds
            await asyncio.sleep(0.5)
            # Turn off close relay
            await self.hass.services.async_call(
                "switch", "turn_off", {"entity_id": self._close_relay}
            )
            
            # Set state to closing
            self._state = "closing"
            self.async_write_ha_state()
            
            # Start movement timeout task
            self._movement_task = asyncio.create_task(
                self._async_movement_timeout("closing", self._close_time)
            )

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        # Cancel movement task
        if self._movement_task and not self._movement_task.done():
            self._movement_task.cancel()
            self._movement_task = None
        
        # Stop both relays
        await self.hass.services.async_call(
            "switch", "turn_off", {"entity_id": self._open_relay}
        )
        await self.hass.services.async_call(
            "switch", "turn_off", {"entity_id": self._close_relay}
        )
        
        # Update state based on sensors
        await self._async_update_state()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Restore state
        if (last_state := await self.async_get_last_state()) is not None:
            self._state = last_state.state
        
        # Set up listeners for sensor changes
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._closed_sensor, self._open_sensor],
                self._async_sensor_changed,
            )
        )
        
        # Update state immediately
        await self._async_update_state()

    @callback
    def _async_sensor_changed(self, event) -> None:
        """Handle sensor state changes."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return
        
        entity_id = event.data.get("entity_id")
        
        # If we're in a movement state and sensors indicate we've reached target, cancel timeout
        if self._state in ("opening", "closing"):
            closed_state = self.hass.states.get(self._closed_sensor)
            open_state = self.hass.states.get(self._open_sensor)
            
            # Check if we've reached the target state
            if self._state == "opening" and open_state and open_state.state == self._open_sensor_state:
                # Reached open state
                if self._movement_task and not self._movement_task.done():
                    self._movement_task.cancel()
                    self._movement_task = None
                self._state = "open"
                self.async_write_ha_state()
                return
            elif self._state == "closing" and closed_state and closed_state.state == self._closed_sensor_state:
                # Reached closed state
                if self._movement_task and not self._movement_task.done():
                    self._movement_task.cancel()
                    self._movement_task = None
                self._state = "closed"
                self.async_write_ha_state()
                return
        
        # Otherwise, schedule state update
        self.hass.async_create_task(self._async_update_state())

    async def _async_update_state(self) -> None:
        """Update the cover state based on sensors."""
        closed_state = self.hass.states.get(self._closed_sensor)
        open_state = self.hass.states.get(self._open_sensor)
        
        # Check sensor states
        if closed_state and closed_state.state == self._closed_sensor_state:
            # Cancel any movement task if we've reached closed state
            if self._movement_task and not self._movement_task.done():
                self._movement_task.cancel()
                self._movement_task = None
            self._state = "closed"
        elif open_state and open_state.state == self._open_sensor_state:
            # Cancel any movement task if we've reached open state
            if self._movement_task and not self._movement_task.done():
                self._movement_task.cancel()
                self._movement_task = None
            self._state = "open"
        elif self._state not in ("opening", "closing"):
            # Only set to unknown if we're not in a movement state
            # (movement states are maintained until sensors indicate completion or timeout)
            self._state = "unknown"
        
        self.async_write_ha_state()

    async def _async_movement_timeout(self, movement_state: str, timeout_seconds: int) -> None:
        """Handle movement timeout - check if door is stuck."""
        try:
            # Wait for the movement timeout
            await asyncio.sleep(timeout_seconds)
            
            # Check if we're still in the movement state (door might be stuck)
            if self._state == movement_state:
                # Door didn't complete movement in time
                if self._enable_stuck_notification:
                    await self.hass.services.async_call(
                        "persistent_notification",
                        "create",
                        {
                            "title": "Garage Door Stuck",
                            "message": f"The {self._attr_name} appears stuck (state: {self._state}). Check sensors or manually inspect.",
                        },
                    )
                # Cancel the movement task
                self._movement_task = None
                # Update state based on sensors
                await self._async_update_state()
        except asyncio.CancelledError:
            # Movement completed or was cancelled - this is normal
            pass

