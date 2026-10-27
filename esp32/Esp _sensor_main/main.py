#---Imports--------------------------------
from wifi import connect
from mqtt_client import MQTTManager
from sensors import read_all
from config import MQTT_TOPIC_SENSOR, DEVICE_ID
import machine
from machine import RTC
import gc
import json
import time
import network
from relay import relays

# --- New Display Module Imports ---
from display import init_display, update_display

# ==========================================
# Constants & Settings
# ==========================================

PUMP_RUNTIME = 10  # The exact number of seconds a pump will run when triggered manually
PUBLISH_INTERVAL = 60 # How often to read sensors & send MQTT data (60 = 1 minute)
RECONNECT_INTERVAL = 10 # How often to retry Wi-Fi/MQTT if offline

# --- Light & Time Constants ---
LIGHT_RELAY = 14
LDR_THRESHOLD = 2500
START_HOUR = 6    
START_MINUTE = 0
END_HOUR = 23     
END_MINUTE = 0

# --- MQTT Topics ---
MQTT_TOPIC_TIME_REQUEST = b"hydroponics/time/request"
MQTT_TOPIC_TIME_RESPONSE = b"hydroponics/time/response"
MQTT_TOPIC_CONTROL = b"hydroponics/control"

# ==========================================
# Global State
# ==========================================
latest_sensor_data = {}
wlan = network.WLAN(network.STA_IF)
mqtt = MQTTManager()
rtc = RTC()

mode = "AUTO"
manual_light = False
mqtt_connected = False  
last_network_retry = 0

# Track when a pump was turned on so we can auto-turn it off
pump_timers = {
    33: None,
    25: None,
    26: None,
    4: None,
}

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
            manage_lights(latest_sensor_data.get("ldr_raw")) # Force immediate update

        # Pump Control
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
# Non-Blocking Reconnect Functions
# ==========================================

def try_wifi():
    print("Attempting Wi-Fi connection...")
    try:
        connect() 
        return wlan.isconnected()
    except Exception as e:
        print("Wi-Fi attempt failed:", e)
        return False

def try_mqtt():
    global mqtt_connected
    print("Attempting MQTT connection...")
    try:
        mqtt.connect()
        mqtt.set_callback(mqtt_callback)
        mqtt.subscribe(MQTT_TOPIC_CONTROL)
        mqtt.subscribe(MQTT_TOPIC_TIME_RESPONSE)
        mqtt.publish(MQTT_TOPIC_TIME_REQUEST, json.dumps({"device_id": DEVICE_ID}))
        
        mqtt_connected = True
        print("MQTT Reconnected Successfully!")
    except Exception as e:
        print("MQTT attempt failed:", e)
        mqtt_connected = False


# ==========================================
# Automation Functions
# ==========================================

def manage_lights(ldr_raw):
    if mode == "AUTO":
        current = time.localtime()
        current_minutes = current[3] * 60 + current[4]
        start_minutes = START_HOUR * 60 + START_MINUTE
        end_minutes = END_HOUR * 60 + END_MINUTE

        if start_minutes <= current_minutes < end_minutes:
            if ldr_raw is not None and ldr_raw < LDR_THRESHOLD:
                if relays[LIGHT_RELAY].value() != 0:
                    relays[LIGHT_RELAY].value(0)
            else:
                if relays[LIGHT_RELAY].value() != 1:
                    relays[LIGHT_RELAY].value(1)
        else:
            if relays[LIGHT_RELAY].value() != 1:
                relays[LIGHT_RELAY].value(1)
                
    elif mode == "MANUAL":
        if manual_light:
            if relays[LIGHT_RELAY].value() != 0:
                relays[LIGHT_RELAY].value(0)
        else:
            if relays[LIGHT_RELAY].value() != 1:
                relays[LIGHT_RELAY].value(1)

def auto_turn_off_pumps(now):
    for relay, start_time in pump_timers.items():
        if start_time is None:
            continue
        if now - start_time >= PUMP_RUNTIME:
            relays[relay].value(1)
            pump_timers[relay] = None
            print(f"Relay {relay} AUTO OFF")


# ==========================================
# INITIALIZATION
# ==========================================
gc.enable()
last_publish = 0
print("Standalone Hydroponics Node Started")

# --- Initialize physical OLED Screen ---
oled_screen = init_display()

# Try connecting once on boot
if not wlan.isconnected():
    try_wifi()
if wlan.isconnected():
    try_mqtt()


# ==========================================
# MAIN LOOP
# ==========================================

while True:
    try:
        now = time.time()

        # 1. NETWORK MANAGEMENT (Non-Blocking)
        if not wlan.isconnected():
            mqtt_connected = False
            if now - last_network_retry >= RECONNECT_INTERVAL:
                try_wifi()
                last_network_retry = now
                
        elif not mqtt_connected:
            if now - last_network_retry >= RECONNECT_INTERVAL:
                try_mqtt()
                last_network_retry = now
                
        else:
            # Connected, check for messages
            try:
                mqtt.check_messages()
            except Exception:
                print("MQTT Connection Lost!")
                mqtt_connected = False

        # 2. CORE AUTOMATION
        # This checks the 5-second timers every single loop!
        auto_turn_off_pumps(now)
        
        # 3. SENSOR & LIGHT MANAGEMENT (Runs on interval)
        if now - last_publish >= PUBLISH_INTERVAL:
            latest_sensor_data = read_all()
            
            # Update physical display with newest sensor readouts
            update_display(oled_screen, latest_sensor_data)
            
            # Lights are managed offline-safely
            manage_lights(latest_sensor_data.get("ldr_raw"))

            # 4. PUBLISH
            if mqtt_connected:
                try:
                    latest_sensor_data["device_id"] = DEVICE_ID
                    latest_sensor_data["mode"] = mode
                    mqtt.publish(MQTT_TOPIC_SENSOR, json.dumps(latest_sensor_data))
                    print("Published:", latest_sensor_data)
                except Exception as e:
                    print("Publish failed:", e)
                    mqtt_connected = False # Force a reconnect on next loop
            else:
                print("Offline Mode. Sensors read, but skipping publish.")
            
            gc.collect()
            last_publish = now

        # FAST LOOP SLEEP: Keeps the loop ticking so it can check pump timers instantly!
        # Do not change this to 50 or 60! 
        time.sleep(1.0)

    except Exception as e:
        print("Main Loop Error:  ", e)
        time.sleep(1.0)

