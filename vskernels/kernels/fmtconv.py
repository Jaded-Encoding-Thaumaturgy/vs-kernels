from __future__ import annotations

from typing import Any, Dict, List, Tuple, overload

import vapoursynth as vs

from ..types import Matrix, VideoFormatT
from .abstract import Kernel

core = vs.core


class FmtConv(Kernel):
    """
    Abstract fmtconv's resizer.

    Dependencies:

    * fmtconv
    """

    scale_function = core.fmtc.resample
    descale_function = core.fmtc.resample

    kernel: str
    """Name of the fmtconv kernel"""

    def __init__(self, taps: int = 4, **kwargs: Any) -> None:
        self.taps = taps
        super().__init__(**kwargs)

    def get_scale_args(
        self, clip: vs.VideoNode, shift: Tuple[float, float] = (0, 0),
        width: int | None = None, height: int | None = None,
    ) -> Dict[str, Any]:
        return dict(
            sx=shift[1], sy=shift[0], kernel=self.kernel,
            **self.kwargs, **self.get_params_args(False, clip, width, height)
        )

    def get_descale_args(
        self, clip: vs.VideoNode, shift: Tuple[float, float] = (0, 0),
        width: int | None = None, height: int | None = None,
    ) -> Dict[str, Any]:
        return dict(
            **self.get_scale_args(clip, shift, width, height),
            invks=True, invkstaps=self.taps,
            **self.get_params_args(True, clip, width, height)
        )

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None
    ) -> Dict[str, Any]:
        if is_descale:
            return dict(w=width, h=height, sw=width, sh=height)
        return dict(w=width, h=height)

    @overload
    def shift(self, clip: vs.VideoNode, shift: Tuple[float, float] = (0, 0)) -> vs.VideoNode:
        ...

    @overload
    def shift(
        self, clip: vs.VideoNode,
        shift_top: float | List[float] = 0.0, shift_left: float | List[float] = 0.0
    ) -> vs.VideoNode:
        ...

    def shift(  # type: ignore
        self, clip: vs.VideoNode,
        shifts_or_top: float | Tuple[float, float] | List[float] | None = None,
        shift_left: float | List[float] | None = None
    ) -> vs.VideoNode:
        assert clip.format

        n_planes = clip.format.num_planes

        def _shift(shift_top: float | List[float] = 0.0, shift_left: float | List[float] = 0.0) -> vs.VideoNode:
            return self.scale_function(
                clip, sy=shift_top, sx=shift_left, kernel=self.kernel, **self.kwargs
            )

        if not shifts_or_top and not shift_left:
            return _shift()
        elif isinstance(shifts_or_top, tuple):
            return _shift(*shifts_or_top)
        elif isinstance(shifts_or_top, float) and isinstance(shift_left, float):
            return _shift(shifts_or_top, shift_left)

        shifts_top = shifts_or_top or 0.0
        if isinstance(shifts_top, list):
            if not shifts_top:
                shifts_top = [0.0] * n_planes
            elif len(shifts_top) > n_planes:
                shifts_top[:n_planes]

        shifts_left = shift_left or 0.0
        if isinstance(shifts_left, list):
            if not shifts_left:
                shifts_left = [0.0] * n_planes
            elif len(shifts_left) > n_planes:
                shifts_left = shifts_left[:n_planes]

        return _shift(shifts_top, shifts_left)

    def get_matrix_args(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        raise NotImplementedError

    def resample(
        self, clip: vs.VideoNode, format: VideoFormatT, matrix: Matrix | None = None, matrix_in: Matrix | None = None
    ) -> vs.VideoNode:
        raise NotImplementedError
