"""Tests for the animation managers"""
from unittest import TestCase, main

from hello_neopixel import Animation, Pixel
from hello_neopixel import animations as ani
from hello_neopixel import manager
from hello_neopixel._compat import utime

from .mockpixel import MockPixel

__all__ = ["TestRunAnimations"]


class TestRunAnimations(TestCase):
    def test_writes_once_per_frame_according_to_framerate(self):
        for frame_rate in (12, 24, 36):
            light_strip = MockPixel(1)
            blink = ani.Blink(Pixel(light_strip, 0), (255, 255, 255))
            expected_write_count = 1 + frame_rate // 10  # first is t=0
            manager.run_animations(
                [blink], runtime=0.1, frame_rate=frame_rate, clear_after=False
            )
            self.assertEqual(len(light_strip.write_log), expected_write_count)

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

    def test_can_manage_multiple_animations_on_different_strips(self):
        red_strip = MockPixel(1)
        green_strip = MockPixel(1)
        blink_red = ani.Blink(Pixel(red_strip, 0), (255, 0, 0))
        blink_green = ani.Blink(
            Pixel(green_strip, 0), (0, 255, 0), duty_cycle=0.05
        )
        manager.run_animations(
            [blink_red, blink_green], runtime=0.1, frame_rate=16
        )
        # writes at t=0, once more, then clears
        self.assertEqual(len(red_strip.write_log), 3)
        self.assertEqual(len(green_strip.write_log), 3)

        # blanks when done
        for light_strip in (red_strip, green_strip):
            self.assertEqual(light_strip[0], (0, 0, 0))

        expected_red_write_log = [[(255, 0, 0)], [(255, 0, 0)], [(0, 0, 0)]]
        expected_green_write_log = [[(0, 255, 0)], [(0, 0, 0)], [(0, 0, 0)]]

        # write logs are as expected
        self.assertEqual(red_strip.write_log, expected_red_write_log)
        self.assertEqual(green_strip.write_log, expected_green_write_log)

    def test_writes_only_once_per_strip(self):
        light_strip = MockPixel(2)
        blink_red = ani.Blink(Pixel(light_strip, 0), (255, 0, 0))
        blink_green = ani.Blink(
            Pixel(light_strip, 1), (0, 255, 0), duty_cycle=0.05
        )
        manager.run_animations(
            [blink_red, blink_green],
            runtime=0.1,
            frame_rate=16,
            clear_after=False,
        )
        # writes at t=0, then once more, but does not clear
        self.assertEqual(len(light_strip.write_log), 2)

        expected_write_log = [
            [(255, 0, 0), (0, 255, 0)],
            [(255, 0, 0), (0, 0, 0)],
        ]

        # write logs are as expected
        self.assertEqual(light_strip.write_log, expected_write_log)

    class SleepyAnimation(Animation):
        def __init__(self, pixels, render_time_ms):
            super().__init__(pixels)
            self.render_time_ms = render_time_ms

        def render(self, current_time: float) -> None:
            utime.sleep_ms(self.render_time_ms)
            # yeah, this doesn't actually render anything

    def test_compensates_for_render_times(self):
        for render_time_ms in (5, 10, 45):
            light_strip = MockPixel(1)
            animation = self.SleepyAnimation(
                [Pixel(light_strip, 0)], render_time_ms
            )
            manager.run_animations(
                [animation], runtime=0.31, frame_rate=20, clear_after=False
            )
            self.assertEqual(len(light_strip.write_log), 7)

    def test_does_its_best_when_render_time_exceeds_step_time(self):
        light_strip = MockPixel(1)
        animation = self.SleepyAnimation(
            [Pixel(light_strip, 0)], render_time_ms=50
        )
        manager.run_animations(
            [animation], runtime=0.325, frame_rate=200, clear_after=False
        )
        self.assertEqual(len(light_strip.write_log), 7)


if __name__ == "__main__":
    main()
