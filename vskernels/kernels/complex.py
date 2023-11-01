from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

from vstools import KwargsT, Resolution, Sar, inject_self, vs

from .abstract import Descaler, Kernel, Scaler

__all__ = [
    'LinearScaler', 'LinearDescaler',

    'KeepArScaler',

    'ComplexScaler', 'ComplexScalerT',
    'ComplexKernel', 'ComplexKernelT'
]


class _BaseLinearOperation:
    orig_kwargs = {}

    def __init__(self, **kwargs: Any) -> None:
        self.orig_kwargs = kwargs
        self.kwargs = {k: v for k, v in kwargs.items() if k not in ('linear', 'sigmoid')}

    @staticmethod
    def _linear_op(op_name: str) -> Any:
        def func(
            self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0),
            *, linear: bool = False, sigmoid: bool | tuple[float, float] = False, **kwargs: Any
        ) -> vs.VideoNode:
            from ..util import LinearLight

            has_custom_op = hasattr(self, f'_linear_{op_name}')
            operation = getattr(self, f'_linear_{op_name}') if has_custom_op else getattr(super(), op_name)
            sigmoid = self.orig_kwargs.get('sigmoid', sigmoid)
            linear = self.orig_kwargs.get('linear', False) or linear or not not sigmoid

            if not linear and not has_custom_op:
                return operation(clip, width, height, shift, **kwargs)

            with LinearLight(clip, linear, sigmoid, self) as ll:
                ll.linear = operation(ll.linear, width, height, shift, **kwargs)

            return ll.out

        return func


class LinearScaler(_BaseLinearOperation, Scaler):
    if TYPE_CHECKING:
        @inject_self.cached
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
        def descale(  # type: ignore[override]
            self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0),
            *, linear: bool = False, sigmoid: bool | tuple[float, float] = False, **kwargs: Any
        ) -> vs.VideoNode:
            ...
    else:
        descale = inject_self.cached(_BaseLinearOperation._linear_op('descale'))


class KeepArScaler(Scaler):
    def _handle_crop_resize_kwargs(  # type: ignore[override]
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0),
        **kwargs: Any
    ) -> tuple[KwargsT, tuple[float, float], Sar]:
        kwargs.setdefault('src_top', kwargs.pop('sy', shift[0]))
        kwargs.setdefault('src_left', kwargs.pop('sx', shift[1]))
        kwargs.setdefault('src_width', kwargs.pop('sw', clip.width))
        kwargs.setdefault('src_height', kwargs.pop('sh', clip.height))

        src_res = Resolution(kwargs['src_width'], kwargs['src_height'])
        out_res = Resolution(width, height)

        sar = Sar.from_clip(clip)

        if sar.numerator != sar.denominator:
            sar_f = sar.numerator / sar.denominator

            if sar_f > 1:
                out_res = Resolution(out_res.width / sar_f, out_res.height)
            else:
                out_res = Resolution(out_res.width, out_res.height * sar_f)

            sar = Sar(1, 1)

        src_dar, out_dar = src_res.width / src_res.height, out_res.width / out_res.height

        if src_dar != out_dar:
            if src_dar > out_dar:
                src_res, out_res = src_res.transpose(), out_res.transpose()
                src_shift, src_window = 'src_left', 'src_width'
            else:
                src_shift, src_window = 'src_top', 'src_height'

            fix_scale = src_res.width / out_res.width
            fix_crop = src_res.height - (out_res.height * fix_scale)
            fix_shift = fix_crop / 2

            kwargs[src_shift] = kwargs.get(src_shift, 0) + fix_shift
            kwargs[src_window] = kwargs[src_window] - fix_crop

        out_shift = (kwargs.pop('src_top'), kwargs.pop('src_left'))

        return kwargs, out_shift, sar

    @inject_self.cached
    def scale(  # type: ignore[override]
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0),
        *, keep_ar: bool = False, **kwargs: Any
    ) -> vs.VideoNode:
        if keep_ar:
            kwargs, shift, sar = self._handle_crop_resize_kwargs(clip, width, height, shift, **kwargs)
        check_correct_subsampling(clip, width, height)

        kwargs = self.get_scale_args(clip, shift, width, height, **kwargs)

        clip = self.scale_function(clip, **kwargs)

        if keep_ar:
            clip = sar.apply(clip)

        return clip


class ComplexScaler(LinearScaler, KeepArScaler):
    if TYPE_CHECKING:
        @inject_self.cached
        def scale(  # type: ignore[override]
            self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0),
            *, keep_ar: bool = False, linear: bool = False, sigmoid: bool | tuple[float, float] = False,
            **kwargs: Any
        ) -> vs.VideoNode:
            ...


class ComplexKernel(Kernel, LinearDescaler, ComplexScaler):
    ...


ComplexScalerT = Union[str, type[ComplexScaler], ComplexScaler]
ComplexKernelT = Union[str, type[ComplexKernel], ComplexKernel]
