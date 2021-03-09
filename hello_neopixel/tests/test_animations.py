"""Placeholder for tests for the various animations.
Of course, the best test of any animation is how it looks on the strip."""
from unittest import TestCase, main

import utime

from hello_neopixel import animations as ani


class FakeNeoPixel:
    """Mock NeoPixel to use for testing

    Attributes:
        n (int) : the number of pixels
        write_log (list of list of three-int tuples):
            recording of every set of pixels that were ever written to the strip
    """

    def __init__(self, n_pixels: int) -> None:
        """Initialize a mock light strip

        Args:
            n_pixels (int) : the number of pixels in your virtual strip
        """
        self.n = n_pixels
        self._pending_pixels = [(0, 0, 0) for _ in range(n_pixels)]
        self.write_log = []  # type: list

    def __iter__(self):
        for pixel in self._pending_pixels:
            yield pixel

    def __getitem__(self, index: int) -> tuple:
        return self._pending_pixels[index]

    def __setitem__(self, index: int, value: tuple) -> None:
        # TODO: is typing available for uPython?
        #       alternatively, is there a more primitive way to hint at
        #       "tuple of three ints"?
        self._pending_pixels[index] = value  # type: ignore[assignment]

    def write(self) -> None:
        """Emulate the NeoPixel write operation by "displaying" the set values.
        This is done by logging writing the pending pixels to a log.
        """
        self.write_log.append(list(self))

    @property
    def displayed_pixels(self) -> list:
        """list of three-int tuples :  the pixel RGB values that were last
        "written" to the virtual strip
        """
        if len(self.write_log) == 0:
            return [(0, 0, 0) for i in range(self.n)]
        return self.write_log[-1]


class TestRandomCycle(TestCase):
    def test_runtime_is_in_seconds(self):
        fake_neopixel = FakeNeoPixel(5)
        start = utime.ticks_ms()
        ani.random_cycle(fake_neopixel, runtime=0.1, frame_rate=1000)
        duration = utime.ticks_diff(utime.ticks_ms(), start) / 1000

        assert (
            0.1 <= duration < 0.15  # allow 50ms for computation outside loop
        ), "random_cycle animation ran for {} seconds".format(duration)

    def test_clear_after_leaves_pixels_blank(self):
        fake_neopixel = FakeNeoPixel(5)
        ani.random_cycle(
            fake_neopixel, runtime=0.1, frame_rate=100, clear_after=True
        )

        blank = (0, 0, 0)
        for i in range(fake_neopixel.n):
            assert (
                fake_neopixel.displayed_pixels[i] == blank
            ), "pixel {} was not blanked".format(i)

    def test_clear_after_false_leaves_pixels_illuminated(self):
        """taking advantage of the fact that all random colors are max brightness
        and saturation"""
        fake_neopixel = FakeNeoPixel(5)
        ani.random_cycle(
            fake_neopixel, runtime=0.1, frame_rate=100, clear_after=False
        )
        blank = (0, 0, 0)
        for i in range(fake_neopixel.n):
            assert (
                fake_neopixel.displayed_pixels[i] != blank
            ), "pixel {} was blanked".format(i)

    def test_clear_after_is_default_behavior(self):
        fake_neopixel = FakeNeoPixel(5)
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
        baseline_neopixel = FakeNeoPixel(2)
        ani.random_cycle(baseline_neopixel, runtime=-1, clear_after=False)
        baseline_write_count = len(baseline_neopixel.write_log)

        # doubt I'm actually this memory-limited but shouldn't hurt
        del baseline_neopixel

        fake_neopixel = FakeNeoPixel(2)
        ani.random_cycle(
            fake_neopixel,
            frame_rate=20,  # setting this very low to be micro-CPU friendly
            runtime=0.499,  # slightly less than divisible by frame rate
            clear_after=False,
        )
        self.assertEqual(
            10, len(fake_neopixel.write_log) - baseline_write_count
        )

    def test_colors_are_shifted_by_one_pixel_after_transition_time(self):
        fake_neopixel = FakeNeoPixel(3)
        ani.random_cycle(
            fake_neopixel,
            frame_rate=10,
            transition_time=0.4,  # theoretically 4 frames
            runtime=0.999,
        )  # expecting 10 frames total

        start_frames_to_check = (0, 3, 4, 6)
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
                        " {} and {}".format(start_frame, end_frame)
                    )


if __name__ == "__main__":
    main()
