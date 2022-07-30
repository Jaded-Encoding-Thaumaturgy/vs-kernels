from __future__ import annotations

__all__ = [
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


class UndefinedTransferError(ValueError):
    """Raised when an undefined transfer is passed."""


class ReservedTransferError(PermissionError):
    """Raised when a reserved transfer is requested."""


class UnsupportedTransferError(ValueError):
    """Raised when an unsupported transfer is passed."""


class UndefinedPrimariesError(ValueError):
    """Raised when an undefined primaries value is passed."""


class ReservedPrimariesError(PermissionError):
    """Raised when reserved primaries are requested."""


class UnsupportedPrimariesError(ValueError):
    """Raised when a unsupported primaries value is passed."""


class UnknownKernelError(ValueError):
    """Raised when an unknown kernel is passed."""


class VideoPropError(KeyError):
    """Raised when there was an issue with a VideoProp."""
