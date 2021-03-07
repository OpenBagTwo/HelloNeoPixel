"""Placeholder for tests for the various animations.
Of course, the best test of any animation is how it looks on the strip."""
from unittest import TestCase, main

from hello_neopixel import animations as ani  # noqa: F401


class FakeNeoPixel:
    """Mock NeoPixel to use for testing

    Attributes:
        n (int) : the number of pixels
        _pending_pixels (tuple of three ints) : the set pixel values, pending
                                                a write()
        _live_pixels (tuple of three ints) : the pixel colors that are actually
                                             being displayed
    """

    def __init__(self, n_pixels: int) -> None:
        """Initialize a mock light strip

        Args:
            n_pixels (int) : the number of pixels in your virtual strip
        """
        self.n = n_pixels
        self._pending_pixels = [(0, 0, 0) for _ in range(n_pixels)]
        self._live_pixels = [(0, 0, 0) for _ in range(n_pixels)]

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

    def write(self):
        for i in range(self.n):
            self._live_pixels[i] = self._pending_pixels[i]


class TestRandomCycle(TestCase):
    # TODO
    pass


if __name__ == "__main__":
    main()
