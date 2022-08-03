from __future__ import annotations

from functools import lru_cache
from typing import Any, Generator, List, Type, TypeVar, overload

import vapoursynth as vs

from .exceptions import UnknownKernelError, VideoPropError
from .kernels import FmtConv, Kernel, Placebo
from .kernels.docs import Example
from .kernels.impulse import Impulse
from .types import MISSING, HoldsPropValueT, Matrix, MissingT, VideoProp

__all__: List[str] = [
    'get_matrix_from_res', 'get_prop',
    'get_all_kernels', 'get_kernel',
    'get_matrix', 'Matrix'
]

core = vs.core


T = TypeVar('T', bound=VideoProp)
DT = TypeVar('DT')
CT = TypeVar('CT')


def get_matrix_from_res(frame: vs.VideoFrame | vs.VideoNode) -> Matrix:
    """Return matrix based on the frame dimensions."""
    print(DeprecationWarning('get_matrix_from_res: deprecated in favor of Matrix.from_res!'))

    return Matrix.from_res(frame)


@overload
def get_prop(obj: HoldsPropValueT, key: str, t: Type[T], cast: None = None, default: MissingT = MISSING) -> T:
    ...


@overload
def get_prop(obj: HoldsPropValueT, key: str, t: Type[T], cast: Type[CT], default: MissingT = MISSING) -> CT:
    ...


@overload
def get_prop(obj: HoldsPropValueT, key: str, t: Type[T], cast: None, default: DT) -> T | DT:
    ...


@overload
def get_prop(obj: HoldsPropValueT, key: str, t: Type[T], cast: Type[CT], default: DT) -> CT | DT:
    ...


def get_prop(
    obj: HoldsPropValueT, key: str, t: Type[T], cast: Type[CT] | None = None, default: DT | MissingT = MISSING
) -> T | CT | DT:
    """
    Get FrameProp ``prop`` from frame ``frame`` with expected type ``t`` to satisfy the type checker.

    :param frame:               Frame containing props.
    :param key:                 Prop to get.
    :param t:                   Type of prop.
    :param cast:                Cast value to this type, if specified.
    :param default:             Fallback value.

    :return:                    frame.prop[key].

    :raises VideoPropError:     ``key`` is not found in props.
    :raises VideoPropError:     Returns a prop of the wrong type.
    """

    if isinstance(obj, (vs.VideoNode, vs.AudioNode)):
        props = obj.get_frame(0).props
    elif isinstance(obj, (vs.VideoFrame, vs.AudioFrame)):
        props = obj.props
    else:
        props = obj

    prop: Any = MISSING

    try:
        prop = props[key]

        if not isinstance(prop, t):
            raise TypeError

        if cast is None:
            return prop

        return cast(prop)  # type: ignore
    except BaseException as e:
        if not isinstance(default, MissingT):
            return default

        if isinstance(e, KeyError) or prop is MISSING:
            raise VideoPropError(f"get_prop: 'Key {key} not present in props!'")
        elif isinstance(e, TypeError):
            raise VideoPropError(
                f"get_prop: 'Key {key} did not contain expected type: Expected {t} got {type(prop)}!'"
            )

        raise e


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

    print(DeprecationWarning('get_matrix: deprecated in favor of Matrix.from_video!'))

    return Matrix.from_video(frame, strict)
