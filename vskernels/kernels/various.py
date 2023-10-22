from __future__ import annotations

from typing import Any

from .fmtconv import FmtConv
from .placebo import Placebo

__all__ = [
    'Box',
    'BlackMan',
    'BlackManMinLobe',
    'Sinc',
    'Gaussian',
    'EwaBicubic',
    'EwaLanczos',
    'EwaGinseng',
    'EwaHann',
    'EwaHannSoft',
    'EwaRobidoux',
    'EwaRobidouxSharp',
]


class Box(FmtConv):
    """fmtconv's box resizer."""

    _kernel = 'box'


class BlackMan(FmtConv):
    """fmtconv's blackman resizer."""

    _kernel = 'blackman'


class BlackManMinLobe(FmtConv):
    """fmtconv's blackmanminlobe resizer."""

    _kernel = 'blackmanminlobe'


class Sinc(FmtConv):
    """fmtconv's sinc resizer."""

    _kernel = 'sinc'


class Gaussian(FmtConv):
    """fmtconv's gaussian resizer."""

    _kernel = 'gaussian'

    def __init__(self, curve: float = 30, taps: int = 2, **kwargs: Any) -> None:
        super().__init__(taps, a1=curve, **kwargs)


class EwaBicubic(Placebo):
    _kernel = 'ewa_robidoux'

    def __init__(self, b: float = 0.0, c: float = 0.5, radius: int | None = None, **kwargs: Any) -> None:
        radius = kwargs.pop('taps', radius)

        if radius is None:
            radius = 1 if (b, c) == (0, 0) else 2

        super().__init__(radius, b, c, **kwargs)


class EwaJinc(Placebo):
    _kernel = 'ewa_jinc'

    def __init__(self, taps: float = 3.2383154841662362076499, **kwargs: Any) -> None:
        super().__init__(taps, None, None, **kwargs)


class EwaLanczos(Placebo):
    _kernel = 'ewa_lanczos'

    def __init__(self, taps: float = 3.2383154841662362076499, **kwargs: Any) -> None:
        super().__init__(taps, None, None, **kwargs)


class EwaGinseng(Placebo):
    _kernel = 'ewa_ginseng'

    def __init__(self, taps: float = 3.2383154841662362076499, **kwargs: Any) -> None:
        super().__init__(taps, None, None, **kwargs)


class EwaHann(Placebo):
    _kernel = 'ewa_hann'

    def __init__(self, taps: float = 3.2383154841662362076499, **kwargs: Any) -> None:
        super().__init__(taps, None, None, **kwargs)


class EwaHannSoft(Placebo):
    _kernel = 'haasnsoft'

    def __init__(self, taps: float = 3.2383154841662362076499, **kwargs: Any) -> None:
        super().__init__(taps, None, None, **kwargs)


class EwaRobidoux(Placebo):
    _kernel = 'ewa_robidoux'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(None, None, None, **kwargs)


class EwaRobidouxSharp(Placebo):
    _kernel = 'ewa_robidouxsharp'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(None, None, None, **kwargs)
