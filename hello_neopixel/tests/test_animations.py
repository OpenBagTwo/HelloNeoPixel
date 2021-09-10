"""Tests for the various animations.
Of course, the best test of any animation is how it looks on the strip."""
from unittest import TestCase, main

from hello_neopixel import animations as ani
from hello_neopixel._compat import utime
from hello_neopixel.base import Pixel

from .mockpixel import MockPixel

__all__ = ["TestBlink", "TestRunRandomCycle", "TestBeeFace", "TestRunBeeFace"]


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


# dedicated tests for the RandomCycle animation class would go here
# but all important functionality should be covered by the runner tests


class TestRunRandomCycle(TestCase):
    def test_runtime_is_in_seconds(self):
        fake_neopixel = MockPixel(5)
        start = utime.ticks_ms()
        ani.random_cycle(fake_neopixel, runtime=0.1, frame_rate=100)
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
        # taking advantage of the fact that all random colors are
        # max brightness and saturation
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
        fake_neopixel = MockPixel(2)
        ani.random_cycle(
            fake_neopixel,
            frame_rate=60,
            runtime=0.166,  # slightly less than divisible by frame rate
            clear_after=False,
        )

        # should write at t=0 then step forward 9 times before terminating
        self.assertEqual(len(fake_neopixel.write_log), 10)

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

    def test_accepts_a_list_of_pixels(self):
        fake_neopixel = MockPixel(5)
        light_strip = [Pixel(fake_neopixel, i) for i in range(5)]
        ani.random_cycle(
            light_strip, runtime=0.1, frame_rate=100, clear_after=False
        )
        blank = (0, 0, 0)
        for i in range(fake_neopixel.n):
            assert (
                fake_neopixel.displayed_pixels[i] != blank
            ), "pixel {} was blank".format(i)


class TestBeeFace(TestCase):
    def test_accepts_exactly_twelve_pixels(self):
        light_strip = MockPixel(100)
        another_light_strip = MockPixel(6)

        test_cases = (
            ("contiguous strip", (Pixel(light_strip, i) for i in range(12))),
            (
                "discontiguous strip",
                (
                    Pixel(light_strip, i)
                    for i in (0, 1, 3, 8, 12, 16, 19, 50, 32, 6, 99, 42)
                ),
            ),
            (
                "separate strips",
                [Pixel(light_strip, i) for i in range(6)]
                + [Pixel(another_light_strip, 5 - i) for i in range(6)],
            ),
            ("repeated_pixels", [Pixel(light_strip, 0)] * 12),
        )

        for case_name, pixel_list in test_cases:
            try:
                bee_face = ani.BeeFace(pixel_list)
                mismatches = []
                for i, pixel in enumerate(pixel_list):
                    if bee_face.pixels[i] is not pixel:
                        mismatches.append(i)
            except Exception as error:
                raise AssertionError(
                    "Could not create animation using {}".format(case_name)
                ) from error

            if len(mismatches) > 0:
                raise AssertionError(
                    "Pixels {} on {} did not get correctly assigned".format(
                        mismatches, case_name
                    )
                )

    def test_raises_when_the_wrong_number_of_pixels_is_provided(self):
        light_strip = MockPixel(100)

        for n_pixels in (0, 11, 13, 100):
            self.assertRaises(
                ValueError,
                ani.BeeFace,
                [Pixel(light_strip, i) for i in range(n_pixels)],
            )

    def test_that_the_following_tests_wont_always_pass(self):
        """gotta love meta-tests..."""
        self.assertNotEqual(
            ani.BeeFace.ANGRY_CHEEK[0], ani.BeeFace.PASSIVE_CHEEK[0]
        )

    def test_works_after_a_ton_of_cycles(self):
        light_strip = MockPixel(12)
        bee_face = ani.BeeFace([Pixel(light_strip, i) for i in range(12)])

        bee_face.render(282.3)
        self.assertEqual(light_strip[0], ani.BeeFace.PASSIVE_CHEEK[0])
        self.assertEqual(light_strip[11], ani.BeeFace.PASSIVE_CHEEK[0])
        bee_face.render(78927.9)
        self.assertEqual(light_strip[0], ani.BeeFace.ANGRY_CHEEK[0])
        self.assertEqual(light_strip[11], ani.BeeFace.ANGRY_CHEEK[0])

    def test_can_have_a_custom_period(self):
        light_strip = MockPixel(12)
        ani.BeeFace(
            [Pixel(light_strip, i) for i in range(12)], period=100
        ).render(60.9)
        self.assertEqual(light_strip[0], ani.BeeFace.PASSIVE_CHEEK[0])
        self.assertEqual(light_strip[11], ani.BeeFace.PASSIVE_CHEEK[0])

    def test_can_have_a_custom_duty_cycle(self):
        light_strip = MockPixel(12)
        ani.BeeFace(
            [Pixel(light_strip, i) for i in range(12)], duty_cycle=0.1
        ).render(1.8)

        self.assertEqual(light_strip[0], ani.BeeFace.ANGRY_CHEEK[0])
        self.assertEqual(light_strip[11], ani.BeeFace.ANGRY_CHEEK[0])


class TestRunBeeFace(TestCase):
    def test_runtime_is_in_seconds(self):
        fake_neopixel = MockPixel(12)
        start = utime.ticks_ms()
        ani.bee_face(fake_neopixel, runtime=0.1, frame_rate=100)
        duration = utime.ticks_diff(utime.ticks_ms(), start) / 1000

        assert (
            0.1 <= duration < 0.15  # allow 50ms for computation outside loop
        ), "bee_cycle animation ran for {} seconds".format(duration)

    def test_clear_after_leaves_pixels_blank(self):
        fake_neopixel = MockPixel(12)
        ani.bee_face(
            fake_neopixel, runtime=0.1, frame_rate=100, clear_after=True
        )

        blank = (0, 0, 0)
        for i in range(fake_neopixel.n):
            assert (
                fake_neopixel.displayed_pixels[i] == blank
            ), "pixel {} was not blanked".format(i)

    def test_clear_after_false_leaves_pixels_illuminated(self):
        # taking advantage of the fact that the angry bee face has no BLACK vals
        fake_neopixel = MockPixel(12)
        ani.bee_face(
            fake_neopixel,
            runtime=0.1,
            frame_rate=100,
            period=0.2,
            duty_cycle=0.3,
            clear_after=False,
        )
        blank = (0, 0, 0)
        for i in range(fake_neopixel.n):
            assert (
                fake_neopixel.displayed_pixels[i] != blank
            ), "pixel {} was blanked".format(i)

    def test_clear_after_is_default_behavior(self):
        fake_neopixel = MockPixel(12)
        ani.bee_face(fake_neopixel, runtime=0.1, frame_rate=100)

        blank = (0, 0, 0)
        for i in range(fake_neopixel.n):
            assert (
                fake_neopixel.displayed_pixels[i] == blank
            ), "pixel {} was not blanked".format(i)

    def test_pixels_are_written_according_to_the_framerate(self):
        fake_neopixel = MockPixel(12)
        ani.bee_face(
            fake_neopixel,
            frame_rate=60,
            runtime=0.166,  # slightly less than divisible by frame rate
            clear_after=False,
        )

        # should write at t=0 then step forward 9 times before terminating
        self.assertEqual(len(fake_neopixel.write_log), 10)

    def test_accepts_a_list_of_pixels(self):
        fake_neopixel = MockPixel(12)
        light_strip = [Pixel(fake_neopixel, 11 - i) for i in range(12)]
        ani.bee_face(
            light_strip,
            runtime=0.1,
            period=0.11,
            frame_rate=100,
            clear_after=False,
        )
        blank = (0, 0, 0)
        for i in range(fake_neopixel.n):
            assert (
                fake_neopixel.displayed_pixels[i] != blank
            ), "pixel {} was blank".format(i)


if __name__ == "__main__":
    main()
