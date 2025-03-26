"""Global PCF8574 instance."""

from _seeed_relay import Relay

RELAY_INSTANCE: Relay | None = None


def is_configured() -> bool:
    """Return true if the PCF8574 is already configured."""
    return RELAY_INSTANCE is not None
