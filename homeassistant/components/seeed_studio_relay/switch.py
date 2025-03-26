"""Support for PCF8574 switches."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from ._seeed_relay import Relay
from .const import CONF_PIN_NAME, CONF_PIN_NUMBER

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the PCF8574 switch platform."""
    pcf = entry.runtime_data

    switch_entity = Switch(entry.data[CONF_PIN_NAME], entry.data[CONF_PIN_NUMBER], pcf)
    _ENTITIES[entry.entry_id] = switch_entity
    async_add_entities([switch_entity])


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry and remove the switch entity."""
    entity = _ENTITIES.pop(entry.entry_id)
    await entity.async_turn_off()
    await entity.async_remove()
    return True


class Switch(SwitchEntity):
    """Representation of a PCF8574 switch."""

    def __init__(self, name: str, pin_num: int, board: Relay) -> None:
        """Initialize the switch."""
        self._name = name
        self._pin_num = pin_num

        self._board = board
        self._state = False

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return f"Switch {self._name}"

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self._board.on(self._pin_num)
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self._board.off(self._pin_num)
        self._state = False
        self.schedule_update_ha_state()


_ENTITIES: dict[str, Switch] = {}
