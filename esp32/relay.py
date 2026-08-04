from machine import Pin

relays = {
    33: Pin(33, Pin.OUT),
    25: Pin(25, Pin.OUT),
    26: Pin(26, Pin.OUT),
    4: Pin(4, Pin.OUT),
}

for relay in relays.values():
    relay.value(1)
