from hello_neopixel import AsciiPixel, Pixel
from hello_neopixel import animations as ani
from hello_neopixel import run_animations

light_strip = AsciiPixel(12, animate=True)
mouth = Pixel(light_strip, 6)
fireball = ani.Fireball(mouth)

mouth.set((128, 0, 0))
fireball.trigger_time = 2.0
run_animations((fireball,), runtime=5.0, clear_after=False)
