from __future__ import annotations

from typing import TYPE_CHECKING, Any, SupportsFloat, TypeVar, Union, cast

from stgpytools import inject_kwargs_params
from vstools import Dar, KwargsT, Resolution, Sar, VSFunctionAllArgs, check_correct_subsampling, inject_self, vs

from .abstract import Descaler, Kernel, Resampler, Scaler

__all__ = [
    'LinearScaler', 'LinearDescaler',

    'KeepArScaler',

    'ComplexScaler', 'ComplexScalerT',
    'ComplexKernel', 'ComplexKernelT'
]

XarT = TypeVar('XarT', Sar, Dar)


def _from_param(cls: type[XarT], value: XarT | bool | float | None, fallback: XarT) -> XarT | None:
    if value is False:
        return fallback

    if value is True:
        return None

    if isinstance(value, cls):
        return value

    if isinstance(value, SupportsFloat):
        return cls.from_float(float(value))

    return None


class _BaseLinearOperation:
    @staticmethod
    def _linear_op(op_name: str) -> Any:
        @inject_kwargs_params
        def func(
            self: _BaseLinearOperation, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0),
            *, linear: bool = False, sigmoid: bool | tuple[float, float] = False, **kwargs: Any
        ) -> vs.VideoNode:
            from ..util import LinearLight

            has_custom_op = hasattr(self, f'_linear_{op_name}')
            operation = cast(
                VSFunctionAllArgs,
                getattr(self, f'_linear_{op_name}') if has_custom_op else getattr(super(), op_name)  # type: ignore
            )

            if sigmoid:
                linear = True

            if not linear and not has_custom_op:
                return operation(clip, width, height, shift, **kwargs)

            resampler: Resampler | None = self if isinstance(self, Resampler) else None

            with LinearLight(clip, linear, sigmoid, resampler, kwargs.pop('format', None)) as ll:
                ll.linear = operation(ll.linear, width, height, shift, **kwargs)

            return ll.out

        return func


class LinearScaler(_BaseLinearOperation, Scaler):
    if TYPE_CHECKING:
        @inject_self.cached
        @inject_kwargs_params
        def scale(  # type: ignore[override]
            self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0),
            *, linear: bool = False, sigmoid: bool | tuple[float, float] = False, **kwargs: Any
        ) -> vs.VideoNode:
            ...
    else:
        scale = inject_self.cached(_BaseLinearOperation._linear_op('scale'))


class LinearDescaler(_BaseLinearOperation, Descaler):
    if TYPE_CHECKING:
        @inject_self.cached
        @inject_kwargs_params
        def descale(  # type: ignore[override]
            self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0),
            *, linear: bool = False, sigmoid: bool | tuple[float, float] = False, **kwargs: Any
        ) -> vs.VideoNode:
            ...
    else:
        descale = inject_self.cached(_BaseLinearOperation._linear_op('descale'))


class KeepArScaler(Scaler):
    def _get_kwargs_keep_ar(
        self, sar: Sar | float | bool | None = None, dar: Dar | float | bool | None = None, keep_ar: bool = False,
        **kwargs: Any
    ) -> KwargsT:
        kwargs = KwargsT(keep_ar=keep_ar, sar=sar, dar=dar) | kwargs

        if None not in set(kwargs.get(x) for x in ('keep_ar', 'sar', 'dar')):
            print(UserWarning(
                f'{self.__class__.__name__}.scale: "keep_ar" set '
                'with non-None values set in "sar" and "dar" won\'t do anything!'
            ))

        default_val = kwargs.pop('keep_ar')

        for key in ('sar', 'dar'):
            if kwargs[key] is None:
                kwargs[key] = default_val

        return kwargs

    def _handle_crop_resize_kwargs(  # type: ignore[override]
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float],
        sar: Sar | bool | float | None, dar: Dar | bool | float | None, **kwargs: Any
    ) -> tuple[KwargsT, tuple[float, float], Sar | None]:
        kwargs.setdefault('src_top', kwargs.pop('sy', shift[0]))
        kwargs.setdefault('src_left', kwargs.pop('sx', shift[1]))
        kwargs.setdefault('src_width', kwargs.pop('sw', clip.width))
        kwargs.setdefault('src_height', kwargs.pop('sh', clip.height))

        src_res = Resolution(kwargs['src_width'], kwargs['src_height'])

        src_sar = float(_from_param(Sar, sar, Sar(1, 1)) or Sar.from_clip(clip))
        out_sar = None

        src_dar = float(Dar.from_size(clip, False))
        out_dar = float(_from_param(Dar, dar, src_dar) or Dar.from_size(width, height))  # type: ignore

        if src_sar != 1.0:
            if src_sar > 1.0:
                out_dar = (width / src_sar) / height
            else:
                out_dar = width / (height * src_sar)

            out_sar = Sar(1, 1)

        if src_dar != out_dar:
            if src_dar > out_dar:
                src_shift, src_window = 'src_left', 'src_width'

                fix_crop = src_res.width - (src_res.height * out_dar)
            else:
                src_shift, src_window = 'src_top', 'src_height'

                fix_crop = src_res.height - (src_res.width / out_dar)

            fix_shift = fix_crop / 2

            kwargs[src_shift] += fix_shift
            kwargs[src_window] -= fix_crop

        out_shift = (kwargs.pop('src_top'), kwargs.pop('src_left'))

        return kwargs, out_shift, out_sar

    @inject_self.cached
    @inject_kwargs_params
    def scale(  # type: ignore[override]
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0), *,
        sar: Sar | float | bool | None = None, dar: Dar | float | bool | None = None, keep_ar: bool = False,
        **kwargs: Any
    ) -> vs.VideoNode:
        check_correct_subsampling(clip, width, height)

        const_size = 0 not in (clip.width, clip.height)

        if const_size:
            kwargs = self._get_kwargs_keep_ar(sar, dar, keep_ar, **kwargs)

            kwargs, shift, out_sar = self._handle_crop_resize_kwargs(clip, width, height, shift, **kwargs)

        kwargs = self.get_scale_args(clip, shift, width, height, **kwargs)

        clip = self.scale_function(clip, **kwargs)

        if const_size and out_sar:
            clip = out_sar.apply(clip)

        return clip


class ComplexScaler(LinearScaler, KeepArScaler):
    @inject_self.cached
    @inject_kwargs_params
    def scale(  # type: ignore[override]
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0),
        *,
        sar: Sar | bool | float | None = None, dar: Dar | bool | float | None = None, keep_ar: bool = False,
        linear: bool = False, sigmoid: bool | tuple[float, float] = False,
        **kwargs: Any
    ) -> vs.VideoNode:
        return super().scale(
            clip, width, height, shift, sar=sar, dar=dar, keep_ar=keep_ar, linear=linear, sigmoid=sigmoid, **kwargs
        )


class ComplexKernel(Kernel, LinearDescaler, ComplexScaler):  # type: ignore
    ...


ComplexScalerT = Union[str, type[ComplexScaler], ComplexScaler]
ComplexKernelT = Union[str, type[ComplexKernel], ComplexKernel]
