from __future__ import annotations

from functools import lru_cache
from typing import Any, TypeAlias

from vstools import CustomIntEnum, KwargsT, padder, vs

__all__ = [
    'BorderHandling', 'SampleGridModel'
]


class BorderHandling(CustomIntEnum):
    MIRROR = 0
    ZERO = 1
    REPEAT = 2

    def prepare_clip(self, clip: vs.VideoNode, min_pad: int = 2) -> vs.VideoNode:
        pad_w, pad_h = (
            self.pad_amount(size, min_pad) for size in (clip.width, clip.height)
        )

        if pad_w == pad_h == 0:
            return clip

        args = (clip, pad_w, pad_w, pad_h, pad_h)

        match self:
            case BorderHandling.MIRROR:
                return padder.MIRROR(*args)
            case BorderHandling.ZERO:
                return padder.COLOR(color=False if clip.format.color_family is vs.RGB else (False, None), *args)
            case BorderHandling.REPEAT:
                return padder.REPEAT(*args)

    @lru_cache
    def pad_amount(self, size: int, min_amount: int = 2) -> int:
        if self is BorderHandling.MIRROR:
            return 0

        return (((size + min_amount) + 7) & -8) - size


class SampleGridModel(CustomIntEnum):
    MATCH_EDGES = 0
    MATCH_CENTERS = 1

    def __call__(
        self, width: int, height: int, src_width: float, src_height: float, shift: tuple[float, float], kwargs: KwargsT
    ) -> tuple[KwargsT, tuple[float, float]]:
        if self is SampleGridModel.MATCH_CENTERS:
            src_width = src_width * (width - 1) / (src_width - 1)
            src_height = src_height * (height - 1) / (src_height - 1)

            kwargs |= dict(src_width=src_width, src_height=src_height)
            shift_x, shift_y, *_ = tuple(
                (x / 2 + y for x, y in zip(((height - src_height), (width - src_width)), shift))
            )
            shift = shift_x, shift_y

        return kwargs, shift

    def for_dst(
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float], **kwargs: Any
    ) -> tuple[KwargsT, tuple[float, float]]:
        src_width = kwargs.get('src_width', width)
        src_height = kwargs.get('src_height', height)

        return self(src_width, src_height, width, height, shift, kwargs)

    def for_src(
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float], **kwargs: Any
    ) -> tuple[KwargsT, tuple[float, float]]:
        src_width = kwargs.get('src_width', clip.width)
        src_height = kwargs.get('src_height', clip.height)

        return self(width, height, src_width, src_height, shift, kwargs)


TopShift: TypeAlias = float
LeftShift: TypeAlias = float
TopFieldTopShift: TypeAlias = float
TopFieldLeftShift: TypeAlias = float
BotFieldTopShift: TypeAlias = float
BotFieldLeftShift: TypeAlias = float
Slope: TypeAlias = float
Center: TypeAlias = float
