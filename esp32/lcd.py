from mux import select_mux_channel

def draw_bar(percent):
    percent = max(0, min(100, percent))
    filled = int(percent / 12.5)      # 8 blocks max
    
    # chr(255) is the hardware code for a solid block on 16x2 LCDs
    solid_block = chr(255) 
    
    return "[" + (solid_block * filled) + (" " * (8 - filled)) + "]"

  # ------------------------------------------
    # UPDATE LCD: SYSTEM PAGINATION (CH 1)
    # ------------------------------------------
def update_lcd(
    lcd,
    i2c,
    page,
    water_percent,
    light_percent,
    pump_on,
    dosing_on,
    wifi_ok,mqtt_ok,
    reservoir_level_cm):
    
    select_mux_channel(i2c, 1)
    lcd.clear()

    # PAGE 1: Bars
    if page == 0:
        lcd.move_to(0,0)
        lcd.putstr("Water")
        lcd.move_to(6,0)
        lcd.putstr(draw_bar(water_percent))
        lcd.move_to(0,1)
        lcd.putstr("Light")
        lcd.move_to(6,1)
        lcd.putstr(draw_bar(light_percent))

    # PAGE 2: Hardware Status
    elif page == 1:
        lcd.move_to(0, 0)
        lcd.putstr("Pump : ")
        lcd.putstr("ON " if pump_on else "OFF")
        lcd.move_to(0, 1)
        lcd.putstr("Dose : ")
        lcd.putstr("ON " if dosing_on else "OFF")

    # PAGE 3: Network Status
    elif page == 2:
        lcd.move_to(0, 0)
        lcd.putstr("WiFi : ")
        lcd.putstr("OK " if wifi_ok else "FAIL")
        lcd.move_to(0, 1)
        lcd.putstr("MQTT : ")
        lcd.putstr("OK " if mqtt_ok else "FAIL")

    # PAGE 4: Alarms
    elif page == 3:
        if reservoir_level_cm > 17:
            lcd.move_to(0, 0)
            lcd.putstr("!! WARNING !!")
            lcd.move_to(0, 1)
            lcd.putstr("LOW WATER")
        else:
            lcd.move_to(0, 0)
            lcd.putstr("System Healthy")
            lcd.move_to(0, 1)
            lcd.putstr("All OK")

    # Increment page and loop back
    page = (page + 1) % 4
    return page

