from __future__ import annotations

from functools import lru_cache
from typing import Any, Callable, Generator, List, Sequence, Type, TypeVar, Union

import vapoursynth as vs

from .exceptions import UnknownKernelError, VideoPropError
from .kernels import Kernel, fmtconv
from .kernels.docs import Example
from .types import Matrix

__all__: List[str] = []

VideoProp = Union[
    int, Sequence[int],
    float, Sequence[float],
    str, Sequence[str],
    vs.VideoNode, Sequence[vs.VideoNode],
    vs.VideoFrame, Sequence[vs.VideoFrame],
    Callable[..., Any], Sequence[Callable[..., Any]]
]

T = TypeVar("T", bound=VideoProp)


def _get_matrix_from_res(frame: vs.VideoFrame | vs.VideoNode) -> Matrix:
    """Return matrix based on the frame dimensions."""
    if isinstance(frame, vs.VideoNode):
        frame = frame.get_frame(0)

    w, h = frame.width, frame.height

    if frame.format.color_family == vs.RGB:
        return Matrix(0)
    elif w <= 1024 and h <= 576:
        return Matrix(6)
    elif w <= 2048 and h <= 1536:
        return Matrix(1)
    return Matrix(9)


def _get_prop(frame: vs.VideoFrame, key: str, t: Type[T]) -> T:
    """
    Get FrameProp ``prop`` from frame ``frame`` with expected type ``t`` to satisfy the type checker.

    Taken from `lvsfunc`.

    :param frame:               Frame containing props.
    :param key:                 Prop to get.
    :param t:                   Type of prop.

    :return:                    frame.prop[key].

    :raises VideoPropError:     ``key`` is not found in props.
    :raises VideoPropError:     Returns a prop of the wrong type.
    """
    try:
        prop = frame.props[key]
    except KeyError:
        raise VideoPropError(f"get_prop: 'Key {key} not present in props!'")

    if not isinstance(prop, t):
        raise VideoPropError(f"get_prop: 'Key {key} did not contain expected type: "
                             f"Expected {t} got {type(prop)}!'")

    return prop


excluded_kernels = [Kernel, fmtconv, Example]


@lru_cache
def get_all_kernels() -> List[Type[Kernel]]:
    """Get all kernels as a list."""
    def _subclasses(cls: Type[Kernel]) -> Generator[Type[Kernel], None, None]:
        for subclass in cls.__subclasses__():
            yield from _subclasses(subclass)
            if subclass in excluded_kernels:
                continue
            yield subclass

    return list(set(_subclasses(Kernel)))


@lru_cache
def get_kernel(name: str) -> Type[Kernel]:
    """
    Get a kernel by name.

    :param name:    Kernel name.

    :return:        Kernel class.

    :raise UnknownKernelError:  Some kind of unknown error occured.
    """
    all_kernels = get_all_kernels()
    search_str = name.lower().strip()

    for kernel in all_kernels:
        if kernel.__name__.lower() == search_str:
            return kernel

    raise UnknownKernelError(f"get_kernel: 'Unknown kernel: {name}!'")
