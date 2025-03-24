"""Global PCF8574 instance."""

from pcf8574 import PCF8574

PCF_INSTANCE: PCF8574 | None = None


def is_configured() -> bool:
    """Return true if the PCF8574 is already configured."""
    return PCF_INSTANCE is not None
