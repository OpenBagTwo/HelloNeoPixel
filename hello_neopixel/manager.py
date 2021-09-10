"""Recipes for choreographing animations"""
from ._compat import utime


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
            if runtime is not None and current_time > runtime:
                break

            for animation in animations:
                animation.render(current_time)

            for light_strip in light_strips:
                light_strip.write()

            compute_time_us = utime.ticks_us() - step_start_tick_us
            if compute_time_us < step_time_us:
                utime.sleep_us(step_time_us - compute_time_us)

    finally:
        if clear_after:
            for pixel in pixels:
                pixel.blank()
            for light_strip in light_strips:
                light_strip.write()
