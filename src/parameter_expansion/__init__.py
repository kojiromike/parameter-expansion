import sys
import warnings
from typing import Optional

from .pe import ParameterExpansionNullError, expand

_default_version = "0.0.0+unknown"


def _version_from_importlib(name: str) -> Optional[str]:
    try:
        if sys.version_info >= (3, 8):
            from importlib import metadata
        else:
            import importlib_metadata as metadata
    except ImportError:
        return None

    try:
        return metadata.version(__name__)
    except metadata.PackageNotFoundError:
        return None


def _version_from_pkg_resources(name: str) -> Optional[str]:
    try:
        import pkg_resources
    except ImportError:
        return None

    try:
        return pkg_resources.get_distribution(name).version
    except pkg_resources.DistributionNotFound:
        return None


def _version_failover(name: str) -> str:
    warnings.warn(
        UserWarning(
            f"Unable to determine version for {name}. Falling back to {_default_version}"
        )
    )
    return _default_version


__version__ = (
    _version_from_pkg_resources(__name__)
    or _version_from_importlib(__name__)
    or _version_failover(__name__)
)
