"""Base class / ABC definitions"""


class Pixel:
    """An encapsulation of an light strip pixel.

    Since NeoPixel color values are generally written via direct assignment,
    e.g.

        >>> light_strip[i] = (255, 255, 255))

    it's difficult to work with individual pixels by reference. For example,
    you can't, say, blank a strip via:

        >>> for pixel in light_strip:
        ...     pixel = (0, 0, 0)

    let alone easily work with pixels on different strips.

    This class attempts to solve for that by taking a light strip and the index
    of an LED on that strip, wrapping them, and providing an access method
    for setting their values, a la

        >>> for pixel in pixels:
        ...    pixel.set((0, 255, 0))

    """

    def __init__(
        self, light_strip, index: int, blank_value: tuple = (0, 0, 0)
    ) -> None:
        """Args:

        Args:
            light_strip (NeoPixel): the light strip containing the pixel
            index (int): the index of the LED on the light strip
            blank_value (tuple, optional):
                the value of the pixel that corresponds to blank / off. If
                None is specified, an RGB pixel will be assumed with a blank
                value of (0, 0, 0).
        """
        self.light_strip = light_strip
        self._index = index
        self._blank_value = blank_value

    def set(self, color: tuple) -> None:
        """Set the pixel's color value

        Args:
            color (tuple of ints): the color to give to the pixel. Generally
                                   this should be a three-tuple of RGB
                                   values, though other formats (RGBW) would
                                   be supported.

        Returns:
            None

        Notes:
            This function does not actually "write" the new color (that is,
            calling this method alone will not update the color displayed on the
            light strip).
        """
        self.light_strip[self._index] = color

    def blank(self) -> None:
        """Blank the pixel (set the color to "off")

        Notes:
            This function does not actually "write" the off command (that is,
            calling this method alone will not turn off the pixel).
        """
        self.set(self._blank_value)


class Animation:
    """Abstract definition of an animation.

    Attributes:
        pixels (list of Pixels) : The list of pixels that will be used to render
        the animation
    """

    def __init__(self, pixels) -> None:
        """Initialize an animation by giving it a light strip and a range of
        pixels for it to control on that strip

        Args:
            pixels (list-like of Pixels):
                The pixels that will be used to render the animation. They do
                not necessarily need to be on the same strip.
        """
        self.pixels = list(pixels)

    def render(self, current_time: float) -> None:
        """Set the color values for each pixel, based on the time since the
        animation began. This will necessarily be different for each animation.

        Args:
            current_time (float) : the time (in seconds) since the animation
                                   started

        Returns:
            None

        Note:
            This function *should not* actually "write" the color values (that
            is, update what's displayed on the actual light strip)--that
            should be left to the animation runner.
        """
        raise NotImplementedError
