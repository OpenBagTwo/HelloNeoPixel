"""Library of animations"""
import random

import utime
from neopixel import NeoPixel

from . import utils


def random_cycle(
    light_strip: NeoPixel,
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
    n_pixels = light_strip.n
    step_time = int(1000 / frame_rate)  # ms to sleep between steps

    colors = []

    for i in range(n_pixels):
        hue = int(random.random() * 360)
        rgb = utils.convert_hue_to_rgb(hue)
        colors.append(rgb)

    start_time = utime.ticks_ms()

    try:
        while True:
            current_time = utime.ticks_diff(utime.ticks_ms(), start_time)
            pixel_shift = int(current_time / transition_time / 1000) % n_pixels

            shift_progress = (current_time / transition_time / 1000) % 1

            for i in range(n_pixels):
                light_strip[i] = utils.crossfade(
                    colors[(i + pixel_shift) % n_pixels],
                    colors[(i + pixel_shift + 1) % n_pixels],
                    progress=shift_progress,
                )
            light_strip.write()

            # TODO: see if uPython has math.nan
            if runtime is not None and current_time > runtime:
                break

            utime.sleep_ms(step_time)
    finally:
        if clear_after:
            for i in range(n_pixels):
                light_strip[i] = (0, 0, 0)
            light_strip.write()
