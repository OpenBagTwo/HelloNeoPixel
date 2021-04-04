"""Tests for the various animations.
Of course, the best test of any animation is how it looks on the strip."""
from unittest import TestCase, main

import utime

from hello_neopixel import animations as ani
from hello_neopixel.base import Pixel

from .mockpixel import MockPixel

__all__ = ["TestBlink", "TestRandomCycle"]


class TestBlink(TestCase):
    def test_blink_takes_a_single_pixel(self):
        light_strip = [None]
        pixel = Pixel(light_strip, 0)
        blink = ani.Blink(pixel, (255, 255, 255))
        self.assertIs(blink.pixels[0], pixel)

    def test_blink_sets_the_specified_color(self):
        light_strip = [None]
        pixel = Pixel(light_strip, 0)
        blink = ani.Blink(pixel, ("magenta",))
        blink.render(0.2)
        self.assertEqual(light_strip[0], ("magenta",))

    def test_blink_respects_custom_blanks(self):
        light_strip = [None]
        pixel = Pixel(light_strip, 0, blank_value=("turn", "me", "off"))
        blink = ani.Blink(pixel, (12, 34, 56))
        blink.render(0.7)
        self.assertEqual(light_strip[0], ("turn", "me", "off"))

    def test_blink_works_after_a_ton_of_cycles(self):
        light_strip = [None]
        pixel = Pixel(light_strip, 0, blank_value=(0,))
        blink = ani.Blink(pixel, (1,))
        blink.render(228.3)
        self.assertEqual(light_strip[0], (1,))
        blink.render(78927.9)
        self.assertEqual(light_strip[0], (0,))

    def test_blink_can_have_a_custom_period(self):
        light_strip = [None]
        pixel = Pixel(light_strip, 0, blank_value=(0,))
        blink = ani.Blink(pixel, (1,), period=100.0)
        blink.render(48.9)
        self.assertEqual(light_strip[0], (1,))

    def test_blink_can_have_a_custom_duty_cycle(self):
        light_strip = [None]
        pixel = Pixel(light_strip, 0, blank_value=(0,))
        blink = ani.Blink(pixel, (1,), duty_cycle=0.1)
        blink.render(0.2)
        self.assertEqual(light_strip[0], (0,))


class TestRandomCycle(TestCase):
    def test_runtime_is_in_seconds(self):
        fake_neopixel = MockPixel(5)
        start = utime.ticks_ms()
        ani.random_cycle(fake_neopixel, runtime=0.1, frame_rate=1000)
        duration = utime.ticks_diff(utime.ticks_ms(), start) / 1000

        assert (
            0.1 <= duration < 0.15  # allow 50ms for computation outside loop
        ), "random_cycle animation ran for {} seconds".format(duration)

    def test_clear_after_leaves_pixels_blank(self):
        fake_neopixel = MockPixel(5)
        ani.random_cycle(
            fake_neopixel, runtime=0.1, frame_rate=100, clear_after=True
        )

        blank = (0, 0, 0)
        for i in range(fake_neopixel.n):
            assert (
                fake_neopixel.displayed_pixels[i] == blank
            ), "pixel {} was not blanked".format(i)

    def test_clear_after_false_leaves_pixels_illuminated(self):
        """taking advantage of the fact that all random colors are
        max brightness and saturation"""
        fake_neopixel = MockPixel(5)
        ani.random_cycle(
            fake_neopixel, runtime=0.1, frame_rate=100, clear_after=False
        )
        blank = (0, 0, 0)
        for i in range(fake_neopixel.n):
            assert (
                fake_neopixel.displayed_pixels[i] != blank
            ), "pixel {} was blanked".format(i)

    def test_clear_after_is_default_behavior(self):
        fake_neopixel = MockPixel(5)
        ani.random_cycle(fake_neopixel, runtime=0.1, frame_rate=100)

        blank = (0, 0, 0)
        for i in range(fake_neopixel.n):
            assert (
                fake_neopixel.displayed_pixels[i] == blank
            ), "pixel {} was not blanked".format(i)

    def test_pixels_are_written_according_to_the_framerate(self):

        # first run a neopixel that should terminate immediately
        # (to account for the fact that the animation MAY OR MAY NOT display
        # once before checking the time)
        baseline_neopixel = MockPixel(2)
        ani.random_cycle(baseline_neopixel, runtime=-1, clear_after=False)
        baseline_write_count = len(baseline_neopixel.write_log)

        # doubt I'm actually this memory-limited but shouldn't hurt
        del baseline_neopixel

        fake_neopixel = MockPixel(2)
        ani.random_cycle(
            fake_neopixel,
            frame_rate=60,
            runtime=0.166,  # slightly less than divisible by frame rate
            clear_after=False,
        )

        # so not counting that (maybe) first write, we expect it to step
        # forward 9 times before terminating
        self.assertEqual(len(fake_neopixel.write_log) - baseline_write_count, 9)

    def test_colors_are_shifted_by_one_pixel_after_transition_time(self):
        fake_neopixel = MockPixel(3)
        ani.random_cycle(
            fake_neopixel,
            frame_rate=20,
            transition_time=0.2,  # theoretically 4 frames
            runtime=0.499,
        )  # expecting 10 frames total

        start_frames_to_check = (0, 3, 4, 5)
        for start_frame in start_frames_to_check:
            end_frame = start_frame + 4
            for i in range(fake_neopixel.n):
                start_pixel = fake_neopixel.write_log[start_frame][i]
                end_pixel = fake_neopixel.write_log[end_frame][
                    (i - 1) % fake_neopixel.n
                ]
                for j in range(3):
                    # allow a little wiggle room
                    assert abs(start_pixel[j] - end_pixel[j]) < 10, (
                        "Pixels not properly shifted between frames"
                        " {} and {}."
                        "\nFor example, at the latter frame,"
                        " pixel {} is {} when it should be {}".format(
                            start_frame, end_frame, i, start_pixel, end_pixel
                        )
                    )


if __name__ == "__main__":
    main()
