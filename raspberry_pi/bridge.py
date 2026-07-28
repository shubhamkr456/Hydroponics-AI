import json
import requests
import paho.mqtt.client as mqtt

# MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "hydroponics/sensors"

# Flask Server
FLASK_URL = "http://10.111.27.93:5000/captures"


def on_connect(client, userdata, flags, reason_code, properties=None):
    print("✅ Connected to MQTT Broker")
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        print("\nReceived MQTT:")
        print(payload)

        response = requests.post(
            FLASK_URL,
            json=payload,
            timeout=5
        )

        print(f"HTTP Status: {response.status_code}")
        print(response.text)

    except Exception as e:
        print("Error:", e)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

print("Waiting for sensor data...")
client.loop_forever()