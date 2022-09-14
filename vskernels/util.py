from __future__ import annotations

from functools import lru_cache
from typing import Generator, List, Type

import vapoursynth as vs

from .exceptions import UnknownKernelError
from .kernels import FmtConv, Kernel, Placebo
from .kernels.docs import Example
from .kernels.impulse import Impulse

__all__: List[str] = [
    'get_all_kernels', 'get_kernel'
]

core = vs.core


excluded_kernels = [Kernel, FmtConv, Example, Impulse, Placebo]


@lru_cache
def get_all_kernels(family: Type[Kernel] = Kernel) -> List[Type[Kernel]]:
    """Get all kernels as a list."""
    def _subclasses(cls: Type[Kernel]) -> Generator[Type[Kernel], None, None]:
        for subclass in cls.__subclasses__():
            yield from _subclasses(subclass)
            if subclass in excluded_kernels:
                continue
            yield subclass

    return list(set(_subclasses(family)))


@lru_cache
def get_kernel(kernel_name: str | type[Kernel] | Kernel) -> Type[Kernel]:
    """
    Get a kernel by name.

    :param name:    Kernel name.

    :return:        Kernel class.

    :raise UnknownKernelError:  Some kind of unknown error occured.
    """
    if isinstance(kernel_name, str):
        all_kernels = get_all_kernels()
        search_str = kernel_name.lower().strip()

        for kernel in all_kernels:
            if kernel.__name__.lower() == search_str:
                return kernel

        raise UnknownKernelError(f"get_kernel: 'Unknown kernel: {kernel_name}!'")
    elif isinstance(kernel_name, Kernel):
        return kernel_name.__class__

    return kernel_name
