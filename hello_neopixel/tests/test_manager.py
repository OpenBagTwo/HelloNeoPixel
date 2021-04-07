"""Tests for the animation managers"""
from unittest import TestCase, main

from hello_neopixel import Pixel
from hello_neopixel import animations as ani
from hello_neopixel import manager

from .mockpixel import MockPixel

__all__ = ["TestRunAnimations"]


class TestRunAnimations(TestCase):
    def test_writes_once_per_frame_according_to_framerate(self):
        light_strip = MockPixel(1)
        blink = ani.Blink(Pixel(light_strip, 0), (255, 255, 255))
        manager.run_animations(
            [blink], runtime=0.1, frame_rate=24, clear_after=False
        )
        self.assertEqual(len(light_strip.write_log), 3)  # (t=0, 1/24, 1/12)

    def test_clears_when_done_by_default(self):
        light_strip = MockPixel(1)
        blink = ani.Blink(Pixel(light_strip, 0), (255, 255, 255))
        manager.run_animations([blink], runtime=0.1, frame_rate=24)
        self.assertEqual(len(light_strip.write_log), 4)  # plus the clear
        self.assertEqual(light_strip[0], (0, 0, 0))

    def test_always_clears_when_done_when_clear_after_is_true(self):
        light_strip = MockPixel(1)
        light_strip[0] = ("I'm on",)
        blink = ani.Blink(
            Pixel(light_strip, 0, blank_value=("I'm off",)),
            ("I'm a different on",),
        )
        manager.run_animations([blink], runtime=-0.1)
        # not doing a write log len test because
        # I don't care if it does an initial write
        self.assertEqual(light_strip[0], ("I'm off",))


if __name__ == "__main__":
    main()
