from umqtt.simple import MQTTClient
from config import DEVICE_ID, MQTT_BROKER, MQTT_PORT


class MQTTManager:

    def __init__(self):
        self.client = MQTTClient(
            client_id=DEVICE_ID,
            server=MQTT_BROKER,
            port=MQTT_PORT
        )

    def connect(self):
        print("Connecting to MQTT...")
        self.client.connect()
        print("MQTT Connected")

    def publish(self, topic, message):
        self.client.publish(topic, message)

    def disconnect(self):
        self.client.disconnect()