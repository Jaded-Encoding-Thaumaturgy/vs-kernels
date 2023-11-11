from __future__ import annotations

from math import ceil, log, sqrt
from typing import Any

from vstools import CustomValueError, to_singleton

from .fmtconv import FmtConv
from .placebo import Placebo

__all__ = [
    'Box',
    'BlackMan',
    'BlackManMinLobe',
    'Sinc',
    'Gaussian',
    'EwaBicubic',
    'EwaJinc',
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

    def __init__(self, sigma: float = 0.5, taps: int = 2, **kwargs: Any) -> None:
        """
        Sigma is imagemagick's sigma scaling.
        This will internally be scaled to fmtc's curve.

        You can specify "curve" to override sigma and specify the original `a1` value.
        """
        if 'curve' in kwargs:
            a1 = kwargs.pop('curve')

            if a1 is not None:
                if a1 < 1.0 or a1 > 100.0:
                    raise CustomValueError("curve must be in range 1-100! (inclusive)")
        else:
            a1 = self.sigma.to_fmtc(sigma)

            low, up = self.sigma.from_fmtc(100), self.sigma.from_fmtc(1)

            if a1 < 1.0 or a1 > 100.0:
                raise CustomValueError(f"sigma must be in range {low:.4f}-{up:.4f}! (inclusive)")

        super().__init__(taps, a1=a1, **kwargs)

    @to_singleton
    class sigma:
        def from_fmtc(self, curve: float) -> float:
            if not curve:
                return 0.0
            return sqrt(1.0 / (2.0 * (curve / 10.0) * log(2)))

        def to_fmtc(self, sigma: float) -> float:
            if not sigma:
                return 0.0
            return 10 / (2 * log(2) * (sigma ** 2))

        def from_libplacebo(self, sigma: float) -> float:
            if not sigma:
                return 0.0
            return sqrt(sigma / 4)

        def to_libplacebo(self, sigma: float) -> float:
            if not sigma:
                return 0.0
            return 4 * (sigma ** 2)


class EwaBicubic(Placebo):
    _kernel = 'ewa_robidoux'

    def __init__(self, b: float = 0.0, c: float = 0.5, radius: int | None = None, **kwargs: Any) -> None:
        radius = self._kernel_size(kwargs.pop('taps', radius), b, c)

        super().__init__(radius, b, c, **kwargs)


class EwaLanczos(Placebo):
    _kernel = 'ewa_lanczos'

    def __init__(self, taps: float = 3.2383154841662362076499, **kwargs: Any) -> None:
        super().__init__(taps, None, None, **kwargs)


class EwaJinc(Placebo):
    _kernel = 'ewa_jinc'

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
