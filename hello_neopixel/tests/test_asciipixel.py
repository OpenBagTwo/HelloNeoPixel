from io import StringIO
from unittest import TestCase, main

from hello_neopixel import asciipixel

__all__ = ["TestConvertRGBToANSIEscape", "TestAsciiPixel"]


class TestConvertRGBToANSIEscape(TestCase):
    def test_background_coloring(self):

        self.assertEqual(
            asciipixel.convert_rgb_to_ansi_escape((123, 234, 56), "background"),
            "\033[48;2;123;234;56m",
        )

    def test_text_coloring(self):
        for color_arg in ("foreground", "text"):
            self.assertEqual(
                asciipixel.convert_rgb_to_ansi_escape((30, 0, 255), color_arg),
                "\033[38;2;30;0;255m",
            )

    def test_unrecognized_color_arg_raises_value_error(self):
        for color_arg in ("baground", "fg", "character", "all", "blink"):
            self.assertRaises(
                ValueError,
                asciipixel.convert_rgb_to_ansi_escape,
                (6, 6, 6),
                color_arg,
            )

    def test_color_arg_is_required(self):
        self.assertRaises(
            TypeError, asciipixel.convert_rgb_to_ansi_escape, (255, 255, 255)
        )


class TestAsciiPixel(TestCase):
    def test_setting_strip_length(self):
        light_strip = asciipixel.AsciiPixel(4)
        self.assertEqual(light_strip.n, 4)
        self.assertEqual(len(light_strip), 4)

    def test_default_pixel_value_is_black(self):
        black = (0, 0, 0)
        light_strip = asciipixel.AsciiPixel(7)
        for i in range(7):
            assert (
                light_strip[i] == black
            ), "Pixel {} was initialized to {}".format(i, light_strip[i])

    def test_writes_the_correct_number_of_pixels(self):
        testing_io = StringIO()
        light_strip = asciipixel.AsciiPixel(16)
        for i in range(16):
            light_strip[i] = (
                255 * (i % 3 == 0),
                255 * (i % 3 == 1),
                255 * (i % 3 == 2),
            )

        light_strip.write(output_to=testing_io)

        testing_io.seek(0)  # rewind
        output = testing_io.read()
        self.assertEqual(output.count(asciipixel.PIXEL_CHARACTER), 16)

    def test_writes_the_correct_number_and_size_of_spacers(self):
        testing_io = StringIO()
        light_strip = asciipixel.AsciiPixel(7, pixel_spacing=4)
        for i in range(7):
            light_strip[i] = ((400 * i) % 255, (70 * i + 160) % 255, 0)

        light_strip.write(output_to=testing_io)

        testing_io.seek(0)  # rewind
        output = testing_io.read()
        self.assertEqual(output.count("    "), light_strip.n + 1)
        # if spacers were larger than intended, the above might still be true
        self.assertEqual(output.count("     "), 0)

    def test_default_writes_end_in_newline(self):
        testing_io = StringIO()
        light_strip = asciipixel.AsciiPixel(2)
        for i in range(2):
            light_strip[i] = (128, 128, 255)

        light_strip.write(output_to=testing_io)

        testing_io.seek(0)  # rewind
        output = testing_io.read()
        assert output.endswith("\n"), (
            "Write sequence was" "\n{}" "\nand didn't end with a newline"
        ).format(repr(output))

    def test_animate_mode_writes_end_in_carriage_return(self):
        testing_io = StringIO()
        light_strip = asciipixel.AsciiPixel(2, animate=True)
        for i in range(2):
            light_strip[i] = (0, 255, 0)

        light_strip.write(output_to=testing_io)

        testing_io.seek(0)  # rewind
        output = testing_io.read()
        assert output.endswith("\r"), (
            "Write sequence was"
            "\n{}"
            "\nand didn't end with a carriage return"
        ).format(repr(output))

    def test_animate_mode_can_be_altered_mid_animation(self):
        testing_io = StringIO()
        light_strip = asciipixel.AsciiPixel(2, animate=True)
        for i in range(2):
            light_strip[i] = (255, 255, 255)

        light_strip.write(output_to=testing_io)

        light_strip.animate_mode = False

        for i in range(2):
            light_strip[i] = (0, 0, 0)

        light_strip.write(output_to=testing_io)

        testing_io.seek(0)  # rewind
        output = testing_io.read()
        frames = [
            "\x1b[48" + frame
            # bg sequence should only be written once per frame
            # (I guess this tests that)
            for frame in output.split("\x1b[48")[1:]
        ]
        for frame_num, expected_end in enumerate(("\r", "\n")):
            frame = frames[frame_num]
            assert frame.endswith(expected_end), (
                "Frame {} was\n{}\nand didn't end with {}"
            ).format(frame_num, repr(frame), repr(expected_end))

    def test_writes_end_in_reset_sequence(self):
        testing_io = StringIO()
        for animate in (True, False):
            light_strip = asciipixel.AsciiPixel(2, animate=animate)
            for i in range(2):
                light_strip[i] = (255, 0, 0)

            light_strip.write(output_to=testing_io)

            testing_io.seek(0)  # rewind
            output = testing_io.read()
            assert output[:-1].endswith(  # ignore newline / carriage return
                asciipixel.RESET_SEQUENCE
            ), (
                "With animate={}, write sequence was"
                "\n{}"
                "\nand didn't end in the reset sequence"
            ).format(
                animate, repr(output)
            )


if __name__ == "__main__":
    main()
