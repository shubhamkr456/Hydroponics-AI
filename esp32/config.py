# config.py

DEVICE_ID = "esp32_001"

# Wi-Fi
WIFI_SSID = "Hydroponics_LAB"
WIFI_PASSWORD = "hydroponic@123"

# MQTT
MQTT_BROKER = "10.111.27.53"     # Raspberry Pi IP
MQTT_PORT = 1883

MQTT_TOPIC_SENSOR = b"hydroponics/sensors"
MQTT_TOPIC_RELAY = b"hydroponics/relay"