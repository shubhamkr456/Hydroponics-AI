#---Imports--------------------------------
from wifi import connect
from mqtt_client import MQTTManager
from sensors import read_all
from config import MQTT_TOPIC_SENSOR

import json
import time
from relay import relays
from display import init_display, update_display

# ==========================================
# Constants
# ==========================================

PUMP_RUNTIME = 5  # seconds
PUBLISH_INTERVAL = 60
DISPLAY_INTERVAL = 4

# -- changed to global
latest_sensor_data = {}

pump_timers = {
    33: None,
    25: None,
    26: None,
    4:None,
}

# ==========================================
# FUNCTIONS
# ==========================================

def initialize():

    print("Connecting Wi-Fi...")
    connect()

    print("Connecting MQTT...")
    mqtt = MQTTManager()
    mqtt.connect()

    mqtt.set_callback(mqtt_callback)
    mqtt.subscribe("hydroponics/control")

    print("Hydroponics Node Started")

    return mqtt

def auto_turn_off_pumps(now):

    for relay, start_time in pump_timers.items():

        if start_time is None:
            continue

        if now - start_time >= PUMP_RUNTIME:

            relays[relay].value(1)

            pump_timers[relay] = None

            print("Relay", relay, "AUTO OFF")

"""
def publish_sensor_data(
    mqtt,
    now,
    last_publish,
    lcd,
    oled_ch5,
    oled_ch7,
    i2c,
    page,):
    
    global latest_sensor_data

    if now - last_publish < PUBLISH_INTERVAL:
        return last_publish, page

    #sensor_data = read_all()
    # inserted here
    latest_sensor_data = read_all()

    page = update_display(
        lcd,
        oled_ch5,
        oled_ch7,
        i2c,
        latest_sensor_data,
        page,
    )
    
    mqtt.publish(
    MQTT_TOPIC_SENSOR,
    json.dumps(latest_sensor_data))

    print(latest_sensor_data)

    return now, page"""
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




#  Connect and initialize wifi
#--------------------Working Crux of the code--------
mqtt = initialize()
oled_ch5, oled_ch7, i2c = init_display()

latest_sensor_data = read_all()

last_publish = 0
last_display = 0
#-----------------
# MAIn Loop
#-----------------
while True:

    try:

        mqtt.check_messages()

        now = time.time()

        auto_turn_off_pumps(now)

        # -----------------------------
        # Refresh Display
        # -----------------------------
        if now - last_display >= DISPLAY_INTERVAL:
            update_display(
             oled_ch5,
             oled_ch7, i2c,
               latest_sensor_data,
             )
            last_display = now

        # -----------------------------
        # Read Sensors + Publish MQTT
        # -----------------------------
        if now - last_publish >= PUBLISH_INTERVAL:

            latest_sensor_data = read_all()

            mqtt.publish(
                MQTT_TOPIC_SENSOR,
                json.dumps(latest_sensor_data)
            )

            print(latest_sensor_data)

            last_publish = now

        time.sleep(0.1)

    except Exception as e:
        print("Error:", e)