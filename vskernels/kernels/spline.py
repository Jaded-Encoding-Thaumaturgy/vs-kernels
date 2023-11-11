from __future__ import annotations

import re
from math import ceil, isqrt
from typing import Any

from vstools import core, inject_self

from .zimg import ZimgComplexKernel
from .fmtconv import FmtConv

__all__ = [
    'Spline',
    'Spline16',
    'Spline36',
    'Spline64',
]


class _SplineKernelSize:
    """Spline kernel size sub-class."""

    @inject_self.property
    def kernel_size(self) -> int:
        radius = re.search(r'\d+$', self.__class__.__name__)

        if not radius:
            return 1

        return ceil(isqrt(int(radius.group())) / 2)


class Spline(FmtConv):
    """fmtconv's spline resizer."""

    _kernel = 'spline'

    def __init__(self, taps: int = 2, **kwargs: Any) -> None:
        super().__init__(taps=taps, **kwargs)

    @inject_self.property
    def kernel_size(self) -> int:
        return ceil(self.taps)


class Spline16(ZimgComplexKernel, _SplineKernelSize):
    """
    Built-in spline16 resizer.

    Dependencies:

    * VapourSynth-descale
    """

    scale_function = resample_function = core.lazy.resize.Spline16
    descale_function = core.lazy.descale.Despline16


class Spline36(ZimgComplexKernel, _SplineKernelSize):
    """
    Built-in spline36 resizer.

    Dependencies:

    * VapourSynth-descale
    """

    scale_function = resample_function = core.lazy.resize.Spline36
    descale_function = core.lazy.descale.Despline36


class Spline64(ZimgComplexKernel, _SplineKernelSize):
    """
    Built-in spline64 resizer.

    Dependencies:

    * VapourSynth-descale
    """

    scale_function = resample_function = core.lazy.resize.Spline64
    descale_function = core.lazy.descale.Despline64
