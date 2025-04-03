"""Seeed Studio Relay Board Library."""


# =========================================================
# Seeed Studio Raspberry Pi Relay Board Library
#
# by John M. Wargo (www.johnwargo.com)
#
# Modified from the sample code on the Seeed Studio Wiki
# http://wiki.seeed.cc/Raspberry_Pi_Relay_Board_v1.0/
# =========================================================

import logging

import smbus3 as smbus

# This value should never change since Seeed only makes 4 port boards,
# but I made it a constructor option anyway
# The number of relay ports on the relay board.
# NUM_RELAY_PORTS = 4

_LOGGER = logging.getLogger(__name__)

bus = smbus.SMBus()


class Relay:
    """Class for representing a relay board."""

    def __init__(self, device_address: int = 0x20, num_relays: int = 4) -> None:
        """Initialize the relay board."""
        _LOGGER.debug("Initializing relay board")
        if bus.fd is None:
            _LOGGER.debug("Opening I2C bus")
            try:
                bus.open(1)
                _LOGGER.debug("I2C bus opened")
            except OSError as e:
                _LOGGER.error("Error initializing relay board: %s", str(e))
                raise OSError("Error initializing relay board") from e

        self.DEVICE_ADDRESS = device_address
        self.NUM_RELAY_PORTS = num_relays
        self.DEVICE_REG_MODE1 = 0x06
        self.DEVICE_REG_DATA = 0xFF
        bus.write_byte_data(
            self.DEVICE_ADDRESS, self.DEVICE_REG_MODE1, self.DEVICE_REG_DATA
        )

    def on(self, relay_num: int) -> None:
        """Turn on the specified relay port.

        Closes the circuit between COM AND NO
        @param relay_num: The relay port number to turn on (1-4).
        """
        if 0 < relay_num <= self.NUM_RELAY_PORTS:
            self.DEVICE_REG_DATA &= ~(0x1 << (relay_num - 1))
            bus.write_byte_data(
                self.DEVICE_ADDRESS, self.DEVICE_REG_MODE1, self.DEVICE_REG_DATA
            )

    def off(self, relay_num: int) -> None:
        """Turn off the specified relay port.

        Closes the circuit between COM AND NC
        @param relay_num: The relay port number to turn off (1-4).
        """
        if 0 < relay_num <= self.NUM_RELAY_PORTS:
            self.DEVICE_REG_DATA |= 0x1 << (relay_num - 1)
            bus.write_byte_data(
                self.DEVICE_ADDRESS, self.DEVICE_REG_MODE1, self.DEVICE_REG_DATA
            )

    def all_on(self) -> None:
        """Turn on all relay ports."""
        self.DEVICE_REG_DATA &= ~(0xF << 0)
        bus.write_byte_data(
            self.DEVICE_ADDRESS, self.DEVICE_REG_MODE1, self.DEVICE_REG_DATA
        )

    def all_off(self) -> None:
        """Turn off all relay ports."""
        self.DEVICE_REG_DATA |= 0xF << 0
        bus.write_byte_data(
            self.DEVICE_ADDRESS, self.DEVICE_REG_MODE1, self.DEVICE_REG_DATA
        )

    def toggle_port(self, relay_num: int) -> None:
        """Toggle the specified relay port."""
        if self.get_port_status(relay_num):
            # it's on, so turn it off
            self.off(relay_num)
        else:
            # it's off, so turn it on
            self.on(relay_num)

    def get_port_status(self, relay_num: int) -> bool:
        """Return the status of the specified relay port."""
        # determines whether the specified port is ON/OFF
        res = self.get_port_data(relay_num)
        if res > 0:
            mask = 1 << (relay_num - 1)
            # return the specified bit status
            # return (DEVICE_REG_DATA & mask) != 0
            return (self.DEVICE_REG_DATA & mask) == 0
        return False

    def get_port_data(self, relay_num: int) -> int:
        """Return the current byte value stored in the relay board."""
        if 0 < relay_num <= self.NUM_RELAY_PORTS:
            # read the memory location
            self.DEVICE_REG_DATA = bus.read_byte_data(
                self.DEVICE_ADDRESS, self.DEVICE_REG_MODE1
            )
            # return the specified bit status
            return self.DEVICE_REG_DATA
        return 0
