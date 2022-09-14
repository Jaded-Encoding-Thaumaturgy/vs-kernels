from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Tuple, cast, overload

import vapoursynth as vs

from ..types import MatrixT, VideoFormatT

core = vs.core


class Scaler(ABC):
    """
    Abstract scaling interface.
    """

    kwargs: Dict[str, Any]
    """Arguments passed to the internal scale function"""

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    @abstractmethod
    def scale(
        self, clip: vs.VideoNode, width: int, height: int, shift: Tuple[float, float] = (0, 0), **kwargs: Any
    ) -> vs.VideoNode:
        pass


class Descaler(ABC):
    @abstractmethod
    def descale(
        self, clip: vs.VideoNode, width: int, height: int, shift: Tuple[float, float] = (0, 0), **kwargs: Any
    ) -> vs.VideoNode:
        pass


class Kernel(Scaler, Descaler):
    """
    Abstract scaling kernel interface.

    Additional kwargs supplied to constructor are passed only to the internal
    resizer, not the descale resizer.
    """

    scale_function: Callable[..., vs.VideoNode]
    """Scale function called internally when scaling/resampling/shifting"""
    descale_function: Callable[..., vs.VideoNode]
    """Descale function called internally when descaling"""

    def scale(
        self, clip: vs.VideoNode, width: int, height: int, shift: Tuple[float, float] = (0, 0), **kwargs: Any
    ) -> vs.VideoNode:
        return self.scale_function(clip, **self.get_scale_args(clip, shift, width, height, **kwargs))

    def descale(
        self, clip: vs.VideoNode, width: int, height: int, shift: Tuple[float, float] = (0, 0), **kwargs: Any
    ) -> vs.VideoNode:
        return self.descale_function(clip, **self.get_descale_args(clip, shift, width, height, **kwargs))

    def resample(
        self, clip: vs.VideoNode, format: VideoFormatT,
        matrix: MatrixT | None = None, matrix_in: MatrixT | None = None, **kwargs: Any
    ) -> vs.VideoNode:
        return self.scale_function(clip, **self.get_matrix_args(clip, format, matrix, matrix_in, **kwargs))

    @overload
    def shift(self, clip: vs.VideoNode, shift: Tuple[float, float] = (0, 0), **kwargs: Any) -> vs.VideoNode:
        ...

    @overload
    def shift(
        self, clip: vs.VideoNode,
        shift_top: float | List[float] = 0.0, shift_left: float | List[float] = 0.0, **kwargs: Any
    ) -> vs.VideoNode:
        ...

    def shift(  # type: ignore
        self, clip: vs.VideoNode,
        shifts_or_top: float | Tuple[float, float] | List[float] | None = None,
        shift_left: float | List[float] | None = None, **kwargs: Any
    ) -> vs.VideoNode:
        assert clip.format

        n_planes = clip.format.num_planes

        def _shift(src: vs.VideoNode, shift: Tuple[float, float] = (0, 0)) -> vs.VideoNode:
            return self.scale_function(src, **self.get_scale_args(src, shift, **kwargs))

        if not shifts_or_top and not shift_left:
            return _shift(clip)
        elif isinstance(shifts_or_top, tuple):
            return _shift(clip, shifts_or_top)
        elif isinstance(shifts_or_top, float) and isinstance(shift_left, float):
            return _shift(clip, (shifts_or_top, shift_left))

        if shifts_or_top is None:
            shifts_or_top = 0.0
        if shift_left is None:
            shift_left = 0.0

        shifts_top = shifts_or_top if isinstance(shifts_or_top, List) else [shifts_or_top]
        shifts_left = shift_left if isinstance(shift_left, list) else [shift_left]

        if not shifts_top:
            shifts_top = [0.0] * n_planes
        elif (ltop := len(shifts_top)) > n_planes:
            shifts_top = shifts_top[:n_planes]
        else:
            shifts_top += shifts_top[-1:] * (n_planes - ltop)

        if not shifts_left:
            shifts_left = [0.0] * n_planes
        elif (lleft := len(shifts_left)) > n_planes:
            shifts_left = shifts_left[:n_planes]
        else:
            shifts_left += shifts_left[-1:] * (n_planes - lleft)

        if len(set(shifts_top)) == len(set(shifts_left)) == 1 or n_planes == 1:
            return _shift(clip, (shifts_top[0], shifts_left[0]))

        planes = cast(List[vs.VideoNode], clip.std.SplitPlanes())

        shifted_planes = [
            plane if top == left == 0 else _shift(plane, (top, left))
            for plane, top, left in zip(planes, shifts_top, shifts_left)
        ]

        return core.std.ShufflePlanes(shifted_planes, [0, 0, 0], clip.format.color_family)

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> Dict[str, Any]:
        return dict(width=width, height=height) | kwargs

    def get_scale_args(
        self, clip: vs.VideoNode, shift: Tuple[float, float] = (0, 0),
        width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> Dict[str, Any]:
        return dict(src_top=shift[0], src_left=shift[1]) | self.kwargs | self.get_params_args(
            False, clip, width, height, **kwargs
        )

    def get_descale_args(
        self, clip: vs.VideoNode, shift: Tuple[float, float] = (0, 0),
        width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> Dict[str, Any]:
        return dict(src_top=shift[0], src_left=shift[1]) | self.get_params_args(True, clip, width, height, **kwargs)

    def get_matrix_args(
        self, clip: vs.VideoNode, format: VideoFormatT, matrix: MatrixT | None, matrix_in: MatrixT | None, **kwargs: Any
    ) -> Dict[str, Any]:
        return dict(
            format=int(format), matrix=matrix, matrix_in=matrix_in
        ) | self.kwargs | self.get_params_args(False, clip, **kwargs)
