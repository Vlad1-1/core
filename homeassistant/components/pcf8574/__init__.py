"""The PCF8574 I/O Expander integration."""

from __future__ import annotations

import logging

from pcf8574 import PCF8574

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError

from .const import CONF_I2C_ADDRESS, CONF_I2C_BUS, DOMAIN

# For your initial PR, limit it to 1 platform.
_PLATFORMS: list[Platform] = [Platform.SWITCH]

type PCFConfigEntry = ConfigEntry[PCF8574]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: PCFConfigEntry) -> bool:
    """Set up PCF8574 I/O Expander from a config entry."""

    if entry.data[CONF_I2C_ADDRESS] not in range(0x20, 0x28):
        _LOGGER.error(
            "Invalid I2C address for PCF8574: %s", entry.data[CONF_I2C_ADDRESS]
        )
        raise ConfigEntryError("Invalid I2C address")

    try:
        entry.runtime_data = await hass.async_add_executor_job(
            PCF8574, entry.data[CONF_I2C_BUS], entry.data[CONF_I2C_ADDRESS]
        )
    except OSError as e:
        _LOGGER.error("Error setting up: %s", str(e))
        raise ConfigEntryError("Could not open i2c bus") from e

    entry.unique_id = DOMAIN

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: PCFConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
