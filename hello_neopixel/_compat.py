"""Compatibility layer to allow for running across Python implementations"""
try:
    import urandom
except ModuleNotFoundError:
    import random as urandom  # type: ignore[no-redef]


def _random() -> float:
    """Workaround for MicroPython on the desktop not having random.random()

    Returns:
        float: A random floating value between 0 and 1

    """
    return urandom.getrandbits(8) / 2 ** 8  # way more resolution than we need


if not hasattr(urandom, "random"):
    setattr(urandom, "random", _random)

try:
    import utime
except ModuleNotFoundError:
    import time as utime  # type: ignore[no-redef]


_START_TIME = utime.time()


def _ticks_ms() -> int:
    """Workaround for ticks_ms being a MicroPython-only function

    Returns:
        int: the number of milliseconds since this module was imported
    """
    return int((utime.time() - _START_TIME) * 1e3)


def _ticks_us() -> int:
    """Workaround for ticks_us being a MicroPython-only function

    Returns:
        int: the number of microseconds since this module was imported
    """
    return int((utime.time() - _START_TIME) * 1e6)


def _ticks_diff(end_tick: int, start_tick: int) -> int:
    """Workaround for ticks_diff being a MicroPython-only function

    Args:
        end_tick (int): The later tick value
        start_tick (int): The earlier tick value

    Returns:
        int: the number of ticks between the two provided values
    """
    return end_tick - start_tick


def _sleep_ms(ms_of_sleep: int) -> None:
    """Workaround for sleep_ms being a MicroPython-only function

    Args:
        ms_of_sleep (int): The number of milliseconds to sleep

    Returns:
        None
    """
    utime.sleep(ms_of_sleep / 1e3)


def _sleep_us(us_of_sleep: int) -> None:
    """Workaround for sleep_us being a MicroPython-only function

    Args:
        us_of_sleep (int): The number of microseconds to sleep

    Returns:
        None
    """
    utime.sleep(us_of_sleep / 1e6)


if not hasattr(utime, "ticks_ms"):
    setattr(utime, "ticks_ms", _ticks_ms)
if not hasattr(utime, "ticks_us"):
    setattr(utime, "ticks_us", _ticks_us)
if not hasattr(utime, "ticks_diff"):
    setattr(utime, "ticks_diff", _ticks_diff)
if not hasattr(utime, "sleep_ms"):
    setattr(utime, "sleep_ms", _sleep_ms)
if not hasattr(utime, "sleep_us"):
    setattr(utime, "sleep_us", _sleep_us)
