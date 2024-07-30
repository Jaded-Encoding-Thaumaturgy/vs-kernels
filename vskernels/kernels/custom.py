from __future__ import annotations
from stgpytools import inject_self
from inspect import Signature

from vstools import vs, core
from typing import Any
from .abstract import Kernel

from typing import TypeVar


__all__ = [
    'CustomKernel'
]


class CustomKernel(Kernel):
    @inject_self
    def kernel(self: CustomKernelT, *, x: float) -> float:
        raise NotImplementedError

    def _modify_kernel_func(self, *, blur: float = 1.0, **kwargs: Any):
        support = self.kernel_radius * blur

        if blur != 1.0:
            def kernel(x: float) -> float:
                return self.kernel(x=x / blur)

            return kernel, support

        return self.kernel, support

    @inject_self
    def scale_function(self, clip: vs.VideoNode, width: int | None = None, height: int | None = None, *args: Any, **kwargs: Any) -> vs.VideoNode:
        clean_kwargs = {k: v for k, v in kwargs.items() if k not in Signature.from_callable(self._modify_kernel_func).parameters.keys()}
        return core.resize2.Custom(clip, *self._modify_kernel_func(**kwargs), width, height, *args, **clean_kwargs)

    resample_function = scale_function

    @inject_self
    def descale_function(self, clip: vs.VideoNode, width: int, height: int, *args: Any, **kwargs: Any) -> vs.VideoNode:
        clean_kwargs = {k: v for k, v in kwargs.items() if k not in Signature.from_callable(self._modify_kernel_func).parameters.keys()}
        return core.descale.Decustom(clip, width, height, *self._modify_kernel_func(**kwargs), *args, **clean_kwargs)

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        args = super().get_params_args(is_descale, clip, width, height, **kwargs)

        if not is_descale:
            for key in ('border_handling', 'ignore_mask', 'force', 'force_h', 'force_v'):
                args.pop(key, None)

        return args


CustomKernelT = TypeVar('CustomKernelT', bound=CustomKernel)
