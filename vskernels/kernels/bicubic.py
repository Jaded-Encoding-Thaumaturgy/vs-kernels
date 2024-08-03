from __future__ import annotations

from math import sqrt
from typing import Any

from vstools import CustomValueError, core, inject_self, vs

from .zimg import ZimgComplexKernel

__all__ = [
    'Bicubic',
    'BSpline',
    'Hermite',
    'Mitchell',
    'Catrom',
    'FFmpegBicubic',
    'AdobeBicubic',
    'BicubicSharp',
    'RobidouxSoft',
    'Robidoux',
    'RobidouxSharp',
    'BicubicAuto',
]


class Bicubic(ZimgComplexKernel):
    """
    Built-in bicubic resizer.

    Default: b=0, c=0.5

    Dependencies:

    * VapourSynth-descale

    :param b: B-param for bicubic kernel
    :param c: C-param for bicubic kernel
    """

    scale_function = resample_function = core.lazy.resize.Bicubic
    descale_function = core.lazy.descale.Debicubic

    def __init__(self, b: float = 0, c: float = 1 / 2, **kwargs: Any) -> None:
        self.b = b
        self.c = c
        super().__init__(**kwargs)

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        args = super().get_params_args(is_descale, clip, width, height, **kwargs)
        if is_descale:
            return args | dict(b=self.b, c=self.c)
        return args | dict(filter_param_a=self.b, filter_param_b=self.c)

    @inject_self.property
    def kernel_radius(self) -> int:  # type: ignore
        if (self.b, self.c) == (0, 0):
            return 1
        return 2


class BSpline(Bicubic):
    """Bicubic b=1, c=0"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=1, c=0, **kwargs)


class Hermite(Bicubic):
    """Bicubic b=0, c=0"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=0, c=0, **kwargs)


class Mitchell(Bicubic):
    """Bicubic b=1/3, c=1/3"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=1 / 3, c=1 / 3, **kwargs)


class Catrom(Bicubic):
    """Bicubic b=0, c=0.5"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=0, c=1 / 2, **kwargs)


class FFmpegBicubic(Bicubic):
    """Bicubic b=0, c=0.6; FFmpeg's swscale default"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=0, c=0.6, **kwargs)


class AdobeBicubic(Bicubic):
    """Bicubic b=0, c=0.75; Adobe's "Bicubic" interpolation preset"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=0, c=3 / 4, **kwargs)


class BicubicSharp(Bicubic):
    """Bicubic b=0, c=1"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=0, c=1, **kwargs)


class RobidouxSoft(Bicubic):
    """Bicubic b=0.67962, c=0.16019"""

    def __init__(self, **kwargs: Any) -> None:
        b = (9 - 3 * sqrt(2)) / 7
        c = (1 - b) / 2
        super().__init__(b=b, c=c, **kwargs)


class Robidoux(Bicubic):
    """Bicubic b=0.37822, c=0.31089"""

    def __init__(self, **kwargs: Any) -> None:
        b = 12 / (19 + 9 * sqrt(2))
        c = 113 / (58 + 216 * sqrt(2))
        super().__init__(b=b, c=c, **kwargs)


class RobidouxSharp(Bicubic):
    """Bicubic b=0.26201, c=0.36899"""

    def __init__(self, **kwargs: Any) -> None:
        b = 6 / (13 + 7 * sqrt(2))
        c = 7 / (2 + 12 * sqrt(2))
        super().__init__(b=b, c=c, **kwargs)


class BicubicAuto(ZimgComplexKernel):
    """
    Kernel that follows the rule of:
    b + 2c = target
    """

    scale_function = resample_function = core.lazy.resize.Bicubic
    descale_function = core.lazy.descale.Debicubic

    def __init__(self, b: float | None = None, c: float | None = None, target: float = 1.0, **kwargs: Any) -> None:
        if None not in {b, c}:
            raise CustomValueError("You can't specify both b and c!", self.__class__)

        self.b = b
        self.c = c
        self.target = target

        super().__init__(**kwargs)

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        args = super().get_params_args(is_descale, clip, width, height, **kwargs)

        b, c = self._get_bc_args()

        if is_descale:
            return args | dict(b=b, c=c)
        return args | dict(filter_param_a=b, filter_param_b=c)

    def _get_bc_args(self) -> tuple[float, float]:
        autob = 0.0 if self.b is None else self.b
        autoc = 0.5 if self.c is None else self.c

        if self.c is not None and self.b is None:
            autob = self.target - 2 * self.c
        elif self.c is None and self.b is not None:
            autoc = (self.target - self.b) / 2

        return autob, autoc

    @inject_self.property
    def kernel_radius(self) -> int:  # type: ignore
        return Bicubic(*self._get_bc_args()).kernel_radius
