from __future__ import annotations

from typing import Any

import vapoursynth as vs

from .fmtconv import FmtConv
from .placebo import Placebo

core = vs.core


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
