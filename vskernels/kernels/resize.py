from __future__ import annotations

from typing import Any

from vstools import inject_self

from .helpers import sinc
from .complex import CustomComplexKernel, CustomComplexTapsKernel

__all__ = [
    'Point',
    'Bilinear',
    'Lanczos',
]


class Point(CustomComplexKernel):
    """Built-in point resizer."""

    _static_kernel_radius = 1

    @inject_self
    def kernel(self, *, x: float) -> float:  # type: ignore
        return 1.0


class Bilinear(CustomComplexKernel):
    """Built-in bilinear resizer."""

    _static_kernel_radius = 1

    @inject_self
    def kernel(self, *, x: float) -> float:  # type: ignore
        return max(1.0 - abs(x), 0.0)


class Lanczos(CustomComplexTapsKernel):
    """
    Lanczos resizer.

    :param taps: taps param for lanczos kernel
    """

    def __init__(self, taps: int = 3, **kwargs: Any) -> None:
        super().__init__(taps, **kwargs)

    @inject_self
    def kernel(self, *, x: float) -> float:  # type: ignore
        x, taps = abs(x), self.kernel_radius

        return sinc(x) * sinc(x / taps) if x < taps else 0.0
