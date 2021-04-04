"""Library of animations"""
import urandom

from . import utils
from .base import Animation, Pixel
from .manager import run_animations

try:
    random = urandom.random
except AttributeError:
    """Workaround for MicroPython on the desktop not having random.random()"""
    random = (
        lambda: urandom.getrandbits(8) / 2 ** 8
    )  # way more resolution than we need


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
