"""Config flow for the PCF8574 I/O Expander integration."""

from __future__ import annotations

import logging
from typing import Any

from pcf8574 import PCF8574
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_I2C_ADDRESS,
    CONF_I2C_BUS,
    CONF_PINS,
    DEFAULT_I2C_ADDRESS,
    DEFAULT_I2C_BUS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

_SWITCHES_SCHEMA = vol.Schema({range(8): cv.string})

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PINS): [_SWITCHES_SCHEMA],
        vol.Optional(CONF_I2C_ADDRESS, default=DEFAULT_I2C_ADDRESS): vol.All(
            int, vol.Range(min=0x20, max=0x27)
        ),
        vol.Optional(CONF_I2C_BUS, default=DEFAULT_I2C_BUS): range(1),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )

    try:
        await hass.async_add_executor_job(
            PCF8574, data[CONF_I2C_BUS], data[CONF_I2C_ADDRESS]
        )
    except OSError as e:
        raise InvalidI2CBus from e

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "PCF8574"}


class PCFConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PCF8574 I/O Expander."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except InvalidI2CBus:
                errors["base"] = "invalid_i2c_bus"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class InvalidI2CBus(HomeAssistantError):
    """Error to indicate there is an invalid I2C bus."""
