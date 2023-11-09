from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vstools import CustomIntEnum, inject_self, vs

from .complex import ComplexKernel, Descaler


__all__ = [
    'BorderHandling',
    'ZimgDescaler',
    'ZimgComplexKernel'
]


class BorderHandling(CustomIntEnum):
    MIRROR = 0
    ZERO = 1
    REPEAT = 2


class ZimgDescaler(Descaler):
    if TYPE_CHECKING:
        @inject_self.cached
        def descale(  # type: ignore[override]
            self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0),
            *, blur: float = 1.0, border_handling: BorderHandlingT = BorderHandling.MIRROR, **kwargs: Any
        ) -> vs.VideoNode:
            ...


class ZimgComplexKernel(ComplexKernel, ZimgDescaler):
    if TYPE_CHECKING:
        @inject_self.cached
        def descale(  # type: ignore[override]
            self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0),
            *, blur: float = 1.0, border_handling: BorderHandlingT,
            linear: bool = False, sigmoid: bool | tuple[float, float] = False, **kwargs: Any
        ) -> vs.VideoNode:
            ...

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        args = super().get_params_args(is_descale, clip, width, height, **kwargs)

        if not is_descale:
            args.pop('border_handling', None)
            args.pop('blur', None)

        return args


BorderHandlingT = BorderHandling | int
