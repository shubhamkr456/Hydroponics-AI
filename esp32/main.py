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

relay_33 = Pin(33, Pin.OUT)
relay_25 = Pin(25, Pin.OUT)
relay_26 = Pin(26, Pin.OUT)

relay_33.value(1)
relay_25.value(1)
relay_26.value(1)

# ==========================================
# MQTT Callback
# ==========================================

def mqtt_callback(topic, msg):

    print("MQTT Received:", topic, msg)

    data = json.loads(msg)

    relay = data["relay"]
    state = data["state"]

    # Active-low relay logic
    gpio_state = 0 if state else 1

    if relay == 33:
        relay_33.value(gpio_state)

    elif relay == 25:
        relay_25.value(gpio_state)

    elif relay == 26:
        relay_26.value(gpio_state)

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
# Scheduler
# ==========================================

PUBLISH_INTERVAL = 60       # seconds (change to 5 while developing)

last_publish = 0

# ==========================================
# Main Loop
# ==========================================

while True:

    try:

        # Listen for incoming MQTT commands continuously
        mqtt.check_messages()

        now = time.time()

        # Publish sensor data only every PUBLISH_INTERVAL seconds
        if now - last_publish >= PUBLISH_INTERVAL:

            sensor_data = read_all()

            mqtt.publish(
                MQTT_TOPIC_SENSOR,
                json.dumps(sensor_data)
            )

            print(sensor_data)

            last_publish = now

        # Small delay keeps CPU usage low while remaining responsive
        time.sleep(0.5)

    except Exception as e:
        print("Error:", e)