from machine import Pin, SoftI2C
from i2c_lcd import I2cLcd

# ==========================================
# LCD Configuration
# ==========================================

SDA_PIN = 21
SCL_PIN = 22

LCD_ADDR = 0x27

i2c = SoftI2C(
    scl=Pin(SCL_PIN),
    sda=Pin(SDA_PIN),
    freq=100000
)

lcd = I2cLcd(
    i2c,
    LCD_ADDR,
    2,
    16
)


def startup():

    lcd.clear()

    lcd.move_to(0, 0)
    lcd.putstr("Hydroponics")

    lcd.move_to(0, 1)
    lcd.putstr("Incubator")



def update_display(mode,
                   hour,
                   minute,
                   grow_light):

    lcd.clear()

    lcd.move_to(0, 0)

    lcd.putstr("{} {:02}:{:02}".format(
        mode,
        hour,
        minute
    ))

    lcd.move_to(0, 1)

    if grow_light:
        lcd.putstr("GROW : ON ")
    else:
        lcd.putstr("GROW : OFF")
