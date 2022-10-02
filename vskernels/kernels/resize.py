from __future__ import annotations

from typing import Any

from vstools import core, vs

from .abstract import Kernel

__all__ = [
    'Point',
    'Bilinear',
    'Lanczos',
]


class Point(Kernel):
    """Built-in point resizer."""

    scale_function = core.proxied.resize.Point
    descale_function = core.proxied.resize.Point


class Bilinear(Kernel):
    """Built-in bilinear resizer."""

    scale_function = core.proxied.resize.Bilinear
    descale_function = core.proxied.descale.Debilinear


class Lanczos(Kernel):
    """
    Built-in lanczos resizer.

    Dependencies:

    * VapourSynth-descale

    :param taps: taps param for lanczos kernel
    """

    scale_function = core.proxied.resize.Lanczos
    descale_function = core.proxied.descale.Delanczos

    def __init__(self, taps: int = 3, **kwargs: Any) -> None:
        self.taps = taps
        super().__init__(**kwargs)

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        args = super().get_params_args(is_descale, clip, width, height, **kwargs)
        if is_descale:
            return args | dict(taps=self.taps)
        return args | dict(filter_param_a=self.taps)
