from __future__ import annotations
from stgpytools import CustomValueError, KwargsT, inject_self
from inspect import Signature

from vstools import GenericVSFunction, vs, core
from typing import Any, Protocol, override
from .abstract import Kernel

from typing import TypeVar


__all__ = [
    'CustomKernel'
]


class _kernel_func(Protocol):
    def __call__(self, *, x: float) -> float:
        ...


class CustomKernel(Kernel):
    _no_blur_scale_function: GenericVSFunction | None = None
    """
    Optional scale function that will be used when scaling without blur. This is
    useful for cases where this function is more performant than the custom
    kernel.
    """

    def kernel(self, *, x: float) -> float:
        raise NotImplementedError

    def _modify_kernel_func(self, kwargs: KwargsT) -> tuple[_kernel_func, float]:
        blur = float(kwargs.pop('blur', 1.0))
        taps = int(kwargs.pop('taps', self.kernel_radius))
        support = taps * blur

        if blur != 1.0:
            def kernel(*, x: float) -> float:
                return self.kernel(x=x / blur)

            return kernel, support

        return self.kernel, support

    @inject_self
    @override
    def scale_function(  # type: ignore[override]
        self, clip: vs.VideoNode, width: int | None = None, height: int | None = None, *args: Any, **kwargs: Any
    ) -> vs.VideoNode:
        # If a no-blur scale function is defined and the default blur is being
        # used, then remove the parameter and use the given scale function.
        if self._no_blur_scale_function and kwargs.get("blur", 1.0) == 1.0:
            kwargs.pop("blur", None)
            return self._no_blur_scale_function(clip, width, height, *args, **kwargs)

        # Otherwise, fall back to the slower custom kernel implementation.

        kernel, support = self._modify_kernel_func(kwargs)

        clean_kwargs = {
            k: v for k, v in kwargs.items()
            if k not in Signature.from_callable(self._modify_kernel_func).parameters.keys()
            # Remove params that won't be recognized by `resize2.Custom`.
            and k not in ('filter_param_a', 'filter_param_b')
        }

        return core.resize2.Custom(clip, kernel, int(support), width, height, *args, **clean_kwargs)

    resample_function = scale_function

    @inject_self
    def descale_function(  # type: ignore[override]
        self, clip: vs.VideoNode, width: int, height: int, *args: Any, **kwargs: Any
    ) -> vs.VideoNode:
        kernel, support = self._modify_kernel_func(kwargs)

        clean_kwargs = {
            k: v for k, v in kwargs.items()
            if k not in Signature.from_callable(self._modify_kernel_func).parameters.keys()
        }

        try:
            return core.descale.Decustom(clip, width, height, kernel, int(support), *args, **clean_kwargs)
        except vs.Error as e:
            if 'Output dimension must be' in str(e):
                raise CustomValueError(
                    f'Output dimension ({width}x{height}) must be less than or equal to '
                    f'input dimension ({clip.width}x{clip.height}).', self.__class__
                )

            raise CustomValueError(e, self.__class__)

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        args = super().get_params_args(is_descale, clip, width, height, **kwargs)

        if not is_descale:
            for key in ('border_handling', 'ignore_mask'):
                args.pop(key, None)

        return args


CustomKernelT = TypeVar('CustomKernelT', bound=CustomKernel)
