from __future__ import annotations

from typing import Any

from .placebo import Placebo

__all__ = [
    'EwaBicubic',
    'EwaJinc',
    'EwaLanczos',
    'EwaGinseng',
    'EwaHann',
    'EwaHannSoft',
    'EwaRobidoux',
    'EwaRobidouxSharp',
]


class EwaBicubic(Placebo):
    _kernel = 'ewa_robidoux'

    def __init__(self, b: float = 0.0, c: float = 0.5, radius: int | None = None, **kwargs: Any) -> None:
        radius = kwargs.pop('taps', radius)

        if radius is None:
            from .bicubic import Bicubic

            radius = Bicubic(b, c).kernel_radius

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
