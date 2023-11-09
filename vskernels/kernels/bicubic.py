from __future__ import annotations

from math import acos, asinh, cos, sqrt
from typing import TYPE_CHECKING, Any

from vstools import CustomValueError, core, vs

from .complex import ComplexKernel

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
    'BicubicDidee',
    'SetsuCubic',
    'ZewiaCubic',
    'BicubicZopti',
    'BicubicZoptiNeutral',
    'BicubicAuto',
]


class MemeKernel:
    if TYPE_CHECKING:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            print(DeprecationWarning(
                f"{self.__class__.__name__} and other meme Bicubic presets are deprecated!\n"
                "They will be removed in the next major update."
            ))
            super().__init__(*args, **kwargs)


class Bicubic(ComplexKernel):
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


class BicubicDidee(MemeKernel, Bicubic):
    """
    Kernel inspired by a Didée post.


    `See this doom9 post for further information
    <https://web.archive.org/web/20220713044016/https://forum.doom9.org/showpost.php?p=1579385>`_.

    Bicubic b=-0.5, c=0.25
    This is useful for downscaling content, but might not help much with upscaling.

    Follows `b + 2c = 0` for downscaling as opposed to `b + 2c = 1` for upscaling.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=-1 / 2, c=1 / 4, **kwargs)


class SetsuCubic(MemeKernel, Bicubic):
    """
    Schizo (Setsugen's) values calculated from the legendary Pompo-san filterchain.
    Useful for heavy post processed content or ringing in general.

    Bicubic
    strength=200: b=-0.22582213942537233, c=0.06676658576029935
    strength=100: b=-0.26470935063297507, c=0.73588297801744030
    strength=50:  b=-0.24550548633321580, c=0.37020197611906490
    strength=1:   b=-0.32938660656063920, c=0.21245005943760129
    """

    def __init__(self, strength: float = 100.0, **kwargs: Any) -> None:
        super().__init__(
            asinh(.5) * acos(.5) * -abs(cos(strength * 4)),
            abs(asinh(.5) * acos(-.5) * cos((strength * 4) + strength / 2)),
            **kwargs
        )


class ZewiaCubic(MemeKernel, Bicubic):
    """
    Schizo (Zewia's) values he made up for downscaling after prefiltering for anti-aliasing.

    It is said these values came up in his mind the morning after a good night of sleep the day
    he fell asleep with YouTube music on and the auto recommendations made him listen to Mori Calliope
    (his favourite VTuber/Rapper) for 6 hours straight.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=-1 / 3, c=1 / 6, **kwargs)


class BicubicZopti(MemeKernel, Bicubic):
    """
    Kernel optimized by Zopti.

    `See this doom9 post for further information
    <https://web.archive.org/web/20220713052137/https://forum.doom9.org/showthread.php?p=1865218>`_.

    Bicubic b=-0.6, c=0.4
    Optimized for 2160p to 720p (by Boulder). Beware, not neutral. Adds some local contrast.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=-0.6, c=0.4, **kwargs)


class BicubicZoptiNeutral(MemeKernel, Bicubic):
    """
    Kernel inspired by Zopti.
    Bicubic b=-0.6, c=0.3

    A slightly more neutral alternative to BicubicZopti.

    Follows `b + 2c = 0` for downscaling as opposed to `b + 2c = 1` for upscaling.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=-0.6, c=0.3, **kwargs)


class BicubicAuto(ComplexKernel):
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
