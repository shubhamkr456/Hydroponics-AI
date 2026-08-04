import time
from machine import Pin, I2C
import ssd1306
from i2c_lcd import I2cLcd
from mux import select_mux_channel
from bigfont import (
    draw_big_char,
    draw_big_text_right,
    draw_label,
)
from lcd import update_lcd

# ==========================================
# 3. HARDWARE SETUP & HELPERS
# ==========================================
# Using 100kHz for maximum stability across mixed devices
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)

LCD_ADDR = 0x27 


# ==========================================
# 4. INITIALIZATION
# ==========================================
print("Waiting for screens to power up...")
time.sleep(1)

print("Configuring LCD on Channel 1...")
select_mux_channel(i2c, 1)
lcd = I2cLcd(i2c, LCD_ADDR, 2, 16)
lcd.putstr("LCD Online!")

print("Configuring OLEDs...")
select_mux_channel(i2c, 5)
oled_ch5 = ssd1306.SSD1306_I2C(128, 64, i2c)

select_mux_channel(i2c, 7)
oled_ch7 = ssd1306.SSD1306_I2C(128, 64, i2c)

print("Setup Complete! Running loop...")

# ==========================================
# 5. MAIN LOOP
# ==========================================
page = 0

while True:
    # ----------------------------------
    # DUMMY SENSOR DATA (Replace later)
    # ----------------------------------
    temp_c = 25.1
    humidity = 62.0
    ph_level = 6.8
    tds_ppm = 420
    reservoir_level_cm = 7        # 0-20 cm
    light_percent = 82               # 0-100 %
    pump_on = True
    dosing_on = False
    wifi_ok = True
    mqtt_ok = True

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
    
    oled_ch5.show()
    
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
    
    oled_ch7.show()
    
    page = update_lcd(
    lcd,
    i2c,
    page,
    water_percent,
    light_percent,
    pump_on,
    dosing_on,
    wifi_ok,
    mqtt_ok,
    reservoir_level_cm)
    

 

    time.sleep(4)