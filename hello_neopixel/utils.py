"""Utilities for use in the main script"""


def convert_hue_to_rgb(hue: float) -> tuple:
    """Convert an HSV color of max saturation and brightness to its RGB
    representation

    Note:
        Formula taken from https://en.wikipedia.org/wiki/HSL_and_HSV#HSV_to_RGB

    Args:
        hue (float): The hue value, in degrees

    Returns:
        tuple of three ints: the RGB tuple corresponding to the given hue at
                             max saturation and brightness
    """
    try:
        chroma = 255  # = value * saturation
        hue_prime = hue / 60.0

        intermediate = round(chroma * (1.0 - abs(hue_prime % 2.0 - 1.0)))

        if hue_prime >= 0.0:
            if hue_prime <= 1.0:
                return chroma, intermediate, 0
            if hue_prime <= 2.0:
                return intermediate, chroma, 0
            if hue_prime <= 3.0:
                return 0, chroma, intermediate
            if hue_prime <= 4.0:
                return 0, intermediate, chroma
            if hue_prime <= 5.0:
                return intermediate, 0, chroma
            if hue_prime <= 6.0:
                return chroma, 0, intermediate
    except TypeError:
        pass

    raise ValueError("Hue must be a float between 0 and 360 (inclusive)")


def crossfade(old_color: tuple, new_color: tuple, progress: float) -> tuple:
    """Compute a crossfade between two RGB colors

    Args:
        old_color (tuple of three ints): the color you're fading from
        new_color (tuple of three ints): the color you're fading to
        progress (float): the fraction (between 0 and 1) you are to the new
                          color (0 = all old color, 1 = all new color)

    Returns:
        tuple of three ints: the RGB tuple corresponding to the mixed color
    """
    try:
        assert 0.0 <= progress <= 1.0
    except (TypeError, AssertionError):
        raise ValueError("Progress must be a float between 0 and 1 (inclusive")

    return tuple(
        round(old_color[i] * (1.0 - progress) + new_color[i] * progress)
        for i in range(3)
    )


def render_runner(color: tuple, position: float, pixel_num: int) -> tuple:
    """For a "runner" with the given color that should be "located" at a given
    point on the LED strip, return the rgb value that should be displayed at the
    given pixel position.

    Args:
        color (tuple of three ints) : the color of the runner
        position (float) : the position of the runner
        pixel_num (int) : the index of the pixel on the LED strip (or,
                          alternatively, think of it as the "position" of the
                          LED strip pixel)

    Returns:
        tuple of three ints : the RGB value that should be rendered at the given
                              pixel
    """
    distance = abs(position - pixel_num)
    if distance > 1.0:
        return (0, 0, 0)
    return crossfade((0, 0, 0), color, 1.0 - distance)
