"""Mock NeoPixel definition for use in tests"""


class MockPixel:
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
