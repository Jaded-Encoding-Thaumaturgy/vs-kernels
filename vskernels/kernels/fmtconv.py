from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict, List, Tuple, TypeVar, cast, overload

import vapoursynth as vs
from vskernels.kernels.bicubic import Bicubic

from ..types import MatrixT, VideoFormatT, VSFunction
from .abstract import Kernel

core = vs.core

F = TypeVar('F', bound=Callable[..., Any])
call_wrapT = Callable[..., VSFunction]


class FmtConv(Kernel):
    """
    Abstract fmtconv's resizer.

    Dependencies:

    * fmtconv
    """

    @staticmethod
    def wrap_fmtc_func(function: F) -> VSFunction:
        @wraps(function)
        def _wrapper(self: FmtConv, clip: vs.VideoNode, **kwargs: Any) -> Any:
            assert clip.format

            bicubic = Bicubic()

            def _check_fmt(fmt: int | vs.PresetFormat | vs.VideoFormat) -> Tuple[vs.VideoFormat, bool]:
                if not isinstance(fmt, vs.VideoFormat):
                    fmt = core.get_video_format(fmt)

                return fmt, (
                    fmt.bits_per_sample == 32 and fmt.sample_type == vs.FLOAT
                ) or (
                    fmt.bits_per_sample == 16 and fmt.sample_type == vs.INTEGER
                )

            in_fmt = clip.format
            out_fmt = None

            csp = kwargs.get('csp', None)
            bits = kwargs.get('bits', None)
            flt = kwargs.get('flt', 0)

            if csp:
                out_fmt, valid = _check_fmt(csp)

                if not valid:
                    kwargs.pop('csp')
                else:
                    out_fmt = None
            else:
                out_fmt = in_fmt

            if bits:
                if not out_fmt:
                    out_fmt = in_fmt

                out_fmt = out_fmt.replace(bits_per_sample=bits)

            if not _check_fmt(in_fmt)[1]:
                clip = bicubic.resample(
                    clip, in_fmt.replace(bits_per_sample=16 * (1 + flt), sample_type=vs.SampleType(flt))
                )
            if out_fmt:
                out_fmt, valid = _check_fmt(out_fmt)
                if valid:
                    kwargs['csp'] = out_fmt
                    out_fmt = None

            filtered = function(clip, **kwargs)

            if not out_fmt:
                return filtered

            assert filtered.format
            return bicubic.resample(filtered, out_fmt)

        return cast(VSFunction, _wrapper)

    scale_function = wrap_fmtc_func(core.fmtc.resample)
    descale_function = wrap_fmtc_func(core.fmtc.resample)

    kernel: str
    """Name of the fmtconv kernel"""

    def __init__(self, taps: int = 4, **kwargs: Any) -> None:
        self.taps = taps
        super().__init__(**kwargs)

    def get_scale_args(
        self, clip: vs.VideoNode, shift: Tuple[float, float] = (0, 0),
        width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> Dict[str, Any]:
        return dict(
            sx=shift[1], sy=shift[0], kernel=self.kernel,
            **self.kwargs, **self.get_params_args(False, clip, width, height, **kwargs)
        )

    def get_descale_args(
        self, clip: vs.VideoNode, shift: Tuple[float, float] = (0, 0),
        width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> Dict[str, Any]:
        args = dict(
            invks=True, invkstaps=self.taps,
            **self.get_scale_args(clip, shift, width, height, **kwargs)
        )
        args.update(self.get_params_args(True, clip, width, height, **kwargs))
        return args

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> Dict[str, Any]:
        if is_descale:
            return dict(w=width, h=height, sw=width, sh=height, **kwargs)
        return dict(w=width, h=height, **kwargs)

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

        def _shift(shift_top: float | List[float] = 0.0, shift_left: float | List[float] = 0.0) -> vs.VideoNode:
            return self.scale_function(
                clip, sy=shift_top, sx=shift_left, kernel=self.kernel, **self.kwargs, **kwargs
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
        self, clip: vs.VideoNode, format: VideoFormatT,
        matrix: MatrixT | None = None, matrix_in: MatrixT | None = None, **kwargs: Any
    ) -> vs.VideoNode:
        raise NotImplementedError
