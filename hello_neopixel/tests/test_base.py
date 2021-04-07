"""Tests for the base class definitions"""
from unittest import TestCase, main

from hello_neopixel import base

from .mockpixel import MockPixel

__all__ = ["TestPixel"]


class TestPixel(TestCase):
    def test_set_value_sets_color_value(self):
        light_strip = MockPixel(1)
        pixel = base.Pixel(light_strip, 0)
        pixel.set((123, 45, 6))
        self.assertEqual((123, 45, 6), light_strip[0])

    def test_set_value_does_not_call_write(self):
        light_strip = MockPixel(1)
        pixel = base.Pixel(light_strip, 0)
        pixel.set((123, 45, 6))
        self.assertEqual(len(light_strip.write_log), 0)

    def test_blank_sets_default_blank_value(self):
        light_strip = MockPixel(1)
        light_strip[0] = (255, 255, 255)
        light_strip.write()

        pixel = base.Pixel(light_strip, 0)
        pixel.blank()
        self.assertEqual((0, 0, 0), light_strip[0])

    def test_blank_does_not_call_write(self):
        light_strip = MockPixel(1)
        light_strip[0] = (255, 255, 255)
        light_strip.write()

        pixel = base.Pixel(light_strip, 0)
        pixel.blank()
        self.assertEqual((255, 255, 255), light_strip.displayed_pixels[0])

    def test_custom_blank(self):
        rgbw_light_strip = [None]
        pixel = base.Pixel(rgbw_light_strip, 0, blank_value=(0, 0, 0, 0))
        pixel.blank()
        self.assertEqual((0, 0, 0, 0), rgbw_light_strip[0])


if __name__ == "__main__":
    main()
