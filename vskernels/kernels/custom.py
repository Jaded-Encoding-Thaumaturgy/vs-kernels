from __future__ import annotations
from stgpytools import KwargsT, inject_self
from inspect import Signature

from vstools import vs, core
from typing import Any
from .abstract import Kernel

from typing import TypeVar


__all__ = [
    'CustomKernel'
]


class CustomKernel(Kernel):
    @inject_self.cached
    def kernel(self: CustomKernelT, *, x: float) -> float:
        raise NotImplementedError

    def _modify_kernel_func(self, kwargs: KwargsT):
        blur = float(kwargs.pop('blur', 1.0))
        taps = int(kwargs.pop('taps', self.kernel_radius))
        support = taps * blur

        if blur != 1.0:
            def kernel(x: float) -> float:
                return self.kernel(x=x / blur)

            return kernel, support

        return self.kernel, support

    @inject_self
    def scale_function(
        self, clip: vs.VideoNode, width: int | None = None, height: int | None = None, *args: Any, **kwargs: Any
    ) -> vs.VideoNode:
        custom_kernel_vars = self._modify_kernel_func(kwargs)

        clean_kwargs = {
            k: v for k, v in kwargs.items()
            if k not in Signature.from_callable(self._modify_kernel_func).parameters.keys()
        }

        return core.resize2.Custom(clip, *custom_kernel_vars, width, height, *args, **clean_kwargs)

    resample_function = scale_function

    @inject_self
    def descale_function(
        self, clip: vs.VideoNode, width: int, height: int, *args: Any, **kwargs: Any
    ) -> vs.VideoNode:
        custom_kernel_vars = self._modify_kernel_func(kwargs)

        clean_kwargs = {
            k: v for k, v in kwargs.items()
            if k not in Signature.from_callable(self._modify_kernel_func).parameters.keys()
        }

        return core.descale.Decustom(clip, width, height, *custom_kernel_vars, *args, **clean_kwargs)

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        args = super().get_params_args(is_descale, clip, width, height, **kwargs)

        if not is_descale:
            for key in ('border_handling', 'ignore_mask'):
                args.pop(key, None)

        return args


CustomKernelT = TypeVar('CustomKernelT', bound=CustomKernel)
