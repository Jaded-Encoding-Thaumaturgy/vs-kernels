from __future__ import annotations

from dataclasses import dataclass
from math import exp
from typing import Any

from vstools import CustomValueError, HoldsVideoFormatT, Matrix, MatrixT, Transfer, cachedproperty, depth, inject_self, vs, CustomRuntimeError, get_video_format

from .kernels import Bicubic, Catrom, FmtConv, Impulse, Kernel, KernelT, Placebo, Point, Scaler
from .kernels.docs import Example

__all__ = [
    'excluded_kernels',
    'NoShift', 'NoScale',

    'LinearLight',

    'resample_to'
]


class NoShiftBase(Kernel):
    def get_scale_args(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return super().get_scale_args(clip, (0, 0), *(args and args[1:]), **kwargs)

    def get_descale_args(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return super().get_descale_args(clip, (0, 0), *(args and args[1:]), **kwargs)


class NoShift(Bicubic, NoShiftBase):  # type: ignore
    """
    Class util used to always pass shift=(0, 0)\n
    By default it inherits from :py:class:`vskernels.Bicubic`,
    this behaviour can be changed with :py:attr:`Noshift.from_kernel`\n

    Use case, for example vsaa's ZNedi3:
    ```
    test = ...  # some clip, 480x480
    doubled_no_shift = Znedi3(field=0, nsize=4, nns=3, shifter=NoShift).scale(test, 960, 960)
    down = Point.scale(double, 480, 480)
    ```
    """

    def __class_getitem__(cls, kernel: KernelT) -> type[Kernel]:
        return cls.from_kernel(kernel)

    @staticmethod
    def from_kernel(kernel: KernelT) -> type[Kernel]:
        """
        Function or decorator for making a kernel not shift.

        As example, in vsaa:
        ```
        doubled_no_shift = Znedi3(..., shifter=NoShift.from_kernel('lanczos')).scale(...)

        # which in *this case* can also be written as this
        doubled_no_shift = Znedi3(..., shifter=NoShift, scaler=Lanczos).scale(...)
        ```

        Or for some other code:
        ```
        @NoShift.from_kernel
        class CustomCatromWithoutShift(Catrom):
            # some cool code
            ...
        ```
        """

        kernel_t = Kernel.from_param(kernel)

        class inner_no_shift(NoShiftBase, kernel_t):  # type: ignore
            ...

        return inner_no_shift


class NoScaleBase(Scaler):
    @inject_self.cached
    def scale(  # type: ignore
        self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0), **kwargs: Any
    ) -> vs.VideoNode:
        try:
            return super().scale(clip, clip.width, clip.height, shift, **kwargs)  # type: ignore
        except Exception:
            return clip


class NoScale(NoScaleBase, Bicubic):  # type: ignore
    def __class_getitem__(cls, kernel: KernelT) -> type[Kernel]:
        return cls.from_kernel(kernel)

    @staticmethod
    def from_kernel(kernel: KernelT) -> type[Kernel]:
        kernel_t = Kernel.from_param(kernel)

        class inner_no_scale(kernel_t, NoScaleBase):  # type: ignore
            ...

        return inner_no_scale


excluded_kernels = [Kernel, FmtConv, Example, Impulse, Placebo, NoShiftBase, NoScaleBase]


@dataclass
class LinearLight:
    clip: vs.VideoNode

    linear: bool = True
    sigmoid: bool | tuple[float, float] = False

    kernel: KernelT = Catrom

    out_fmt: vs.VideoFormat | None = None

    @dataclass
    class LinearLightProcessing(cachedproperty.baseclass):
        ll: LinearLight

        @cachedproperty
        def linear(self) -> vs.VideoNode:
            wclip = self.ll._wclip

            if self.ll._wclip.format.color_family is vs.YUV:
                wclip = self.ll._kernel.resample(wclip, vs.RGBS, None, self.ll._matrix)

            if self.ll.linear:
                wclip = Point.scale_function(wclip, transfer_in=self.ll._curve, transfer=Transfer.LINEAR)

            if self.ll.sigmoid:
                wclip = wclip.std.Expr(
                    f'{self.ll._scenter} 1 x {self.ll._sscale} * {self.ll._soffset} + / '
                    f'1 - log {self.ll._sslope} / - 0 max 1 min'
                )

            return wclip

        @linear.setter
        def linear(self, processed: vs.VideoNode) -> vs.VideoNode:
            if self.ll._exited:
                raise CustomRuntimeError('You can\'t set .linear after going out of the context manager!')
            self._linear = processed

        @cachedproperty
        def out(self) -> vs.VideoNode:
            if not self.ll._exited:
                raise CustomRuntimeError('You can\'t get .out while still inside of the context manager!')

            if not hasattr(self, '_linear'):
                raise CustomValueError('You need to set .linear before getting .out!', self.__class__)

            processed = self._linear

            if self.ll.sigmoid:
                processed = processed.std.Expr(
                    f'1 1 {self.ll._sslope} {self.ll._scenter} x - * exp + / '
                    f'{self.ll._soffset} - {self.ll._sscale} / 0 max 1 min'
                )

            if self.ll.linear:
                processed = Point.scale_function(processed, transfer_in=Transfer.LINEAR, transfer=self.ll._curve)

            return resample_to(processed, self.ll._fmt, self.ll._matrix, self.ll._kernel)

    def __enter__(self) -> LinearLightProcessing:
        self.linear = self.linear or not not self.sigmoid

        if self.sigmoid:
            if self.sigmoid is True:
                self.sigmoid = (6.5, 0.75)

            self._sslope, self._scenter = self.sigmoid

            if 1.0 > self._sslope or self._sslope > 20.0:
                raise CustomValueError('sigmoid slope has to be in range 1.0-20.0 (inclusive).', self.__class__)

            if 0.0 > self._scenter or self._scenter > 1.0:
                raise CustomValueError('sigmoid center has to be in range 0.0-1.0 (inclusive).', self.__class__)

            self._soffset = 1.0 / (1 + exp(self._sslope * self._scenter))
            self._sscale = 1.0 / (1 + exp(self._sslope * (self._scenter - 1))) - self._soffset

        self._fmt = self.out_fmt or self.clip.format
        assert self._fmt

        self._wclip = depth(self.clip, 32) if self.sigmoid else self.clip
        self._curve = Transfer.from_video(self.clip)
        self._matrix = Matrix.from_transfer(self._curve)
        self._kernel = Catrom.from_param(self.kernel)

        self._exited = False

        return LinearLight.LinearLightProcessing(self)

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self._exited = True


def resample_to(
    clip: vs.VideoNode, out_fmt: HoldsVideoFormatT, matrix: MatrixT | None = None, kernel: KernelT = Catrom
) -> vs.VideoNode:
    out_fmt = get_video_format(out_fmt)
    assert clip.format

    kernel = Kernel.from_param(kernel)

    if out_fmt == clip.format:
        return clip

    if out_fmt.color_family is clip.format.color_family:
        return depth(clip, out_fmt)

    if out_fmt.subsampling_w == out_fmt.subsampling_h == 0:
        return Point.resample(clip, out_fmt, matrix)

    return kernel.resample(clip, out_fmt, matrix)
