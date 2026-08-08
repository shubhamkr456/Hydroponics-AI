from machine import Pin

# ==========================================
# Grow Light Relay (Active LOW)
# ==========================================

RELAY_PIN = 26

relay = Pin(RELAY_PIN, Pin.OUT)

# Keep relay OFF at startup
relay.value(1)

# Internal state
_grow_light_on = False


def turn_on():
    global _grow_light_on

    relay.value(0)          
    _grow_light_on = True

    print("Grow Light ON")


def turn_off():
    global _grow_light_on

    relay.value(1)
    _grow_light_on = False

    print("Grow Light OFF")


def is_on():
    return _grow_light_on


def toggle():

    if is_on():
        turn_off()
    else:
        turn_on()
