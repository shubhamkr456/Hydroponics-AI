import time
from machine import Pin, I2C
import ssd1306
from mux import select_mux_channel
from bigfont import (
    draw_big_char,
    draw_big_text_right,
    draw_label,
)

# ==========================================
# 3. HARDWARE SETUP & HELPERS
# ==========================================
# Using 100kHz for maximum stability across mixed devices
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)

# ==========================================
# 4. INITIALIZATION
# ==========================================
def init_display():
    print("Waiting for screens to power up...")
    time.sleep(1)

    print("Configuring OLEDs...")
    select_mux_channel(i2c, 5)
    oled_ch5 = ssd1306.SSD1306_I2C(128, 64, i2c)

    select_mux_channel(i2c, 7)
    oled_ch7 = ssd1306.SSD1306_I2C(128, 64, i2c)

    print("Setup Complete!")
    
    return oled_ch5, oled_ch7, i2c

# ==========================================
# 5. MAIN LOOP
# ==========================================
def update_display(
    oled_ch5,
    oled_ch7,
    i2c,
    sensor_data):

#---------------------------------
# Live Sensor Data
# ----------------------------------

    temp_c = sensor_data["temperature"]
    humidity = sensor_data["humidity"]
    ph_level = sensor_data["ph"]
    tds_ppm = sensor_data["tds"]

    reservoir_level_cm = sensor_data["reservoir_distance_cm"]
    light_percent = sensor_data["light_percentage"]

# ----------------------------------
    # WATER LEVEL CALCULATION
    # Total Depth = 50 cm
    # Full Offset = 7 cm (100% full)
    # Usable Range = 43 cm (50 - 7)
    # ----------------------------------
    if reservoir_level_cm <= 7:
        water_percent = 100
    elif reservoir_level_cm >= 50:
        # Prevents negative percentages if the tank is bone dry
        water_percent = 0
    else:   
        # Scale smoothly across the 43cm of actual workable space
        water_percent = int(((50 - reservoir_level_cm) / 43) * 100)

    # ------------------------------------------
    # UPDATE OLED 1: ENVIRONMENT (CH 5)
    # ------------------------------------------
    
    select_mux_channel(i2c, 5)
    oled_ch5.fill(0) 
    
    draw_label(oled_ch5, "TEMP", 0, 2)
    oled_ch5.text("C", 2, 18)
    draw_big_text_right(oled_ch5, "{:.1f}".format(temp_c), 2, scale=5)
    oled_ch5.hline(0, 32, 128, 1) 
    
    draw_label(oled_ch5, "HUM", 0, 36)
    oled_ch5.text("%", 2, 52)
    draw_big_text_right(oled_ch5, "{:.0f}".format(humidity), 36, scale=5)
    
    try:
        time.sleep_ms(5)
        oled_ch5.show()
        time.sleep_ms(1)
    except Exception as e:
        print("OLED5:", e)
    
    # ------------------------------------------
    # UPDATE OLED 2: WATER QUALITY (CH 7)
    # ------------------------------------------
    select_mux_channel(i2c, 7)
    oled_ch7.fill(0) 
    oled_ch7.vline(64, 0, 64, 1)
    
    draw_label(oled_ch7, "pH", 0, 2)
    draw_big_text_right(oled_ch7, "{:.1f}".format(ph_level), 34, scale=4, right_edge=61)
    
    draw_label(oled_ch7, "TDS", 68, 2)
    oled_ch7.text("ppm", 68, 16) 
    draw_big_text_right(oled_ch7, "{:.0f}".format(tds_ppm), 34, scale=4, right_edge=128)
    
    try:
        oled_ch7.show()
    except Exception as e:
        print("OLED7:", e)