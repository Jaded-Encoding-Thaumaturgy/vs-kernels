from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Any, Callable, NamedTuple, NoReturn, Protocol, Sequence, Type, TypeVar, Union

import vapoursynth as vs

from .exceptions import (
    ReservedMatrixError, ReservedPrimariesError, ReservedTransferError, UndefinedMatrixError, UnsupportedMatrixError,
    UnsupportedPrimariesError, UnsupportedTransferError
)

__all__ = [
    'VideoProp', 'HoldsPropValueT',
    'VideoFormatT', 'VSFunction', 'VNodeCallable',
    'Matrix', 'MatrixT',
    'Transfer', 'TransferT',
    'Primaries', 'PrimariesT',
    'MatrixCoefficients',
    'MISSING', 'MissingT'
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

HoldsPropValueT = Union[vs.FrameProps, vs.VideoFrame, vs.AudioFrame, vs.VideoNode, vs.AudioNode]

_MatrixYCGCOError = UnsupportedMatrixError(
    'Matrix: Matrix YCGCO is no longer supported by VapourSynth starting in R55 (APIv4).'
)


VNodeCallable = TypeVar('VNodeCallable', bound=Callable[..., vs.VideoNode])


class VSFunction(Protocol):
    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        ...


class MissingT:
    pass


MISSING = MissingT()

if TYPE_CHECKING:
    class _MatrixMeta(vs.MatrixCoefficients):
        def __new__(cls: type[Matrix], value: MatrixT) -> Matrix:  # type: ignore
            ...

    class _TransferMeta(vs.TransferCharacteristics):
        def __new__(cls: type[Transfer], value: TransferT) -> Transfer:  # type: ignore
            ...

    class _PrimariesMeta(vs.ColorPrimaries):
        def __new__(cls: type[Primaries], value: PrimariesT) -> Primaries:  # type: ignore
            ...
else:
    _MatrixMeta = _TransferMeta = _PrimariesMeta = IntEnum


class Matrix(_MatrixMeta):
    """Matrix coefficients (ITU-T H.265 Table E.5)."""

    _value_: int

    @classmethod
    def _missing_(cls: Type[Matrix], value: Any) -> Matrix | None:
        if value is None:
            return Matrix.UNKNOWN

        if value == 8:
            raise _MatrixYCGCOError

        if cls.RGB < value < cls.ICTCP:
            raise ReservedMatrixError(f'Matrix ({value}) is reserved.')

        if value > cls.ICTCP:
            raise UnsupportedMatrixError(
                f'Matrix ({value}) is current unsupported. '
                'If you believe this to be in error, please leave an issue '
                'in the vs-kernels GitHub repository.'
            )

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
        """Return matrix based on the frame dimensions."""
        if isinstance(frame, vs.VideoNode) and not (
            frame.width and frame.height and frame.format
        ):
            frame = frame.get_frame(0)

        assert frame.format

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
        from .util import get_prop

        if isinstance(frame, vs.VideoNode):
            frame = frame.get_frame(0)

        matrix = get_prop(frame, '_Matrix', int)

        if matrix == Matrix.UNKNOWN:
            if strict:
                raise UndefinedMatrixError(f'Matrix.from_video: Matrix ({matrix}) is undefined.')
            return Matrix.from_res(frame)

        return Matrix(matrix)


class Transfer(_TransferMeta):
    """Transfer characteristics (ITU-T H.265)."""

    _value_: int

    @classmethod
    def _missing_(cls: Type[Transfer], value: Any) -> Transfer | None:
        if value is None:
            return Transfer.UNKNOWN

        if cls.BT709 < value < cls.ARIB_B67:
            raise ReservedTransferError(f'Transfer ({value}) is reserved.')

        if value > cls.ARIB_B67:
            raise UnsupportedTransferError(
                f'Transfer ({value}) is current unsupported. '
                'If you believe this to be in error, please leave an issue '
                'in the vs-kernels GitHub repository.'
            )

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

    """
    Extra tranfer characterists from libplacebo
    https://github.com/haasn/libplacebo/blob/master/src/include/libplacebo/colorspace.h#L193
    """

    # Standard gamut:
    BT601_525 = 100
    BT601_625 = 101
    EBU_3213 = 102
    # Wide gamut:
    APPLE = 103
    ADOBE = 104
    PRO_PHOTO = 105
    CIE_1931 = 106
    DCI_P3 = 107
    DISPLAY_P3 = 108
    V_GAMUT = 109
    S_GAMUT = 110
    FILM_C = 111
    COUNT = 112

    @classmethod
    def from_matrix(cls, matrix: Matrix) -> Transfer:
        if matrix not in _matrix_transfer_map:
            raise KeyError(
                'Transfer.from_matrix: matrix is not supported!'
            )

        return _matrix_transfer_map[matrix]

    def as_libplacebo(self) -> int:
        return _transfer_placebo_map[self]

    @classmethod
    def from_libplacebo(self, val: int) -> int:
        return _placebo_transfer_map[val]


class Primaries(_PrimariesMeta):
    """Color primaries (ITU-T H.265)."""

    _value_: int

    @classmethod
    def _missing_(cls: Type[Primaries], value: Any) -> Primaries | None:
        if value is None:
            return Primaries.UNKNOWN

        if cls.BT709 < value < cls.EBU3213E:
            raise ReservedPrimariesError(f'Primaries ({value}) is reserved.')

        if value > cls.EBU3213E:
            raise UnsupportedPrimariesError(
                f'Primaries ({value}) is current unsupported. '
                'If you believe this to be in error, please leave an issue '
                'in the vs-kernels GitHub repository.'
            )

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

_transfer_placebo_map = {
    Transfer.UNKNOWN: 0,
    Transfer.BT601_525: 1,
    Transfer.BT601_625: 2,
    Transfer.BT709: 3,
    Transfer.BT470M: 4,
    Transfer.EBU_3213: 5,
    Transfer.BT2020_10bits: 6,
    Transfer.BT2020_12bits: 6,
    Transfer.APPLE: 7,
    Transfer.ADOBE: 8,
    Transfer.PRO_PHOTO: 9,
    Transfer.CIE_1931: 10,
    Transfer.DCI_P3: 11,
    Transfer.DISPLAY_P3: 12,
    Transfer.V_GAMUT: 13,
    Transfer.S_GAMUT: 14,
    Transfer.FILM_C: 15,
    Transfer.COUNT: 16
}

_placebo_transfer_map = {
    value: key for key, value in _transfer_placebo_map.items()
}

MatrixT = Union[int, vs.MatrixCoefficients, Matrix]
TransferT = Union[int, vs.TransferCharacteristics, Transfer]
PrimariesT = Union[int, vs.ColorPrimaries, Primaries]
