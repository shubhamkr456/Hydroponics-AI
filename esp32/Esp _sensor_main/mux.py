from machine import I2C
import time

MUX_ADDR = 0x70


def select_mux_channel(i2c, channel):

    if channel < 0 or channel > 7:
        return

    i2c.writeto(MUX_ADDR, bytes([1 << channel]))

    time.sleep_ms(20)