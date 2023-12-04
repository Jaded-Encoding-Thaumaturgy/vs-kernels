from __future__ import annotations

from functools import lru_cache
from inspect import Signature
from math import ceil
from typing import Any, Callable, Sequence, Union, cast, overload

from stgpytools import inject_kwargs_params
from vstools import (
    CustomIndexError, CustomValueError, FieldBased, FuncExceptT, GenericVSFunction, HoldsVideoFormatT, KwargsT, Matrix,
    MatrixT, T, VideoFormatT, check_correct_subsampling, check_variable_resolution, core, depth, expect_bits,
    get_subclasses, get_video_format, inject_self, vs, vs_object
)

from ..exceptions import UnknownDescalerError, UnknownKernelError, UnknownScalerError

__all__ = [
    'Scaler', 'ScalerT',
    'Descaler', 'DescalerT',
    'Resampler', 'ResamplerT',
    'Kernel', 'KernelT'
]


def _default_kernel_radius(cls: type[T], self: T) -> int:
    if hasattr(self, '_static_kernel_radius'):
        return ceil(self._static_kernel_radius)  # type: ignore

    try:
        return super(cls, self).kernel_radius  # type: ignore
    except AttributeError:
        ...

    raise NotImplementedError


@lru_cache
def _get_keywords(_methods: tuple[Callable[..., Any] | None, ...], self: Any) -> set[str]:
    methods_list = list(_methods)

    for cls in self.__class__.mro():
        if hasattr(cls, 'get_implemented_funcs'):
            methods_list.extend(cls.get_implemented_funcs(self))

    methods = {*methods_list} - {None}

    keywords = set[str]()

    for method in methods:
        try:
            try:
                signature = method.__signature__  # type: ignore
            except Exception:
                signature = Signature.from_callable(method)  # type: ignore

            keywords.update(signature.parameters.keys())
        except Exception:
            ...

    return keywords


def _clean_self_kwargs(methods: tuple[Callable[..., Any] | None, ...], self: Any) -> KwargsT:
    return {k: v for k, v in self.kwargs.items() if k not in _get_keywords(methods, self)}


def _base_from_param(
    cls: type[T],
    basecls: type[T],
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
                return scaler_cls  # type: ignore

        raise exception_cls(func_except or cls.from_param, value)  # type: ignore

    if isinstance(value, type) and issubclass(value, basecls):
        return value

    if isinstance(value, cls):
        return value.__class__

    return cls


def _base_ensure_obj(
    cls: type[T],
    basecls: type[T],
    value: str | type[T] | T | None,
    exception_cls: type[CustomValueError],
    excluded: Sequence[type] = [],
    func_except: FuncExceptT | None = None
) -> T:
    new_scaler: T

    if value is None:
        new_scaler = cls()
    elif isinstance(value, cls) or isinstance(value, basecls):
        new_scaler = value
    else:
        new_scaler = cls.from_param(value, func_except)()  # type: ignore

    if new_scaler.__class__ in excluded:
        raise exception_cls(
            func_except or cls.ensure_obj, new_scaler.__class__,  # type: ignore
            'This {cls_name} can\'t be instantiated to be used!',
            cls_name=new_scaler.__class__
        )

    return new_scaler


class Scaler(vs_object):
    """
    Abstract scaling interface.
    """

    kwargs: KwargsT
    """Arguments passed to the internal scale function"""

    scale_function: GenericVSFunction
    """Scale function called internally when scaling/resampling/shifting"""

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    @inject_self.cached
    @inject_kwargs_params
    def scale(  # type: ignore[override]
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0), **kwargs: Any
    ) -> vs.VideoNode:
        check_correct_subsampling(clip, width, height)
        return self.scale_function(clip, **self.get_scale_args(clip, shift, width, height, **kwargs))

    @classmethod
    def from_param(
        cls: type[Scaler], scaler: ScalerT | None = None, func_except: FuncExceptT | None = None
    ) -> type[Scaler]:
        return _base_from_param(cls, Scaler, scaler, UnknownScalerError, [], func_except)  # type: ignore

    @classmethod
    def ensure_obj(
        cls: type[Scaler], scaler: ScalerT | None = None, func_except: FuncExceptT | None = None
    ) -> Scaler:
        return _base_ensure_obj(cls, Scaler, scaler, UnknownScalerError, [], func_except)  # type: ignore

    @inject_self.cached
    def multi(
        self, clip: vs.VideoNode, multi: float = 2, shift: tuple[float, float] = (0, 0), **kwargs: Any
    ) -> vs.VideoNode:
        assert check_variable_resolution(clip, self.multi)

        dst_width, dst_height = ceil(clip.width * multi), ceil(clip.height * multi)

        if max(dst_width, dst_height) <= 0.0:
            raise CustomValueError(
                'Multiplying the resolution by "multi" must result in a positive resolution!', self.multi, multi
            )

        return self.scale(clip, dst_width, dst_height, shift, **kwargs)

    @inject_self.property
    def kernel_radius(self) -> int:
        return _default_kernel_radius(__class__, self)  # type: ignore

    def get_scale_args(
        self, clip: vs.VideoNode, shift: tuple[float, float] = (0, 0),
        width: int | None = None, height: int | None = None,
        *funcs: Callable[..., Any], **kwargs: Any
    ) -> KwargsT:
        return (
            dict(src_top=shift[0], src_left=shift[1])
            | self.get_clean_kwargs(*funcs)
            | dict(width=width, height=height)
            | kwargs
        )

    def get_clean_kwargs(self, *funcs: Callable[..., Any] | None) -> KwargsT:
        return _clean_self_kwargs(funcs, self)

    def get_implemented_funcs(self) -> tuple[Callable[..., Any]]:
        return (self.scale, self.multi)  # type: ignore


class Descaler(vs_object):
    kwargs: KwargsT
    """Arguments passed to the internal descale function"""

    descale_function: GenericVSFunction
    """Descale function called internally when descaling"""

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    @inject_self.cached
    @inject_kwargs_params
    def descale(  # type: ignore[override]
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0), **kwargs: Any
    ) -> vs.VideoNode:
        check_correct_subsampling(clip, width, height)

        field_based = FieldBased.from_param_or_video(kwargs.pop('field_based', None), clip)

        clip, bits = expect_bits(clip, 32)

        de_kwargs = self.get_descale_args(clip, shift, width, height // (1 + field_based.is_inter), **kwargs)

        if field_based.is_inter:
            if height % 2:
                raise CustomIndexError('You can\'t descale to odd resolution when crossconverted!', self.descale)

            top_shift, field_shift = de_kwargs.get('src_top', 0.0), 0.125 * height / clip.height

            fields = clip.std.SeparateFields(field_based.is_tff)

            interleaved = core.std.Interleave([
                self.descale_function(fields[offset::2], **(de_kwargs | dict(src_top=top_shift + (field_shift * mult))))
                for offset, mult in [(0, 1), (1, -1)]
            ])

            descaled = interleaved.std.DoubleWeave(field_based.is_tff)[::2]
        else:
            descaled = self.descale_function(clip, **de_kwargs)

        return depth(descaled, bits)

    @classmethod
    def from_param(
        cls: type[Descaler], descaler: DescalerT | None = None, func_except: FuncExceptT | None = None
    ) -> type[Descaler]:
        return _base_from_param(cls, Descaler, descaler, UnknownDescalerError, [], func_except)  # type: ignore

    @classmethod
    def ensure_obj(
        cls: type[Descaler], descaler: DescalerT | None = None, func_except: FuncExceptT | None = None
    ) -> Descaler:
        return _base_ensure_obj(cls, Descaler, descaler, UnknownDescalerError, [], func_except)  # type: ignore

    @inject_self.property
    def kernel_radius(self) -> int:
        return _default_kernel_radius(__class__, self)  # type: ignore

    def get_descale_args(
        self, clip: vs.VideoNode, shift: tuple[float, float] = (0, 0),
        width: int | None = None, height: int | None = None,
        *funcs: Callable[..., Any], **kwargs: Any
    ) -> KwargsT:
        return (
            dict(src_top=shift[0], src_left=shift[1])
            | self.get_clean_kwargs(*funcs)
            | dict(width=width, height=height) | kwargs
        )

    def get_clean_kwargs(self, *funcs: Callable[..., Any] | None) -> KwargsT:
        return _clean_self_kwargs(funcs, self)

    def get_implemented_funcs(self) -> tuple[Callable[..., Any]]:
        return (self.descale, )


class Resampler(vs_object):
    kwargs: KwargsT
    """Arguments passed to the internal resampling function"""

    resample_function: GenericVSFunction
    """Resample function called internally when resampling"""

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    @inject_self.cached
    @inject_kwargs_params
    def resample(
        self, clip: vs.VideoNode, format: int | VideoFormatT | HoldsVideoFormatT,
        matrix: MatrixT | None = None, matrix_in: MatrixT | None = None, **kwargs: Any
    ) -> vs.VideoNode:
        return self.resample_function(clip, **self.get_resample_args(clip, format, matrix, matrix_in, **kwargs))

    @classmethod
    def from_param(
        cls: type[Resampler], resampler: ResamplerT | None = None, func_except: FuncExceptT | None = None
    ) -> type[Resampler]:
        return _base_from_param(cls, Resampler, resampler, UnknownDescalerError, [], func_except)  # type: ignore

    @classmethod
    def ensure_obj(
        cls: type[Resampler], resampler: ResamplerT | None = None, func_except: FuncExceptT | None = None
    ) -> Resampler:
        return _base_ensure_obj(cls, Resampler, resampler, UnknownDescalerError, [], func_except)  # type: ignore

    @inject_self.property
    def kernel_radius(self) -> int:
        return _default_kernel_radius(__class__, self)  # type: ignore

    def get_resample_args(
        self, clip: vs.VideoNode, format: int | VideoFormatT | HoldsVideoFormatT,
        matrix: MatrixT | None, matrix_in: MatrixT | None,
        *funcs: Callable[..., Any], **kwargs: Any
    ) -> KwargsT:
        return dict(
            format=get_video_format(format).id,
            matrix=Matrix.from_param(matrix),
            matrix_in=Matrix.from_param(matrix_in)
        ) | self.get_clean_kwargs(*funcs) | kwargs

    def get_clean_kwargs(self, *funcs: Callable[..., Any] | None) -> KwargsT:
        return _clean_self_kwargs(funcs, self)

    def get_implemented_funcs(self) -> tuple[Callable[..., Any]]:
        return (self.resample, )


class Kernel(Scaler, Descaler, Resampler):  # type: ignore
    """
    Abstract scaling kernel interface.

    Additional kwargs supplied to constructor are passed only to the internal
    resizer, not the descale resizer.
    """

    @overload  # type: ignore
    @inject_self.cached
    @inject_kwargs_params
    def shift(self, clip: vs.VideoNode, shift: tuple[float, float] = (0, 0), **kwargs: Any) -> vs.VideoNode:
        ...

    @overload  # type: ignore
    @inject_self.cached
    @inject_kwargs_params
    def shift(
        self, clip: vs.VideoNode,
        shift_top: float | list[float] = 0.0, shift_left: float | list[float] = 0.0, **kwargs: Any
    ) -> vs.VideoNode:
        ...

    @inject_self.cached  # type: ignore
    @inject_kwargs_params
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

    @overload
    @classmethod
    def from_param(
        cls: type[Kernel], kernel: KernelT | None = None, func_except: FuncExceptT | None = None
    ) -> type[Kernel]:
        ...

    @overload
    @classmethod
    def from_param(  # type: ignore
        cls: type[Kernel], kernel: ScalerT | KernelT | None = None, func_except: FuncExceptT | None = None
    ) -> type[Scaler]:
        ...

    @overload
    @classmethod
    def from_param(  # type: ignore
        cls: type[Kernel], kernel: DescalerT | KernelT | None = None, func_except: FuncExceptT | None = None
    ) -> type[Descaler]:
        ...

    @overload
    @classmethod
    def from_param(
        cls: type[Kernel], kernel: ResamplerT | KernelT | None = None, func_except: FuncExceptT | None = None
    ) -> type[Resampler]:
        ...

    @classmethod
    def from_param(
        cls: type[Kernel], kernel: ScalerT | DescalerT | ResamplerT | KernelT | None = None,
        func_except: FuncExceptT | None = None
    ) -> type[Scaler] | type[Descaler] | type[Resampler] | type[Kernel]:
        from ..util import abstract_kernels
        return _base_from_param(
            cls, Kernel, kernel, UnknownKernelError, abstract_kernels, func_except  # type: ignore
        )

    @overload
    @classmethod
    def ensure_obj(
        cls: type[Kernel], kernel: KernelT | None = None, func_except: FuncExceptT | None = None
    ) -> Kernel:
        ...

    @overload
    @classmethod
    def ensure_obj(  # type: ignore
        cls: type[Kernel], kernel: ScalerT | KernelT | None = None, func_except: FuncExceptT | None = None
    ) -> Scaler:
        ...

    @overload
    @classmethod
    def ensure_obj(  # type: ignore
        cls: type[Kernel], kernel: DescalerT | KernelT | None = None, func_except: FuncExceptT | None = None
    ) -> Descaler:
        ...

    @overload
    @classmethod
    def ensure_obj(
        cls: type[Kernel], kernel: ResamplerT | KernelT | None = None, func_except: FuncExceptT | None = None
    ) -> Resampler:
        ...

    @classmethod
    def ensure_obj(
        cls: type[Kernel], kernel: ScalerT | DescalerT | ResamplerT | KernelT | None = None,
        func_except: FuncExceptT | None = None
    ) -> Scaler | Descaler | Resampler | Kernel:
        from ..util import abstract_kernels
        return _base_ensure_obj(  # type: ignore
            cls, Kernel, kernel, UnknownKernelError, abstract_kernels, func_except
        )

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> KwargsT:
        return dict(width=width, height=height) | kwargs

    def get_scale_args(
        self, clip: vs.VideoNode, shift: tuple[float, float] = (0, 0),
        width: int | None = None, height: int | None = None,
        *funcs: Callable[..., Any], **kwargs: Any
    ) -> KwargsT:
        return (
            dict(src_top=shift[0], src_left=shift[1])
            | self.get_clean_kwargs(*funcs)
            | self.get_params_args(False, clip, width, height, **kwargs)
        )

    def get_descale_args(
        self, clip: vs.VideoNode, shift: tuple[float, float] = (0, 0),
        width: int | None = None, height: int | None = None,
        *funcs: Callable[..., Any], **kwargs: Any
    ) -> KwargsT:
        return (
            dict(src_top=shift[0], src_left=shift[1])
            | self.get_clean_kwargs(*funcs)
            | self.get_params_args(True, clip, width, height, **kwargs)
        )

    def get_resample_args(
        self, clip: vs.VideoNode, format: int | VideoFormatT | HoldsVideoFormatT,
        matrix: MatrixT | None, matrix_in: MatrixT | None,
        *funcs: Callable[..., Any], **kwargs: Any
    ) -> KwargsT:
        return (
            dict(
                format=get_video_format(format).id, matrix=Matrix.from_param(matrix),
                matrix_in=Matrix.from_param(matrix_in)
            )
            | self.get_clean_kwargs(*funcs)
            | self.get_params_args(False, clip, **kwargs)
        )

    def get_implemented_funcs(self) -> tuple[Callable[..., Any]]:
        return (self.shift, )  # type: ignore


ScalerT = Union[str, type[Scaler], Scaler]
DescalerT = Union[str, type[Descaler], Descaler]
ResamplerT = Union[str, type[Resampler], Resampler]
KernelT = Union[str, type[Kernel], Kernel]
