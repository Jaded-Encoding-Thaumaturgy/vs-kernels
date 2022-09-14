from __future__ import annotations

from vstools import CustomValueError

__all__ = [
    'UnknownKernelError',
]


class UnknownKernelError(CustomValueError):
    """Raised when an unknown kernel is passed."""
