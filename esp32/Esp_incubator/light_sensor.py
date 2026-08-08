from machine import Pin

# ==========================================
# Light Sensor (Digital Output)
# ==========================================

LIGHT_SENSOR_PIN = 34

sensor = Pin(LIGHT_SENSOR_PIN, Pin.IN)


def is_dark():
    """
    Returns True when it is DARK.
    Sensor logic:
        1 -> DARK
        0 -> BRIGHT
    """
    return sensor.value() == 1


def is_bright():
    return sensor.value() == 0


def read():
    return sensor.value()
