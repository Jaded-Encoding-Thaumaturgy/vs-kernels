from typing import List

__all__: List[str] = [
    'ReservedMatrixError',
    'UndefinedMatrixError',
    'UnknownKernelError',
    'UnsupportedMatrixError',
    'VideoPropError',
]


class UndefinedMatrixError(ValueError):
    """Raised when an undefined matrix is passed."""


class ReservedMatrixError(PermissionError):
    """Raised when a reserved matrix is requested."""


class UnsupportedMatrixError(ValueError):
    """Raised when an unsupported matrix is passed."""


class UnknownKernelError(ValueError):
    """Raised when an unknown kernel is passed."""


class VideoPropError(KeyError):
    """Raised when there was an issue with a VideoProp."""
