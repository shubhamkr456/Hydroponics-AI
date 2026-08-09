import json
import requests
import paho.mqtt.client as mqtt
from datetime import datetime


# ==========================================
# MQTT Configuration
# ==========================================

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

MQTT_TOPIC_SENSOR = "hydroponics/sensors"

MQTT_TOPIC_TIME_REQUEST = "hydroponics/time/request"
MQTT_TOPIC_TIME_RESPONSE = "hydroponics/time/response"


# ==========================================
# Flask Server
# ==========================================

FLASK_URL = "http://192.168.0.100:5000/captures"


# ==========================================
# MQTT Connected
# ==========================================

def on_connect(client, userdata, flags, reason_code, properties=None):

    print("Connected to MQTT Broker")

    # Sensor data
    client.subscribe(MQTT_TOPIC_SENSOR)

    # ESP32 time requests
    client.subscribe(MQTT_TOPIC_TIME_REQUEST)

    print("Subscribed:", MQTT_TOPIC_SENSOR)
    print("Subscribed:", MQTT_TOPIC_TIME_REQUEST)


# ==========================================
# MQTT Message
# ==========================================

def on_message(client, userdata, msg):

    try:

        payload = json.loads(msg.payload.decode())

        print("\nReceived MQTT:")
        print(payload)


        # ==========================================
        # TIME REQUEST
        # ==========================================

        if msg.topic == MQTT_TOPIC_TIME_REQUEST:

            current = datetime.now()

            time_payload = {

                "year": current.year,
                "month": current.month,
                "day": current.day,

                "weekday": current.weekday(),

                "hour": current.hour,
                "minute": current.minute,
                "second": current.second
            }

            client.publish(
                MQTT_TOPIC_TIME_RESPONSE,
                json.dumps(time_payload)
            )

            print("Time Response:", time_payload)

            return


        # ==========================================
        # SENSOR DATA → FLASK
        # ==========================================

        if msg.topic == MQTT_TOPIC_SENSOR:

            if payload.get("device_id")!= "esp32_main":
                print("Ignoring incubator data")
                return

            response = requests.post(
                FLASK_URL,
                json=payload,
                timeout=5
            )

            print(f"HTTP Status: {response.status_code}")
            print(response.text)

    except Exception as e:

        print("Error:", e)


# ==========================================
# MQTT Client
# ==========================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message


# ==========================================
# Connect
# ==========================================

client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60
)

print("Waiting for MQTT messages...")


# ==========================================
# Main MQTT Loop
# ==========================================

client.loop_forever()