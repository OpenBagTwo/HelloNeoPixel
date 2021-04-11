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


class Blink(Animation):
    """Probably the simplest possible animation. Blinks a single pixel a single
    color on and off.

    Attributes:
        color: the color used for the animation
    """

    def __init__(
        self,
        pixel: Pixel,
        color: tuple,
        period: float = 1.0,
        duty_cycle: float = 0.5,
    ) -> None:
        """Initialize the animation

        Args:
            pixel (Pixel):
                the pixel (LED) to be used
            color (tuple of three ints for RGB):
                the "on" color for the pixel
            period (float):
                The time (in seconds) for a complete on/off cycle.
                Default is 1.0 seconds.
            duty_cycle (float):
                The fraction (between 0 and 1) of the time the pixel should be
                on. Default is 0.5 (equal times on and off).
        """
        super().__init__((pixel,))
        self.color = color
        self.period = period
        self.duty_cycle = duty_cycle

    def render(self, current_time: float) -> None:
        cycle_point = (current_time % self.period) / self.period
        if cycle_point < self.duty_cycle:
            self.pixels[0].set(self.color)
        else:
            self.pixels[0].blank()


class RandomCycle(Animation):
    """An animation which starts by generating a random color for each pixel
    on the strip and then moves each color around the strip in a loop.

    Attributes:
        colors (list of three-int tuples): the colors used for the animation
    """

    def __init__(self, pixels, transition_time: float = 1.0) -> None:
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
    light_strip,
    runtime: float = None,
    transition_time: float = 1.0,
    frame_rate: float = 60.0,
    clear_after: bool = True,
) -> None:
    """Generates a random color for each pixel and cycles them across the strip

    Args:
        light_strip (NeoPixel or list-like of Pixels):
            the individually addressable light strip
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
    if isinstance(light_strip[0], Pixel):
        pixels = light_strip
    else:
        pixels = [Pixel(light_strip, i) for i in range(light_strip.n)]
    animation = RandomCycle(pixels, transition_time)
    run_animations([animation], runtime, frame_rate, clear_after)


class BeeFace(Animation):
    """A two-frame animation for a Minecraft bee face where the cheeks are
    illuminated using individual NeoPixels. The animation alternates the bee's
    face between passive and angry.

    The face is on a 6 x 5 square grid laid out as follows:

    + -- + -- + -- + -- + -- +
    | YL | YL | YL | YL | YL |
    | YL | BK | YL | BL | YL |
    | YL | YL | YL | YL | YL |
    |  4 |  5 | YL |  6 |  7 |
    |  3 |  2 | YL |  9 |  8 |
    |  0 |  1 | YL | 11 | 10 |
    + -- + -- + -- + -- + -- +

    where cells:
      - marked YL are colored yellow
      - cells marked BK are colored black
      - cells marked BL are colored blue
      - cells colored RD are colored red
      - cells colored WT are colored white
      - numbered cells are transparent and backed by an individually addressable
        LED.

    The two frames of the animation are:

    Passive:                          Angry:
    + -- + -- + -- + -- + -- +        + -- + -- + -- + -- + -- +
    | YL | YL | YL | YL | YL |        | YL | YL | YL | YL | YL |
    | YL | BK | YL | BL | YL |        | YL | BK | YL | BL | YL |
    | YL | YL | YL | YL | YL |        | YL | YL | YL | YL | YL |
    | BK | BL | YL | BL | BK |        | RD | WT | YL | WT | RD |
    | BK | BK | YL | BK | BK |        | RD | RD | YL | RD | RD |
    | BK | BK | YL | BK | BK |        | YL | YL | YL | YL | YL |
    + -- + -- + -- + -- + -- +        + -- + -- + -- + -- + -- +

    And thus, the LEDs need to be colored:

    Passive:
        [BK, BK, BK, BK, BK, BL, BL, BK, BK, BK, Bk, BK]
    Angry:
        [YL, YL, RD, RD, RD, WT, WT, RD, RD, RD, YL, YL]
    """

    BLACK = (0, 0, 0)
    WHITE = (50, 50, 50)
    RED = (150, 0, 0)
    BLUE = (10, 70, 70)
    YELLOW = (80, 60, 0)

    # take advantage of the fact that the cheeks are symmetric
    PASSIVE_CHEEK = (BLACK, BLACK, BLACK, BLACK, BLACK, BLUE)
    ANGRY_CHEEK = (YELLOW, YELLOW, RED, RED, RED, WHITE)

    def __init__(
        self, pixels, period: float = 10.0, duty_cycle: float = 0.7
    ) -> None:
        """Initialize the animation

        Args:
            pixels (list-like of 12 Pixels):
                The pixels that will be used to render the animation. The can be
                attached to different GPIO pins, but they must be indexed in the
                list according to the above diagram.
            period (float, optional):
                The time (in seconds) for a complete passive/angry cycle.
                Default is 10.0 seconds.
            duty_cycle (float, optional):
                The fraction (between 0 and 1) of the time the bee face should
                be "passive". Default is 0.7 (7s passive to 3s angry).
        """
        super().__init__(pixels)
        if len(self.pixels) != 12:
            raise ValueError("This animation requires exactly 12 pixels.")
        self.period = period
        self.duty_cycle = duty_cycle

    def render(self, current_time: float) -> None:
        cycle_point = (current_time % self.period) / self.period
        if cycle_point < self.duty_cycle:
            cheek = self.PASSIVE_CHEEK
        else:
            cheek = self.ANGRY_CHEEK

        for i in range(6):
            self.pixels[i].set(cheek[i])
            self.pixels[11 - i].set(cheek[i])


def bee_face(
    light_strip,
    runtime: float = None,
    period: float = None,
    duty_cycle: float = None,
    frame_rate: float = 1,
    clear_after: bool = True,
) -> None:
    """Display the bee cycle animation

    Args:
        light_strip (NeoPixel or list-like of Pixels):
            The individually addressable light strip. If a NeoPixel is provided,
            the assumption is that the animation should display on the first
            twelve pixels, so if that's not what you want, you'll need to
            generate your own Pixel list.
        runtime (float, optional): how long the animation should run before
                                   terminating (in seconds). If None is
                                   specified, the animation will run
                                   forever.
        period (float, optional): The time (in seconds) for a complete
                                  passive/angry cycle. Default is 10.0 seconds.
        duty_cycle (float, optional): The fraction (between 0 and 1) of the time
                                      the bee face should be "passive". Default
                                      is 0.7 (7s passive to 3s angry).
        frame_rate (float, optional): how many times per second to render the
                                      animation. Default is 1 fps (this is not
                                      a very dynamic animation).
        clear_after (bool, optional): whether to turn off all the LED lights
                                      once the animation ends. Default is True.

    Returns:
        None
    """
    if isinstance(light_strip[0], Pixel):
        pixels = light_strip[:12]
    else:
        pixels = [Pixel(light_strip, i) for i in range(12)]

    animation_kwargs = {}
    if period is not None:
        animation_kwargs["period"] = period
    if duty_cycle is not None:
        animation_kwargs["duty_cycle"] = duty_cycle
    animation = BeeFace(pixels, **animation_kwargs)
    run_animations([animation], runtime, frame_rate, clear_after)
