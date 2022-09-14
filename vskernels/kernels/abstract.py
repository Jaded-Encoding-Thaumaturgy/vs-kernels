from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Union, cast, overload

import vapoursynth as vs
from vstools import (
    FuncExceptT, GenericVSFunction, HoldsVideoFormatT, Matrix, MatrixT, VideoFormatT, get_format, inject_self
)

from ..exceptions import UnknownKernelError

__all__ = [
    'Scaler',
    'Descaler',
    'Kernel',
    'KernelT'
]

core = vs.core


class Scaler(ABC):
    """
    Abstract scaling interface.
    """

    kwargs: dict[str, Any]
    """Arguments passed to the internal scale function"""

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    @abstractmethod
    @inject_self.cached
    def scale(
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0), **kwargs: Any
    ) -> vs.VideoNode:
        pass


class Descaler(ABC):
    @abstractmethod
    @inject_self.cached
    def descale(
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0), **kwargs: Any
    ) -> vs.VideoNode:
        pass


class Kernel(Scaler, Descaler):
    """
    Abstract scaling kernel interface.

    Additional kwargs supplied to constructor are passed only to the internal
    resizer, not the descale resizer.
    """

    scale_function: GenericVSFunction
    """Scale function called internally when scaling/resampling/shifting"""
    descale_function: GenericVSFunction
    """Descale function called internally when descaling"""

    @inject_self.cached
    def scale(  # type: ignore[override]
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0), **kwargs: Any
    ) -> vs.VideoNode:
        return self.scale_function(clip, **self.get_scale_args(clip, shift, width, height, **kwargs))

    @inject_self.cached
    def descale(  # type: ignore[override]
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0), **kwargs: Any
    ) -> vs.VideoNode:
        return self.descale_function(clip, **self.get_descale_args(clip, shift, width, height, **kwargs))

    @inject_self.cached
    def resample(
        self, clip: vs.VideoNode, format: int | VideoFormatT | HoldsVideoFormatT,
        matrix: MatrixT | None = None, matrix_in: MatrixT | None = None, **kwargs: Any
    ) -> vs.VideoNode:
        return self.scale_function(clip, **self.get_matrix_args(clip, format, matrix, matrix_in, **kwargs))

    @overload
    @inject_self.cached
    def shift(self, clip: vs.VideoNode, shift: tuple[float, float] = (0, 0), **kwargs: Any) -> vs.VideoNode:
        ...

    @overload
    @inject_self.cached
    def shift(
        self, clip: vs.VideoNode,
        shift_top: float | list[float] = 0.0, shift_left: float | list[float] = 0.0, **kwargs: Any
    ) -> vs.VideoNode:
        ...

    @inject_self.cached  # type: ignore
    def shift(
        self, clip: vs.VideoNode,
        shifts_or_top: float | tuple[float, float] | list[float] | None = None,
        shift_left: float | list[float] | None = None, **kwargs: Any
    ) -> vs.VideoNode:
        assert clip.format

        n_planes = clip.format.num_planes

        def _shift(src: vs.VideoNode, shift: tuple[float, float] = (0, 0)) -> vs.VideoNode:
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

        shifts_top = shifts_or_top if isinstance(shifts_or_top, list) else [shifts_or_top]
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

        planes = cast(list[vs.VideoNode], clip.std.SplitPlanes())

        shifted_planes = [
            plane if top == left == 0 else _shift(plane, (top, left))
            for plane, top, left in zip(planes, shifts_top, shifts_left)
        ]

        return core.std.ShufflePlanes(shifted_planes, [0, 0, 0], clip.format.color_family)

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        return dict(width=width, height=height) | kwargs

    def get_scale_args(
        self, clip: vs.VideoNode, shift: tuple[float, float] = (0, 0),
        width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        return dict(src_top=shift[0], src_left=shift[1]) | self.kwargs | self.get_params_args(
            False, clip, width, height, **kwargs
        )

    def get_descale_args(
        self, clip: vs.VideoNode, shift: tuple[float, float] = (0, 0),
        width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        return dict(src_top=shift[0], src_left=shift[1]) | self.get_params_args(True, clip, width, height, **kwargs)

    def get_matrix_args(
        self, clip: vs.VideoNode, format: int | VideoFormatT | HoldsVideoFormatT,
        matrix: MatrixT | None, matrix_in: MatrixT | None, **kwargs: Any
    ) -> dict[str, Any]:
        return dict(
            format=get_format(format).id,
            matrix=Matrix.from_param(matrix),
            matrix_in=Matrix.from_param(matrix_in)
        ) | self.kwargs | self.get_params_args(False, clip, **kwargs)

    @classmethod
    def from_param(cls: type[Kernel], kernel: KernelT, func_except: FuncExceptT | None = None) -> type[Kernel]:
        """
        Get a kernel by name.

        :param name:    Kernel name.

        :return:        Kernel class.

        :raise UnknownKernelError:  Some kind of unknown error occured.
        """
        from ..util import get_all_kernels

        if isinstance(kernel, str):
            all_kernels = get_all_kernels()
            search_str = kernel.lower().strip()

            for kernel_cls in all_kernels:
                if kernel_cls.__name__.lower() == search_str:
                    return kernel_cls

            raise UnknownKernelError(func_except or Kernel.from_param, kernel)

        if isinstance(kernel, Kernel):
            return kernel.__class__

        return kernel


KernelT = Union[str, type[Kernel], Kernel]
