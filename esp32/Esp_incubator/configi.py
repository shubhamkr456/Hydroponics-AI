# config.py
# Device ID
DEVICE_ID = "esp32_incubator"

# Wi-Fi
WIFI_SSID = "Hydroponics_LAB"
WIFI_PASSWORD = "hydroponic@123"

# MQTT
MQTT_BROKER = "192.168.0.101"     # Raspberry Pi IP
MQTT_PORT = 1883


# Topics
MQTT_TOPIC_SENSOR = "hydroponics/sensors"
MQTT_TOPIC_CONTROL = "hydroponics/control"
MQTT_TOPIC_TIME_REQUEST = "hydroponics/time/request"
MQTT_TOPIC_TIME_RESPONSE = "hydroponics/time/response"
# Incubator Schedule
START_HOUR = 5
START_MINUTE = 0

END_HOUR = 23
END_MINUTE = 0
