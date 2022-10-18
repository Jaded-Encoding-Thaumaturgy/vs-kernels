from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Sequence, Union, cast, overload

from vstools import (
    CustomValueError, FuncExceptT, GenericVSFunction, HoldsVideoFormatT, Matrix, MatrixT, T, VideoFormatT, core,
    get_subclasses, get_video_format, inject_self, vs
)

from ..exceptions import UnknownDescalerError, UnknownKernelError, UnknownScalerError

__all__ = [
    'Scaler', 'ScalerT',
    'Descaler',
    'Kernel', 'KernelT'
]


class BaseScaler:
    @staticmethod
    def from_param(
        cls: type[T],
        value: str | type[T] | T,
        exception_cls: type[CustomValueError],
        excluded: Sequence[type[T]] = [],
        func_except: FuncExceptT | None = None
    ) -> type[T]:
        if isinstance(value, str):
            all_scalers = get_subclasses(Kernel, excluded)
            search_str = value.lower().strip()

            for scaler_cls in all_scalers:
                if scaler_cls.__name__.lower() == search_str:
                    return scaler_cls

            raise exception_cls(func_except or cls.from_param, value)

        if isinstance(value, cls):
            return value.__class__

        return cls

    @staticmethod
    def ensure_obj(
        cls: type[T],
        value: str | type[T] | T,
        exception_cls: type[CustomValueError],
        excluded: Sequence[type[T]] = [],
        func_except: FuncExceptT | None = None
    ) -> T:
        new_scaler: T | None = None

        if not isinstance(value, cls):
            try:
                new_scaler = cls.from_param(value, func_except)()
            except Exception:
                ...
        else:
            new_scaler = value

        if new_scaler is None:
            new_scaler = cls()

        if new_scaler.__class__ in excluded:
            raise exception_cls(
                'This {cls_name} can\'t be instantiated to be used!', cls_name=new_scaler.__class__
            )

        return new_scaler


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

    @classmethod
    def from_param(
        cls: type[Scaler], scaler: ScalerT | None = None, func_except: FuncExceptT | None = None
    ) -> type[Scaler]:
        return BaseScaler.from_param(cls, scaler, UnknownScalerError, [], func_except)

    @classmethod
    def ensure_obj(
        cls: type[Scaler], scaler: ScalerT | None = None, func_except: FuncExceptT | None = None
    ) -> Scaler:
        return BaseScaler.ensure_obj(cls, scaler, UnknownScalerError, [], func_except)


class Descaler(ABC):
    @abstractmethod
    @inject_self.cached
    def descale(
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0), **kwargs: Any
    ) -> vs.VideoNode:
        pass

    @classmethod
    def from_param(
        cls: type[Descaler], descaler: DescalerT | None = None, func_except: FuncExceptT | None = None
    ) -> type[Descaler]:
        return BaseScaler.from_param(cls, descaler, UnknownDescalerError, [], func_except)

    @classmethod
    def ensure_obj(
        cls: type[Descaler], descaler: DescalerT | None = None, func_except: FuncExceptT | None = None
    ) -> Descaler:
        return BaseScaler.ensure_obj(cls, descaler, UnknownDescalerError, [], func_except)


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
            format=get_video_format(format).id,
            matrix=Matrix.from_param(matrix),
            matrix_in=Matrix.from_param(matrix_in)
        ) | self.kwargs | self.get_params_args(False, clip, **kwargs)

    @classmethod
    def from_param(
        cls: type[Kernel], kernel: KernelT | None = None, func_except: FuncExceptT | None = None
    ) -> type[Kernel]:
        from ..util import excluded_kernels
        return BaseScaler.from_param(cls, kernel, UnknownKernelError, excluded_kernels, func_except)

    @classmethod
    def ensure_obj(
        cls: type[Kernel], kernel: KernelT | None = None, func_except: FuncExceptT | None = None
    ) -> Kernel:
        from ..util import excluded_kernels
        return BaseScaler.ensure_obj(cls, kernel, UnknownKernelError, excluded_kernels, func_except)


ScalerT = Union[str, type[Scaler], Scaler]
DescalerT = Union[str, type[Descaler], Descaler]
KernelT = Union[str, type[Kernel], Kernel]
