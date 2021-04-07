try:
    from ._version import get_versions

    __version__ = get_versions()["version"]
    del get_versions
except ImportError:
    __version__ = "0+unknown"

from .animations import random_cycle  # noqa: F401
from .asciipixel import AsciiPixel  # noqa: F401
from .base import Animation, Pixel  # noqa: F401
from .manager import run_animations  # noqa: F401
