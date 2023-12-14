from __future__ import annotations

from typing import TYPE_CHECKING, Any

from stgpytools import inject_kwargs_params
from vstools import inject_self, vs

from ..types import Center, LeftShift, Slope, TopShift
from .abstract import Descaler
from .complex import ComplexKernel, BorderHandling

__all__ = [
    'ZimgDescaler',
    'ZimgComplexKernel'
]


class ZimgDescaler(Descaler):
    if TYPE_CHECKING:
        @inject_self.cached
        @inject_kwargs_params
        def descale(  # type: ignore[override]
            self, clip: vs.VideoNode, width: int, height: int, shift: tuple[TopShift, LeftShift] = (0, 0),
            *, blur: float = 1.0, border_handling: BorderHandling = BorderHandling.MIRROR, **kwargs: Any
        ) -> vs.VideoNode:
            ...


class ZimgComplexKernel(ComplexKernel, ZimgDescaler):  # type: ignore
    if TYPE_CHECKING:
        @inject_self.cached
        @inject_kwargs_params
        def descale(  # type: ignore[override]
            self, clip: vs.VideoNode, width: int, height: int, shift: tuple[TopShift, LeftShift] = (0, 0),
            *, blur: float = 1.0, border_handling: BorderHandling, ignore_mask: vs.VideoNode | None = None,
            linear: bool = False, sigmoid: bool | tuple[Slope, Center] = False, **kwargs: Any
        ) -> vs.VideoNode:
            ...

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        args = super().get_params_args(is_descale, clip, width, height, **kwargs)

        if not is_descale:
            for key in ('blur', 'border_handling', 'ignore_mask', 'force', 'force_h', 'force_v'):
                args.pop(key, None)

        return args
