from __future__ import annotations

from typing import Any

from vstools import core

from .zimg import ZimgComplexKernel
from .fmtconv import FmtConv

__all__ = [
    'Spline',
    'Spline16',
    'Spline36',
    'Spline64',
]


class Spline(FmtConv):
    """fmtconv's spline resizer."""

    _kernel = 'spline'

    def __init__(self, taps: int = 2, **kwargs: Any) -> None:
        super().__init__(taps=taps, **kwargs)


class Spline16(ZimgComplexKernel):
    """
    Built-in spline16 resizer.

    Dependencies:

    * VapourSynth-descale
    """

    scale_function = resample_function = core.lazy.resize.Spline16
    descale_function = core.lazy.descale.Despline16


class Spline36(ZimgComplexKernel):
    """
    Built-in spline36 resizer.

    Dependencies:

    * VapourSynth-descale
    """

    scale_function = resample_function = core.lazy.resize.Spline36
    descale_function = core.lazy.descale.Despline36


class Spline64(ZimgComplexKernel):
    """
    Built-in spline64 resizer.

    Dependencies:

    * VapourSynth-descale
    """

    scale_function = resample_function = core.lazy.resize.Spline64
    descale_function = core.lazy.descale.Despline64
