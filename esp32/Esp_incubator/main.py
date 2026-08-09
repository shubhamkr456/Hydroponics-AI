# ==========================================
# Imports
# ==========================================
from configi import (
    DEVICE_ID,
    MQTT_TOPIC_SENSOR,
    MQTT_TOPIC_CONTROL,
    MQTT_TOPIC_TIME_REQUEST,
    MQTT_TOPIC_TIME_RESPONSE,
    START_HOUR,
    START_MINUTE,
    END_HOUR,
    END_MINUTE
)

from machine import RTC
from wifi import connect
from mqtt_client import MQTTManager

from relay import turn_on, turn_off, is_on
from light_sensor import is_dark
from lcd import (
    startup,
    update_display,
    show_wifi_error,
    show_mqtt_error,
    show_status
)
import network
import gc
import time
import json

# ==========================================
# Controller State
# ==========================================

mode = "AUTO"
manual_light = False
rtc = RTC()

# ==========================================
# MQTT Callback
# ==========================================

def mqtt_callback(topic, msg):

    global mode
    global manual_light

    try:

        data = json.loads(msg)

        # ==========================================
        # TIME RESPONSE
        # ==========================================

        if topic.decode() == MQTT_TOPIC_TIME_RESPONSE:

            rtc.datetime((
                data["year"],
                data["month"],
                data["day"],
                data["weekday"],
                data["hour"],
                data["minute"],
                data["second"],
                0
            ))

            print(
                "RTC Updated:",
                data["hour"],
                data["minute"],
                data["second"]
            )

            return

        # ==========================================
        # DEVICE CONTROL
        # ==========================================

        if data.get("device_id") != DEVICE_ID:
            return

        if "mode" in data:

            mode = data["mode"].upper()

            if mode == "MANUAL":
                manual_light = is_on()

            print("Mode changed to:", mode)

        if mode == "MANUAL" and "light" in data:

            manual_light = data["light"]

            print("Manual Light:", manual_light)

    except Exception as e:

        print("MQTT Callback Error:", e)


# ==========================================
# Reconnect Functions
# ==========================================

def reconnect_wifi():

    print("Wi-Fi Lost... Reconnecting")
    global wlan
    while True:

        try:

            connect()
            print("Wi-Fi Reconnected")
            return

        except Exception as e:

            print("Wi-Fi Retry Failed:", e)
            show_wifi_error()
            time.sleep(5)


def reconnect_mqtt():

    print("MQTT Lost... Reconnecting")

    while True:

        try:

            mqtt.connect()

            mqtt.set_callback(mqtt_callback)

            mqtt.subscribe(MQTT_TOPIC_CONTROL)
            mqtt.subscribe(MQTT_TOPIC_TIME_RESPONSE)

            mqtt.publish(
                MQTT_TOPIC_TIME_REQUEST,
                json.dumps({
                    "device_id": DEVICE_ID
                })
            )

            print("MQTT Reconnected")
            print("Time re-synchronization requested")

            return

        except Exception as e:

            print("MQTT Retry Failed:", e)

            show_mqtt_error()

            time.sleep(5)

# ==========================================
# Initialize
# ==========================================

gc.enable()

print("Connecting Wi-Fi...")
wlan = connect()
print("Connecting MQTT...")
mqtt = MQTTManager()
mqtt.connect()

mqtt.set_callback(mqtt_callback)

mqtt.subscribe(MQTT_TOPIC_CONTROL)
mqtt.subscribe(MQTT_TOPIC_TIME_RESPONSE)

mqtt.publish(
    MQTT_TOPIC_TIME_REQUEST,
    json.dumps({
        "device_id": DEVICE_ID
    })
)

print("Time synchronization requested")
for _ in range(10):

    mqtt.check_messages()

    time.sleep_ms(100)

startup()

print("Incubator Started")

last_publish = 0

# ==========================================
# Main Loop
# ==========================================

while True:
    try:
       # wlan = network.WLAN(network.STA_IF)

        if not wlan.isconnected():
            reconnect_wifi()
            
        try:
            mqtt.check_messages()
            if hasattr(mqtt, 'ping'):
                mqtt.ping()
            elif hasattr(mqtt, 'client') and hasattr(mqtt.client, 'ping'):
                mqtt.client.ping()

        except Exception as e:
            reconnect_mqtt()
            print("MQTT Check/Ping Failed:", e)

        # Controller
  
        if mode == "AUTO":

            current = time.localtime()

            current_minutes = current[3] * 60 + current[4]

            start_minutes = START_HOUR * 60 + START_MINUTE
            end_minutes = END_HOUR * 60 + END_MINUTE

            if start_minutes <= current_minutes < end_minutes:

                if is_dark():
                    turn_on()
                else:
                    turn_off()

            else:

                turn_off()

        else:

            if manual_light:
                turn_on()
            else:
                turn_off()        
        
        
        
        
        # LCD
       
        current = time.localtime()

        update_display(
            mode,
            current[3],
            current[4],
            is_on()
        )
    
        # Publish status every minute
        if time.time() - last_publish >= 60:
            status = {
                "device_id": DEVICE_ID,
                "light": is_on(),
                "dark": is_dark(),
                "mode": mode
            }
            try:
                mqtt.publish(
                MQTT_TOPIC_SENSOR,
                json.dumps(status)
            )
            except Exception:
                reconnect_mqtt()

            last_publish = time.time()

        gc.collect()
        print("Free RAM:", gc.mem_free())
        time.sleep(5)

    except Exception as e:
        print("Error:", e)
        time.sleep(2)