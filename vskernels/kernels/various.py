from __future__ import annotations

from typing import Any, Dict

import vapoursynth as vs

from .abstract import Kernel
from .fmtconv import FmtConv
from .placebo import Placebo

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
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> Dict[str, Any]:
        args = super().get_params_args(is_descale, clip, width, height, **kwargs)
        if is_descale:
            return dict(**args, taps=self.taps)
        return dict(**args, filter_param_a=self.taps)


class Box(FmtConv):
    """fmtconv's box resizer."""

    kernel = 'box'


class BlackMan(FmtConv):
    """fmtconv's blackman resizer."""

    kernel = 'blackman'


class BlackManMinLobe(FmtConv):
    """fmtconv's blackmanminlobe resizer."""

    kernel = 'blackmanminlobe'


class Sinc(FmtConv):
    """fmtconv's sinc resizer."""

    kernel = 'sinc'


class Gaussian(FmtConv):
    """fmtconv's gaussian resizer."""

    kernel = 'gaussian'

    def __init__(self, curve: int = 30, **kwargs: Any) -> None:
        super().__init__(a1=curve, **kwargs)


class NearestNeighbour(Gaussian):
    """Nearest Neighbour kernel."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(100, **kwargs)


class EwaJinc(Placebo):
    kernel = 'ewa_jinc'

    def __init__(self, taps: int = 3, **kwargs: Any) -> None:
        super().__init__(taps, None, None, **kwargs)


class EwaLanczos(Placebo):
    kernel = 'ewa_lanczos'

    def __init__(self, taps: int = 3, **kwargs: Any) -> None:
        super().__init__(taps, None, None, **kwargs)


class EwaGinseng(Placebo):
    kernel = 'ewa_ginseng'

    def __init__(self, taps: int = 3, **kwargs: Any) -> None:
        super().__init__(taps, None, None, **kwargs)


class EwaHann(Placebo):
    kernel = 'ewa_hann'

    def __init__(self, taps: int = 3, **kwargs: Any) -> None:
        super().__init__(taps, None, None, **kwargs)


class EwaHannSoft(Placebo):
    kernel = 'haasnsoft'

    def __init__(self, taps: int = 3, **kwargs: Any) -> None:
        super().__init__(taps, None, None, **kwargs)


class EwaRobidoux(Placebo):
    kernel = 'ewa_robidoux'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(None, None, None, **kwargs)


class EwaRobidouxSharp(Placebo):
    kernel = 'ewa_robidouxsharp'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(None, None, None, **kwargs)
