"""Tests for utils module"""
from unittest import TestCase

from hello_neopixel import utils


class TestConvertHueToRGB(TestCase):

    parameters = (  # (hue, expected)
        (214, (0, 110, 255)),
        (11, (255, 47, 0)),
        (148, (0, 255, 119)),
    )

    def test_convert_hue_to_rgb_produces_expected_results(self):
        for hue, expected in self.parameters:
            with self.subTest(hue):
                self.assertEqual(expected, utils.convert_hue_to_rgb(hue))

    def test_invalid_hue_handling(self):
        for invalid_value in (-1, 451, "YInMn"):
            with self.subTest(invalid_value):
                self.assertRaises(
                    ValueError, utils.convert_hue_to_rgb, invalid_value
                )
