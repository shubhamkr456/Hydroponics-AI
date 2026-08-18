#---Imports--------------------------------
from wifi import connect
from mqtt_client import MQTTManager
from sensors import read_all, read_reservoir_level
from config import MQTT_TOPIC_SENSOR, DEVICE_ID
import machine
from machine import RTC
import gc
import json
import time
import network
from relay import relays
from display import init_display, update_display

# ==========================================
# Constants & Settings
# ==========================================

PUMP_RUNTIME = 5  # seconds
PUBLISH_INTERVAL = 60

# --- Water Level Constants ---
WATER_PUMP_RELAY = 19
FILL_START_CM = 15.0
FILL_STOP_CM = 8.0

# --- Light & Time Constants ---
LIGHT_RELAY = 14
LDR_THRESHOLD = 2400
START_HOUR = 6    # Light window starts at 6:00 AM
START_MINUTE = 0
END_HOUR = 23     # Light window ends at 11:00 PM
END_MINUTE = 0

# --- MQTT Topics (Merged) ---
MQTT_TOPIC_TIME_REQUEST = b"hydroponics/time/request"
MQTT_TOPIC_TIME_RESPONSE = b"hydroponics/time/response"
MQTT_TOPIC_CONTROL = b"hydroponics/control"

# ==========================================
# Global State
# ==========================================
latest_sensor_data = {}
is_filling = False
wlan = None
mqtt = None
rtc = RTC()

# Modes
mode = "AUTO"
manual_light = False

pump_timers = {
    33: None,
    25: None,
    26: None,
    4: None,
}

# ==========================================
# Reconnect Functions
# ==========================================

def reconnect_wifi():
    print("Wi-Fi Lost... Reconnecting")
    global wlan
    while True:
        try:
            wlan = connect()
            print("Wi-Fi Reconnected")
            return
        except Exception as e:
            print("Wi-Fi Retry Failed:", e)
            time.sleep(5)

def reconnect_mqtt():
    print("MQTT Lost... Reconnecting")
    global mqtt
    while True:
        try:
            mqtt.connect()
            mqtt.set_callback(mqtt_callback)
            mqtt.subscribe(MQTT_TOPIC_CONTROL)
            mqtt.subscribe(MQTT_TOPIC_TIME_RESPONSE)
            
            # Re-sync time on reconnect so the light schedule stays accurate
            mqtt.publish(MQTT_TOPIC_TIME_REQUEST, json.dumps({"device_id": DEVICE_ID}))
            
            print("MQTT Reconnected. Time re-synchronization requested.")
            return
        except Exception as e:
            print("MQTT Retry Failed:", e)
            time.sleep(5)

# ==========================================
# Automation Functions
# ==========================================

def manage_lights(ldr_raw):
    """
    Controls lights based on mode (AUTO/MANUAL), RTC time, and LDR sensor.
    """
    if mode == "AUTO":
        current = time.localtime()
        current_minutes = current[3] * 60 + current[4]
        start_minutes = START_HOUR * 60 + START_MINUTE
        end_minutes = END_HOUR * 60 + END_MINUTE

        # Only check light level if we are inside the scheduled daily window
        if start_minutes <= current_minutes < end_minutes:
            if ldr_raw is not None and ldr_raw < LDR_THRESHOLD:
                if relays[LIGHT_RELAY].value() != 0:
                    relays[LIGHT_RELAY].value(0)
                    print(f"AUTO Mode: Dark inside window. Light ON (Time: {current[3]}:{current[4]:02d}).")
            else:
                if relays[LIGHT_RELAY].value() != 1:
                    relays[LIGHT_RELAY].value(1)
                    print(f"AUTO Mode: Bright enough. Light OFF.")
        else:
            # Outside of scheduled window, force lights off regardless of LDR
            if relays[LIGHT_RELAY].value() != 1:
                relays[LIGHT_RELAY].value(1)
                print(f"AUTO Mode: Outside scheduled window ({END_HOUR}:00). Light OFF.")
                
    elif mode == "MANUAL":
        # Override everything based on manual MQTT command
        if manual_light:
            if relays[LIGHT_RELAY].value() != 0:
                relays[LIGHT_RELAY].value(0)
                print("MANUAL Mode: Light ON.")
        else:
            if relays[LIGHT_RELAY].value() != 1:
                relays[LIGHT_RELAY].value(1)
                print("MANUAL Mode: Light OFF.")

def auto_turn_off_pumps(now):
    for relay, start_time in pump_timers.items():
        if start_time is None:
            continue
        if now - start_time >= PUMP_RUNTIME:
            relays[relay].value(1)
            pump_timers[relay] = None
            print("Relay", relay, "AUTO OFF")

def manage_water_level():
    global is_filling
    dist = read_reservoir_level()
    time.sleep(0.01)

    if dist is not None:
        if dist >= FILL_START_CM and not is_filling:
            print(f"Water low ({dist} cm). Fill Pump ON.")
            relays[WATER_PUMP_RELAY].value(0)  
            is_filling = True
        elif dist <= FILL_STOP_CM and is_filling:
            print(f"Water full ({dist} cm). Fill Pump OFF.")
            relays[WATER_PUMP_RELAY].value(1)  
            is_filling = False

# ==========================================
# MQTT Callback
# ==========================================

def mqtt_callback(topic, msg):
    global mode, manual_light
    print("MQTT Received:", topic, msg)

    try:
        data = json.loads(msg)
        
        # 1. TIME RESPONSE HANDLING
        if topic == MQTT_TOPIC_TIME_RESPONSE:
            rtc.datetime((
                data["year"], data["month"], data["day"], data["weekday"],
                data["hour"], data["minute"], data["second"], 0
            ))
            print("RTC Updated:", data["hour"], ":", data["minute"])
            return

        # 2. CONTROL HANDLING
        if data.get("device_id") != DEVICE_ID:
            return

        # Mode switching (Auto/Manual)
        if "mode" in data:
            mode = data["mode"].upper()
            if mode == "MANUAL":
                manual_light = (relays[LIGHT_RELAY].value() == 0)
            print("Mode changed to:", mode)

        # Manual Light Toggle
        if mode == "MANUAL" and "light" in data:
            manual_light = data["light"]
            print("Manual Light Set To:", manual_light)
            manage_lights(None) # Force immediate update

        # Legacy Pump Control
        relay = data.get("relay")
        state = data.get("state")
        
        if relay is not None and state is not None:
            if relay not in relays:
                print("Unknown relay:", relay)
                return

            if state:
                relays[relay].value(0)       # ON
                if relay in pump_timers:
                    pump_timers[relay] = time.time()
                print("Relay", relay, "ON")
            else:
                relays[relay].value(1)       # OFF
                if relay in pump_timers:
                    pump_timers[relay] = None
                print("Relay", relay, "OFF")

    except Exception as e:
        print("MQTT Callback Error:", e)

# ==========================================
# INITIALIZATION
# ==========================================
gc.enable()

wlan = network.WLAN(network.STA_IF)
if not wlan.isconnected():
    reconnect_wifi()

mqtt = MQTTManager()
reconnect_mqtt()

oled_ch5, oled_ch7, oled_ch3, i2c = init_display()
latest_sensor_data = read_all()
last_publish = 0

print("Hydroponics Node Started")

# ==========================================
# MAIN LOOP
# ==========================================

while True:
    try:
        # Check Connections
        if not wlan.isconnected():
            reconnect_wifi()
            
        try:
            mqtt.check_messages()
            # Simple ping logic to keep broker connection alive
            if hasattr(mqtt.client, 'ping'):
                mqtt.client.ping()
        except Exception as e:
            print("MQTT Check Failed:", e)
            reconnect_mqtt()

        now = time.time()

        # Run Core Processes
        auto_turn_off_pumps(now)
        manage_water_level()
        
        # Publish & Display (Every 60 Seconds)
        if now - last_publish >= PUBLISH_INTERVAL:
            latest_sensor_data = read_all()
            latest_sensor_data["device_id"] = DEVICE_ID
            latest_sensor_data["mode"] = mode
            
            # Manage lights using RTC and Sensor Data
            manage_lights(latest_sensor_data.get("ldr_raw"))
            
            update_display(
                oled_ch5, oled_ch7, oled_ch3, i2c, latest_sensor_data
            )

            mqtt.publish(MQTT_TOPIC_SENSOR, json.dumps(latest_sensor_data))
            print(latest_sensor_data)

            last_publish = now
            
            print("Free RAM:", gc.mem_free())
            gc.collect()

        time.sleep(0.1)

    except Exception as e:
        print("Main Loop Error:", e)
        time.sleep(1)