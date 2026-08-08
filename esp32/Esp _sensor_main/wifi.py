import network
import time
from config import WIFI_SSID, WIFI_PASSWORD


def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        return wlan

    print("Connecting to Wi-Fi...")

    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    timeout = 15

    while timeout > 0:
        if wlan.isconnected():
            print("Wi-Fi Connected")
            print("IP:", wlan.ifconfig()[0])
            return wlan

        print(".", end="")
        time.sleep(1)
        timeout -= 1

    raise RuntimeError("Wi-Fi connection failed")