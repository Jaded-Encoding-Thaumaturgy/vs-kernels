from __future__ import annotations

from functools import lru_cache
from typing import Generator

import vapoursynth as vs

from .kernels import FmtConv, Kernel, Placebo
from .kernels.docs import Example
from .kernels.impulse import Impulse

__all__ = [
    'get_all_kernels'
]

core = vs.core


excluded_kernels = [Kernel, FmtConv, Example, Impulse, Placebo]


@lru_cache
def get_all_kernels(family: type[Kernel] = Kernel) -> list[type[Kernel]]:
    """Get all kernels as a list."""
    def _subclasses(cls: type[Kernel]) -> Generator[type[Kernel], None, None]:
        for subclass in cls.__subclasses__():
            yield from _subclasses(subclass)
            if subclass in excluded_kernels:
                continue
            yield subclass

    return list(set(_subclasses(family)))
