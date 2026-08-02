from wifi import connect
from mqtt_client import MQTTManager
from sensors import read_all
from config import MQTT_TOPIC_SENSOR

from machine import Pin

import json
import time

# ==========================================
# Relay Configuration (Active Low)
# ==========================================

relays = {
    33: Pin(33, Pin.OUT),
    25: Pin(25, Pin.OUT),
    26: Pin(26, Pin.OUT),
    4: Pin(4, Pin.OUT),
}

# All relays OFF initially (Active Low)
for relay in relays.values():
    relay.value(1)

# ==========================================
# Pump Runtime Configuration
# ==========================================

PUMP_RUNTIME = 5  # seconds

pump_timers = {
    33: None,
    25: None,
    26: None,
    4:None,
}

# ==========================================
# MQTT Callback
# ==========================================

def mqtt_callback(topic, msg):

    print("MQTT Received:", topic, msg)

    try:
        data = json.loads(msg)

        relay = data["relay"]
        state = data["state"]

        if relay not in relays:
            print("Unknown relay:", relay)
            return

        # Active-low relay logic
        if state:
            relays[relay].value(0)       # ON
            pump_timers[relay] = time.time()
            print("Relay", relay, "ON")

        else:
            relays[relay].value(1)       # OFF
            pump_timers[relay] = None
            print("Relay", relay, "OFF")

    except Exception as e:
        print("MQTT Callback Error:", e)

# ==========================================
# Wi-Fi & MQTT
# ==========================================

print("Connecting Wi-Fi...")
connect()

print("Connecting MQTT...")
mqtt = MQTTManager()
mqtt.connect()

mqtt.set_callback(mqtt_callback)
mqtt.subscribe("hydroponics/control")

print("Hydroponics Node Started")

# ==========================================
# Sensor Publish Configuration
# ==========================================

PUBLISH_INTERVAL = 60      # Change to 5 during development

last_publish = 0

# ==========================================
# Main Loop
# ==========================================

while True:

    try:

        # Listen for MQTT commands continuously
        mqtt.check_messages()

        now = time.time()

        # ------------------------------------------
        # Auto Turn OFF Pumps
        # ------------------------------------------

        for relay, start_time in pump_timers.items():

            if start_time is not None:

                if now - start_time >= PUMP_RUNTIME:

                    relays[relay].value(1)      # OFF (Active Low)

                    pump_timers[relay] = None

                    print("Relay", relay, "AUTO OFF")

        # ------------------------------------------
        # Publish Sensor Data
        # ------------------------------------------

        if now - last_publish >= PUBLISH_INTERVAL:

            sensor_data = read_all()

            mqtt.publish(
                MQTT_TOPIC_SENSOR,
                json.dumps(sensor_data)
            )

            print(sensor_data)

            last_publish = now

        time.sleep(0.1)

    except Exception as e:
        print("Error:", e)