"""The PCF8574 I/O Expander integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError

from . import board_instance
from .seeed_relay import Relay

# For your initial PR, limit it to 1 platform.
_PLATFORMS: list[Platform] = [Platform.SWITCH]

type PCFConfigEntry = ConfigEntry[Relay]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: PCFConfigEntry) -> bool:
    """Set up PCF8574 I/O Expander from a config entry."""

    if not board_instance.is_configured():
        try:
            board_instance.RELAY_INSTANCE = await hass.async_add_executor_job(Relay)
        except OSError as e:
            _LOGGER.error("Error setting up: %s", str(e))
            raise ConfigEntryError("Could not open i2c bus") from e

    if isinstance(board_instance.RELAY_INSTANCE, Relay):
        entry.runtime_data = board_instance.RELAY_INSTANCE

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: PCFConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
