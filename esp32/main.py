from wifi import connect
from mqtt_client import MQTTManager
from sensors import read_all
from config import MQTT_TOPIC_SENSOR

import json
import time

print("Connecting Wi-Fi...")
connect()

print("Connecting MQTT...")
mqtt = MQTTManager()
mqtt.connect()

print("Hydroponics Node Started")

while True:

    try:
        sensor_data = read_all()

        mqtt.publish(
            MQTT_TOPIC_SENSOR,
            json.dumps(sensor_data)
        )

        print(sensor_data)

    except Exception as e:
        print("Error:", e)

    time.sleep(5)