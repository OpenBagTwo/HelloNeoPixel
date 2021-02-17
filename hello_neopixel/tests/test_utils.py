"""Tests for utils module"""
from unittest import TestCase, main

from hello_neopixel import utils

__all__ = ["TestConvertHueToRGB", "TestCrossfade"]


class TestConvertHueToRGB(TestCase):

    parameters = (  # (hue, expected)
        (214, (0, 110, 255)),
        (11, (255, 47, 0)),
        (148, (0, 255, 119)),
    )

    def test_convert_hue_to_rgb_produces_expected_results(self):
        for hue, expected in self.parameters:
            self.assertEqual(expected, utils.convert_hue_to_rgb(hue))

    def test_invalid_hues_raise_errors(self):
        for invalid_value in (-1, 451, "YInMn"):
            self.assertRaises(
                ValueError, utils.convert_hue_to_rgb, invalid_value
            )


class TestCrossfade(TestCase):
    def test_crossfade_produces_color_between_provided_colors(self):
        progress = 0.3

        old_color = (255, 115, 0)
        new_color = (127, 0, 255)

        faded = utils.crossfade(old_color, new_color, progress=progress)

        assert new_color[0] < faded[0] < old_color[0], "R not in expected range"
        assert new_color[1] < faded[1] < old_color[1], "G not in expected range"
        assert old_color[2] < faded[2] < new_color[2], "B not in expected range"

    def test_crossfade_under_half_produces_color_closer_to_the_old_color(self):
        progress = 0.2

        old_color = (118, 255, 0)
        new_color = (48, 0, 255)

        faded = utils.crossfade(old_color, new_color, progress=progress)

        for i in range(3):
            assert abs(old_color[i] - faded[i]) < abs(
                new_color[i] - faded[i]
            ), "Faded {} is closer to new color".format("RGB"[i])

    def test_flipped_crossfades_are_equivalent(self):
        progress = 0.8

        old_color = (255, 0, 7)
        new_color = (254, 255, 0)

        original_fade = utils.crossfade(old_color, new_color, progress=progress)

        reversed_fade = utils.crossfade(
            new_color, old_color, progress=1.0 - progress
        )

        self.assertEqual(original_fade, reversed_fade)

    def test_zero_progress_results_in_old_color(self):

        old_color = (0, 255, 215)
        new_color = (255, 146, 0)

        faded = utils.crossfade(old_color, new_color, progress=0)

        self.assertEqual(old_color, faded)

    def test_hundred_percent_progress_results_in_new_color(self):

        old_color = (176, 255, 0)
        new_color = (255, 28, 0)

        faded = utils.crossfade(old_color, new_color, progress=1.0)

        self.assertEqual(new_color, faded)

    def test_invalid_progress_raises_error(self):

        for invalid_value in (-0.1, 32, "congress"):
            self.assertRaises(
                ValueError,
                utils.crossfade,
                (255, 0, 0),
                (0, 255, 0),
                progress=invalid_value,
            )


if __name__ == "__main__":
    main()
