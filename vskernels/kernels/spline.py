from __future__ import annotations

from typing import Any

import vapoursynth as vs

from .abstract import Kernel
from .fmtconv import FmtConv

core = vs.core


class Spline16(Kernel):
    """
    Built-in spline16 resizer.

    Dependencies:

    * VapourSynth-descale
    """

    scale_function = core.resize.Spline16
    descale_function = core.descale.Despline16


class Spline36(Kernel):
    """
    Built-in spline36 resizer.

    Dependencies:

    * VapourSynth-descale
    """

    scale_function = core.resize.Spline36
    descale_function = core.descale.Despline36


class Spline64(Kernel):
    """
    Built-in spline64 resizer.

    Dependencies:

    * VapourSynth-descale
    """

    scale_function = core.resize.Spline64
    descale_function = core.descale.Despline64


class Spline144(FmtConv):
    """
    fmtconv spline kernel with taps=6.

    Dependencies:

    * fmtconv
    """

    kernel = 'spline'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(taps=6, **kwargs)
