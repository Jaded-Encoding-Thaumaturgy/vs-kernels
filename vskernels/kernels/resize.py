from __future__ import annotations

from typing import Any, Dict

import vapoursynth as vs

from .abstract import Kernel

core = vs.core


class Point(Kernel):
    """Built-in point resizer."""

    scale_function = core.resize.Point
    descale_function = core.resize.Point


class Bilinear(Kernel):
    """Built-in bilinear resizer."""

    scale_function = core.resize.Bilinear
    descale_function = core.descale.Debilinear


class Lanczos(Kernel):
    """
    Built-in lanczos resizer.

    Dependencies:

    * VapourSynth-descale

    :param taps: taps param for lanczos kernel
    """

    scale_function = core.resize.Lanczos
    descale_function = core.descale.Delanczos

    def __init__(self, taps: int = 3, **kwargs: Any) -> None:
        self.taps = taps
        super().__init__(**kwargs)

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None
    ) -> Dict[str, Any]:
        args = super().get_params_args(is_descale, clip, width, height)
        if is_descale:
            return dict(**args, taps=self.taps)
        return dict(**args, filter_param_a=self.taps)
