from __future__ import annotations

from typing import Any, List, Tuple, overload

import vapoursynth as vs

from ..types import Matrix, VideoFormatT
from .abstract import Kernel

core = vs.core


class Example(Kernel):
    """Example Kernel class for documentation purposes."""

    def __init__(self, b: float = 0, c: float = 1/2, **kwargs: Any) -> None:
        self.b = b
        self.c = c
        super().__init__(**kwargs)

    def scale(self, clip: vs.VideoNode, width: int, height: int, shift: Tuple[float, float] = (0, 0)) -> vs.VideoNode:
        """
        Perform a regular scaling operation.

        :param clip:        Input clip
        :param width:       Output width
        :param height:      Output height
        :param shift:       Shift clip during the operation.
                            Expects a tuple of (src_top, src_left).

        :rtype:             ``VideoNode``
        """
        return core.resize.Bicubic(
            clip, width, height, src_top=shift[0], src_left=shift[1],
            filter_param_a=self.b, filter_param_b=self.c, **self.kwargs
        )

    def descale(self, clip: vs.VideoNode, width: int, height: int, shift: Tuple[float, float] = (0, 0)) -> vs.VideoNode:
        """
        Perform a regular descaling operation.

        :param clip:        Input clip
        :param width:       Output width
        :param height:      Output height
        :param shift:       Shift clip during the operation.
                            Expects a tuple of (src_top, src_left).

        :rtype:             ``VideoNode``
        """
        return core.descale.Debicubic(
            clip, width, height, b=self.b, c=self.c, src_top=shift[0], src_left=shift[1]
        )

    def resample(
        self, clip: vs.VideoNode, format: VideoFormatT, matrix: Matrix | None = None, matrix_in: Matrix | None = None
    ) -> vs.VideoNode:
        """
        Perform a regular resampling operation.

        :param clip:        Input clip
        :param format:      Output format
        :param matrix:      Output matrix. If `None`, will take the matrix from the input clip's frameprops.
        :param matrix_in:   Input matrix. If `None`, will take the matrix from the input clip's frameprops.

        :rtype:             ``VideoNode``
        """
        return core.resize.Bicubic(
            clip, format=int(format),
            filter_param_a=self.b, filter_param_b=self.c,
            matrix=matrix, matrix_in=matrix_in, **self.kwargs
        )

    @overload  # type: ignore
    def shift(self, clip: vs.VideoNode, shift: Tuple[float, float] = (0, 0)) -> vs.VideoNode:
        ...

    def shift(  # type: ignore
        self, clip: vs.VideoNode,
        shift_top: float | List[float] = 0.0, shift_left: float | List[float] = 0.0
    ) -> vs.VideoNode:
        """
        Perform a regular shifting operation.

        :param clip:        Input clip
        :param shift:       Shift clip during the operation.\n
                            Expects a tuple of (src_top, src_left)\n
                            or two top, left arrays for shifting planes individually.

        :rtype:             ``VideoNode``
        """
        return core.resize.Bicubic(
            clip, src_top=shift_top, src_left=shift_left,  # type: ignore
            filter_param_a=self.b, filter_param_b=self.c,
            **self.kwargs
        )
