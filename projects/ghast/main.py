"""Example main.py for controlling the ghast described in this project"""
import network
from blynklib_mp import Blynk
from machine import UART, Pin
from neopixel import NeoPixel

from hello_neopixel import RGBLED, Pixel

from .ghast import Ghast
from .secrets import BLYNK_TOKEN, WIFI_PASS, WIFI_SSID

EYES_GPIO = 19
MOUTH_GPIO = 21
UART_BUS = 2
mouth = Pixel(NeoPixel(Pin(MOUTH_GPIO), 1), 0)
eyes = RGBLED(Pin(EYES_GPIO)).to_pixel()
uart = UART(2, baudrate=9600)  # Using RX2 / TX2

sure_shot_sally = Ghast(eyes, mouth, uart)

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

ghast_app = Blynk(BLYNK_TOKEN)

sure_shot_sally.register_app(ghast_app)

sure_shot_sally.run()
