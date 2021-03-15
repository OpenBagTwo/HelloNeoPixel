"""Library of animations"""
import urandom
import utime

from . import utils

try:
    random = urandom.random
except AttributeError:
    """Workaround for MicroPython on the desktop not having random.random()"""
    random = (
        lambda: urandom.getrandbits(8) / 2 ** 8
    )  # way more resolution than we need


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
        """
        self.light_strip[self._index] = color

    def blank(self) -> None:
        """Blank (turn off) the pixel"""
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
            This function *should not* actually "write" the color values--that
            should be left to the animation runner.
        """
        raise NotImplementedError


def run_animations(
    animations,
    runtime: float = None,
    frame_rate: float = 60.0,
    clear_after: bool = True,
) -> None:
    """Run one or more animations for a length of time.

    Args:
        animations (list-like of Animations): the animations to execute
        runtime (float, optional): how long the animation should run before
                                   terminating (in seconds). If None is
                                   specified, the animation will run
                                   forever.
        frame_rate (float, optional): how many times per second to render the
                                      animations. Default is 60 fps.
        clear_after (bool, optional): whether to turn off all the LED lights
                                      once the animation ends. Default is True.

    Returns:
        None
    """
    # assumes no animations share pixels, but tbh it's not a big deal if they do
    pixels = sum(
        [animation.pixels for animation in animations], []
    )  # type: list

    light_strips = {pixel.light_strip for pixel in pixels}

    step_time_us = int(1e6 / frame_rate)  # microseconds between steps

    start_time = utime.ticks_ms()

    try:
        while True:
            step_start_tick_us = utime.ticks_us()
            current_time = utime.ticks_diff(utime.ticks_ms(), start_time) / 1000
            for animation in animations:
                animation.render(current_time)

            for light_strip in light_strips:
                light_strip.write()
            # TODO: see if uPython has math.nan
            if (
                runtime is not None
                and current_time + step_time_us / 1e6 > runtime
            ):
                break

            compute_time_us = utime.ticks_us() - step_start_tick_us

            utime.sleep_us(step_time_us - compute_time_us)
    finally:
        if clear_after:
            for pixel in pixels:
                pixel.blank()
            for light_strip in light_strips:
                light_strip.write()


class RandomCycle(Animation):
    """An animation which starts by generating a random color for each pixel
    on the strip and then moves each color around the strip in a loop.

    Attributes:
        colors (list of three-int tuples): the colors used for the animation
    """

    def __init__(self, pixels, transition_time: float = 1.0):
        """Initialize the animation

        Args:
            pixels (list-like of Pixels):
                the pixels that will be used to render the animation. They do
                not necessarily need to be on the same strip.
            transition_time (float, optional):
                how many seconds it should take for a color to move from one
                pixel to the next. Defaults to 1.0 seconds.
        """
        super().__init__(pixels)

        self.transition_time = transition_time

        self.colors = []

        for i in range(len(pixels)):
            hue = int(random() * 360)
            rgb = utils.convert_hue_to_rgb(hue)
            self.colors.append(rgb)

    def render(self, current_time: float) -> None:
        shifts = current_time / self.transition_time
        pixel_shift = int(shifts) % len(self.pixels)

        shift_progress = shifts % 1

        for i, pixel in enumerate(self.pixels):
            pixel.set(
                utils.crossfade(
                    self.colors[(i + pixel_shift) % len(self.pixels)],
                    self.colors[(i + pixel_shift + 1) % len(self.pixels)],
                    progress=shift_progress,
                )
            )


def random_cycle(
    light_strip,  # TODO: hint as NeoPixel without importing neopixel
    runtime: float = None,
    transition_time: float = 1.0,
    frame_rate: float = 60.0,
    clear_after: bool = True,
) -> None:
    """Generates a random color for each pixel and cycles them across the strip

    Args:
        light_strip (NeoPixel): the individually addressable light strip
        runtime (float, optional): how long the animation should run before
                                   terminating (in seconds). If None is
                                   specified, the animation will run
                                   forever.
        transition_time (float, optional): how many seconds it should take for a
                                           color to move from one pixel to the
                                           next. Defaults to 1.0 seconds.
        frame_rate (float, optional): how many times per second to render the
                                      animation. Default is 60 fps.
        clear_after (bool, optional): whether to turn off all the LED lights
                                      once the animation ends. Default is True.

    Returns:
        None
    """
    pixels = [Pixel(light_strip, i) for i in range(light_strip.n)]
    animation = RandomCycle(pixels, transition_time)
    run_animations([animation], runtime, frame_rate, clear_after)
