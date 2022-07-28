from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Any, Callable, NamedTuple, Protocol, Sequence, Type, Union, NoReturn

import vapoursynth as vs

from .exceptions import ReservedMatrixError, UndefinedMatrixError, UnsupportedMatrixError

__all__ = [
    'VideoProp', 'VideoFormatT', 'VSFunction',
    'Matrix', 'MatrixT',
    'Transfer', 'TransferT',
    'Primaries', 'PrimariesT'
]

core = vs.core

VideoProp = Union[
    int, Sequence[int],
    float, Sequence[float],
    str, Sequence[str],
    vs.VideoNode, Sequence[vs.VideoNode],
    vs.VideoFrame, Sequence[vs.VideoFrame],
    Callable[..., Any], Sequence[Callable[..., Any]]
]
VideoFormatT = Union[int, vs.PresetFormat, vs.VideoFormat]


class VSFunction(Protocol):
    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        ...


if TYPE_CHECKING:
    class Matrix(vs.MatrixCoefficients):
        RGB = 0
        GBR = 0
        BT709 = 1
        UNKNOWN = 2
        FCC = 4
        BT470BG = 5
        SMPTE170M = 6
        SMPTE240M = 7
        YCGCO = 8
        BT2020NC = 9
        BT2020C = 10
        SMPTE2085 = 11
        CHROMA_DERIVED_NC = 12
        CHROMA_DERIVED_C = 13
        ICTCP = 14

        def __new__(cls: type[Matrix], value: int | Matrix | vs.MatrixCoefficients | None) -> Matrix:
            ...

        @classmethod
        def from_res(cls, frame: vs.VideoFrame | vs.VideoNode) -> Matrix:
            """Return matrix based on the frame dimensions."""
            ...

        @classmethod
        def from_video(cls, frame: vs.VideoNode | vs.VideoFrame, strict: bool = False) -> Matrix:
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
            ...
else:
    _MatrixYCGCOError = UnsupportedMatrixError(
        'Matrix: Matrix YCGCO is no longer supported by VapourSynth starting in R55 (APIv4).'
    )

    class Matrix(IntEnum):
        """Matrix coefficients (ITU-T H.265 Table E.5)."""

        _value_: int

        @classmethod
        def _missing_(cls: Type[Matrix], value: Any) -> Matrix | None:
            if value == 8:
                raise _MatrixYCGCOError

            if cls.RGB < value < cls.ICTCP:
                raise ReservedMatrixError(f'Matrix: this matrix ({value}) is reserved.')

            if value > cls.ICTCP:
                raise UnsupportedMatrixError(
                    f'Matrix: this matrix ({value}) is current unsupported. '
                    'If you believe this to be in error, please leave an issue '
                    'in the vs-kernels GitHub repository.'
                )

            if value is None:
                return Matrix.UNKNOWN

            return None

        RGB = 0
        GBR = 0
        BT709 = 1
        UNKNOWN = 2
        FCC = 4
        BT470BG = 5
        SMPTE170M = 6
        SMPTE240M = 7
        if core.version_number() < 55:
            YCGCO = 8
        else:
            @classmethod
            @property
            def YCGCO(cls) -> NoReturn:
                raise _MatrixYCGCOError
        BT2020NC = 9
        BT2020C = 10
        SMPTE2085 = 11
        CHROMA_DERIVED_NC = 12
        CHROMA_DERIVED_C = 13
        ICTCP = 14

        @classmethod
        def from_res(cls, frame: vs.VideoFrame | vs.VideoNode) -> Matrix:
            if isinstance(frame, vs.VideoNode) and not (
                frame.width and frame.height and frame.format
            ):
                frame = frame.get_frame(0)

            if frame.format.color_family == vs.RGB:
                return Matrix(0)

            w, h = frame.width, frame.height

            if w <= 1024 and h <= 576:
                return Matrix(6)

            if w <= 2048 and h <= 1536:
                return Matrix(1)

            return Matrix(9)

        @classmethod
        def from_video(cls, frame: vs.VideoNode | vs.VideoFrame, strict: bool = False) -> Matrix:
            from .util import get_prop

            if isinstance(frame, vs.VideoNode):
                frame = frame.get_frame(0)

            matrix = get_prop(frame, '_Matrix', int)

            if matrix == Matrix.UNKNOWN:
                if strict:
                    raise UndefinedMatrixError(f'Matrix.from_video: Matrix ({matrix}) is undefined.')
                return Matrix.from_res(frame)

            return Matrix(matrix)

if TYPE_CHECKING:
    class Transfer(vs.TransferCharacteristics):
        BT709 = 1
        UNKNOWN = 2
        BT470M = 4
        BT470BG = 5
        BT601 = 6
        ST240M = 7
        LINEAR = 8
        LOG_100 = 9
        LOG_316 = 10
        XVYCC = 11
        SRGB = 13
        BT2020_10bits = 14
        BT2020_12bits = 15
        ST2084 = 16
        ARIB_B67 = 18

        def __new__(cls: type[Transfer], value: int | Transfer | vs.TransferCharacteristics | None) -> Transfer:
            ...

        @classmethod
        def from_matrix(cls, matrix: Matrix) -> Transfer:
            ...
else:
    class Transfer(IntEnum):
        """Transfer characteristics (ITU-T H.265)."""

        _value_: int

        @classmethod
        def _missing_(cls: Type[Transfer], value: Any) -> Transfer | None:
            if cls.BT709 < value < cls.ARIB_B67:
                raise PermissionError('Transfer: This transfer is reserved!')

            if value is None:
                return Transfer.UNKNOWN

            return None

        BT709 = 1
        UNKNOWN = 2
        BT470M = 4
        BT470BG = 5
        BT601 = 6
        ST240M = 7
        LINEAR = 8
        LOG_100 = 9
        LOG_316 = 10
        XVYCC = 11
        SRGB = 13
        BT2020_10bits = 14
        BT2020_12bits = 15
        ST2084 = 16
        ARIB_B67 = 18

        @classmethod
        def from_matrix(cls, matrix: Matrix) -> Transfer:
            if matrix not in _matrix_transfer_map:
                raise KeyError(
                    'Transfer.from_matrix: matrix is not supported!'
                )

            return _matrix_transfer_map[matrix]

if TYPE_CHECKING:
    class Primaries(vs.ColorPrimaries):
        BT709 = 1
        UNKNOWN = 2
        BT470_M = 4
        BT470_BG = 5
        ST170_M = 6
        ST240_M = 7
        FILM = 8
        BT2020 = 9
        ST428 = 10
        ST431_2 = 11
        ST432_1 = 12
        EBU3213_E = 22

        def __new__(cls: type[Primaries], value: int | Primaries | vs.ColorPrimaries | None) -> Primaries:
            ...
else:
    class Primaries(IntEnum):
        """Color primaries (ITU-T H.265)."""

        _value_: int

        @classmethod
        def _missing_(cls: Type[Primaries], value: Any) -> Primaries | None:
            if cls.BT709 < value < cls.EBU3213E:
                raise PermissionError('Primaries: These primaries are reserved!')

            if value is None:
                return Primaries.UNKNOWN

            return None

        BT709 = 1
        UNKNOWN = 2
        BT470M = 4
        BT470BG = 5
        ST170M = 6
        ST240M = 7
        FILM = 8
        BT2020 = 9
        ST428 = 10
        ST431_2 = 11
        ST432_1 = 12
        EBU3213E = 22


class MatrixCoefficients(NamedTuple):
    k0: float
    phi: float
    alpha: float
    gamma: float

    @classmethod
    @property
    def SRGB(cls) -> MatrixCoefficients:
        return MatrixCoefficients(0.04045, 12.92, 0.055, 2.4)

    @classmethod
    @property
    def BT709(cls) -> MatrixCoefficients:
        return MatrixCoefficients(0.08145, 4.5, 0.0993, 2.22222)

    @classmethod
    @property
    def SMPTE240M(cls) -> MatrixCoefficients:
        return MatrixCoefficients(0.0912, 4.0, 0.1115, 2.22222)

    @classmethod
    @property
    def BT2020(cls) -> MatrixCoefficients:
        return MatrixCoefficients(0.08145, 4.5, 0.0993, 2.22222)

    @classmethod
    def from_curve(cls, curve: Transfer) -> MatrixCoefficients:
        if curve not in _transfer_matrix_map:
            raise KeyError(
                'MatrixCoefficients.from_curve: curve is not supported!'
            )

        return _transfer_matrix_map[curve]  # type: ignore


_matrix_transfer_map = {
    Matrix.RGB: Transfer.SRGB,
    Matrix.BT709: Transfer.BT709,
    Matrix.BT470BG: Transfer.BT601,
    Matrix.SMPTE170M: Transfer.BT601,
    Matrix.SMPTE240M: Transfer.ST240M,
    Matrix.CHROMA_DERIVED_C: Transfer.SRGB,
    Matrix.ICTCP: Transfer.BT2020_10bits,
}

_transfer_matrix_map = {
    Transfer.SRGB: MatrixCoefficients.SRGB,
    Transfer.BT709: MatrixCoefficients.BT709,
    Transfer.BT601: MatrixCoefficients.BT709,
    Transfer.ST240M: MatrixCoefficients.SMPTE240M,
    Transfer.BT2020_10bits: MatrixCoefficients.BT2020,
    Transfer.BT2020_12bits: MatrixCoefficients.BT2020
}

MatrixT = Union[int, vs.MatrixCoefficients, Matrix]
TransferT = Union[int, vs.TransferCharacteristics, Transfer]
PrimariesT = Union[int, vs.ColorPrimaries, Primaries]
