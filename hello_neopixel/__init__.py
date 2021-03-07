try:
    from ._version import get_versions

    __version__ = get_versions()["version"]
    del get_versions
except ImportError:
    __version__ = "0+unknown"

from .animations import *  # noqa: F401, F403
