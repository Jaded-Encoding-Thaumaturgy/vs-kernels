from __future__ import annotations

from functools import lru_cache
from typing import Generator, List, Type, TypeVar

import vapoursynth as vs

from .exceptions import (
    ReservedMatrixError, UndefinedMatrixError, UnknownKernelError, UnsupportedMatrixError, VideoPropError
)
from .kernels import Kernel, fmtconv
from .kernels.docs import Example
from .types import Matrix, VideoProp

__all__: List[str] = [
    'get_matrix_from_res', 'get_prop',
    'get_all_kernels', 'get_kernel',
    'get_matrix', 'Matrix'
]

core = vs.core


T = TypeVar("T", bound=VideoProp)


def get_matrix_from_res(frame: vs.VideoFrame | vs.VideoNode) -> Matrix:
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


def get_prop(frame: vs.VideoFrame, key: str, t: Type[T]) -> T:
    """
    Get FrameProp ``prop`` from frame ``frame`` with expected type ``t`` to satisfy the type checker.

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
        raise VideoPropError(f"get_prop: 'Key {key} did not contain expected type: Expected {t} got {type(prop)}!'")

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


def get_matrix(frame: vs.VideoNode | vs.VideoFrame, strict: bool = False) -> Matrix:
    """
    Get the matrix of a clip or VideoFrame.

    By default this function will first check the `_Matrix` prop for a valid matrix.
    If the matrix is not set, it will guess based on the resolution.

    If you want it to be strict and raise an error if no matrix is set, set ``strict=True``.

    :param clip:                        Clip or VideoFrame to process.
    :param strict:                      Whether to be strict about the matrix.
                                        If ``True``, checks just the `_Matrix` prop.
                                        If ``False``, will check the `_Matrix` prop
                                        and make a guess if `_Matrix=Matrix.UNKNOWN`.
                                        Default: False.

    :return:                            Value representing a matrix.

    :raise UndefinedMatrixError:        This matrix was undefined and strict was enabled.
    :raise ReservedMatrixError:         This matrix is reserved.
    :raise UnsupportedMatrixError:      VapourSynth no longer supports this matrix.
    :raise UnsupportedMatrixError:      This matrix is unsupported.
    """
    if isinstance(frame, vs.VideoNode):
        frame = frame.get_frame(0)

    matrix = get_prop(frame, "_Matrix", int)

    if matrix == 2 and strict:
        raise UndefinedMatrixError(f"get_matrix: 'Matrix ({matrix}) is undefined.'")
    elif matrix == 2:
        return get_matrix_from_res(frame)
    elif matrix == 3:
        raise ReservedMatrixError(f"get_matrix: 'Matrix ({matrix}) is reserved.'")
    elif matrix == 8 and core.version_number() >= 55:
        raise UnsupportedMatrixError(f"get_matrix: 'Matrix {matrix} is no longer supported by VapourSynth.'")
    elif matrix > 14:
        raise UnsupportedMatrixError(f"get_matrix: 'Matrix ({matrix}) is current unsupported. "
                                     "If you believe this to be in error, please leave an issue "
                                     "in the vs-kernels GitHub repository.'")
    return Matrix(matrix)
