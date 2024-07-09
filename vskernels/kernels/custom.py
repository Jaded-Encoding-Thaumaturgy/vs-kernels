from __future__ import annotations
from stgpytools import inject_self

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

    def scale_function(self, clip: vs.VideoNode, width: int, height: int, *args: Any, blur: float = 1.0, **kwargs: Any) -> vs.VideoNode:
        return core.resize2.Custom(clip, self.kernel, self.kernel_radius, width, height, *args, **kwargs)

    resample_function = scale_function

    def descale_function(self, clip: vs.VideoNode, width: int, height: int, *args: Any, **kwargs: Any) -> vs.VideoNode:
        return core.descale.Decustom(clip, width, height, self.kernel, self.kernel_radius, *args, **kwargs)

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        args = super().get_params_args(is_descale, clip, width, height, **kwargs)

        if not is_descale:
            for key in ('border_handling', 'ignore_mask', 'force', 'force_h', 'force_v'):
                args.pop(key, None)

        return args


CustomKernelT = TypeVar('CustomKernelT', bound=CustomKernel)
