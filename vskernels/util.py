from __future__ import annotations

from typing import List

import vapoursynth as vs

from .exceptions import ReservedMatrixError, UndefinedMatrixError, UnsupportedMatrixError
from .helpers import _get_matrix_from_res, _get_prop
from .types import Matrix

core = vs.core

__all__: List[str] = [
    'get_matrix'
]


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

    matrix = _get_prop(frame, "_Matrix", int)

    if matrix == 2 and strict:
        raise UndefinedMatrixError(f"get_matrix: 'Matrix ({matrix}) is undefined.'")
    elif matrix == 2:
        return _get_matrix_from_res(frame)
    elif matrix == 3:
        raise ReservedMatrixError(f"get_matrix: 'Matrix ({matrix}) is reserved.'")
    elif matrix == 8 and core.version_number() >= 55:
        raise UnsupportedMatrixError(f"get_matrix: 'Matrix {matrix} is no longer supported by VapourSynth.'")
    elif matrix > 14:
        raise UnsupportedMatrixError(f"get_matrix: 'Matrix ({matrix}) is current unsupported. "
                                     "If you believe this to be in error, please leave an issue "
                                     "in the vs-kernels GitHub repository.'")
    return Matrix(matrix)
