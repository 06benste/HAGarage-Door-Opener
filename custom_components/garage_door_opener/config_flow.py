"""Config flow for Garage Door Opener integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

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
    DEFAULT_CLOSED_SENSOR_STATE,
    DEFAULT_CLOSE_TIME,
    DEFAULT_COVER_NAME,
    DEFAULT_ENABLE_STUCK_NOTIFICATION,
    DEFAULT_OPEN_SENSOR_STATE,
    DEFAULT_OPEN_TIME,
    DOMAIN,
)


class GarageDoorOpenerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Garage Door Opener."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate inputs
            if not errors:
                # Create the config entry
                return self.async_create_entry(
                    title=user_input[CONF_COVER_NAME],
                    data=user_input,
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_COVER_NAME, default=DEFAULT_COVER_NAME): str,
                vol.Required(CONF_CLOSED_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="binary_sensor")
                ),
                vol.Required(
                    CONF_CLOSED_SENSOR_STATE, default=DEFAULT_CLOSED_SENSOR_STATE
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["off", "on", "closed", "open"],
                        translation_key="sensor_state",
                    )
                ),
                vol.Required(CONF_OPEN_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="binary_sensor")
                ),
                vol.Required(
                    CONF_OPEN_SENSOR_STATE, default=DEFAULT_OPEN_SENSOR_STATE
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["off", "on", "closed", "open"],
                        translation_key="sensor_state",
                    )
                ),
                vol.Required(CONF_OPEN_RELAY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="switch")
                ),
                vol.Required(CONF_CLOSE_RELAY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="switch")
                ),
                vol.Required(CONF_OPEN_TIME, default=DEFAULT_OPEN_TIME): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=300,
                        unit_of_measurement="s",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(CONF_CLOSE_TIME, default=DEFAULT_CLOSE_TIME): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=300,
                        unit_of_measurement="s",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_ENABLE_STUCK_NOTIFICATION,
                    default=DEFAULT_ENABLE_STUCK_NOTIFICATION,
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

