"""Support for PCF8574 switches."""

import logging
from typing import Any

from pcf8574 import PCF8574

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import CONF_PINS, DOMAIN

_LOGGER = logging.getLogger(__name__)
type PCFConfigEntry = ConfigEntry[PCF8574]


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the PCF8574 switch platform."""

    switches = []
    entry = hass.config_entries.async_get_entry(DOMAIN)

    if isinstance(entry, ConfigEntry):
        pcf = entry.runtime_data

        pins = config[CONF_PINS]
        for pin_num, pin_name in pins.items():
            switches.append(PCF8574Switch(pin_name, pin_num, pcf))
            _LOGGER.debug(
                "async_setup_platform: pin_name=%s, pin_num=%s", pin_name, pin_num
            )

        add_entities(switches)
    else:
        _LOGGER.error("Couldn't find config entry")


class PCF8574Switch(SwitchEntity):
    """Representation of a PCF8574 switch."""

    def __init__(self, name: str, pin_num: int, pcf: PCF8574) -> None:
        """Initialize the switch."""
        self._name = name
        self._pin_num = pin_num

        self._pcf = pcf
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
        self._update_state(True)

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self._update_state(False)

    def _update_state(self, state: bool) -> None:
        """Update the state."""
        self._state = state
        self._pcf.set_output(self._pin_num, state)
        self.schedule_update_ha_state()
