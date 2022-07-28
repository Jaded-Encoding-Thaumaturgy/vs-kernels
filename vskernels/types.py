from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Any, Callable, Protocol, Sequence, Type, Union

import vapoursynth as vs

__all__ = [
    'VideoProp', 'VideoFormatT', 'VSFunction',
    'Matrix', 'MatrixT',
    'Transfer', 'TransferT',
    'Primaries', 'PrimariesT'
]

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
else:
    class Matrix(IntEnum):
        """Matrix coefficients (ITU-T H.265 Table E.5)."""

        _value_: int

        @classmethod
        def _missing_(cls: Type[Matrix], value: Any) -> Matrix | None:
            if cls.RGB < value < cls.ICTCP:
                raise PermissionError('Matrix: This matrix is reserved!')

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
        YCGCO = 8
        BT2020NC = 9
        BT2020C = 10
        SMPTE2085 = 11
        CHROMA_DERIVED_NC = 12
        CHROMA_DERIVED_C = 13
        ICTCP = 14

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

MatrixT = Union[int, vs.MatrixCoefficients, Matrix]
TransferT = Union[int, vs.TransferCharacteristics, Transfer]
PrimariesT = Union[int, vs.ColorPrimaries, Primaries]


_matrix_transfer_map = {
    Matrix.BT709: Transfer.BT709,
    Matrix.BT470BG: Transfer.BT601,
    Matrix.SMPTE170M: Transfer.BT601,
    Matrix.SMPTE240M: Transfer.ST240M,
    Matrix.CHROMA_DERIVED_C: Transfer.SRGB,
    Matrix.ICTCP: Transfer.BT2020_10bits,
}
