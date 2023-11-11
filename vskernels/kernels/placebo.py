from __future__ import annotations

from math import ceil
from typing import TYPE_CHECKING, Any

from vstools import Transfer, TransferT, core, inject_self, vs

from .complex import LinearScaler

__all__ = [
    'Placebo'
]


class Placebo(LinearScaler):
    _kernel: str
    """Name of the placebo kernel"""

    # Kernel settings
    taps: float | None
    b: float | None
    c: float | None

    # Filter settings
    clamp: float
    blur: float
    taper: float

    # Quality settings
    antiring: float
    cutoff: float

    # Other settings
    lut_entries: int = 64

    scale_function = core.lazy.placebo.Resample

    def __init__(
        self,
        taps: float | None = None, b: float | None = None, c: float | None = None,
        clamp: float = 0.0, blur: float = 0.0, taper: float = 0.0,
        antiring: float = 0.0, cutoff: float = 0.001,
        **kwargs: Any
    ) -> None:
        self.taps = taps
        self.b = b
        self.c = c
        self.clamp = clamp
        self.blur = blur
        self.taper = taper
        self.antiring = antiring
        self.cutoff = cutoff
        super().__init__(**kwargs)

    if TYPE_CHECKING:
        @inject_self.cached
        def scale(  # type: ignore[override]
            self, clip: vs.VideoNode, width: int, height: int, shift: tuple[float, float] = (0, 0),
            *, linear: bool = True, sigmoid: bool | tuple[float, float] = True, curve: TransferT | None = None,
            **kwargs: Any
        ) -> vs.VideoNode:
            ...
    else:
        ...

    def get_scale_args(
        self, clip: vs.VideoNode, shift: tuple[float, float] = (0, 0),
        width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        return dict(sx=shift[1], sy=shift[0]) | self.kwargs | self.get_params_args(
            False, clip, width, height, **kwargs
        )

    def get_params_args(
        self, is_descale: bool, clip: vs.VideoNode, width: int | None = None, height: int | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        curve = Transfer.from_param_or_video(kwargs.get('curve', Transfer.BT709), clip)

        return dict(
            width=width, height=height, filter=self._kernel,
            radius=self.taps, param1=self.b, param2=self.c,
            clamp=self.clamp, taper=self.taper, blur=self.blur,
            antiring=self.antiring, cutoff=self.cutoff,
            lut_entries=self.lut_entries, trc=curve.value_libplacebo
        )

    def _kernel_size(self, taps: float | None = None, b: int | None = None, c: int | None = None) -> int
        if taps:
            return ceil(self.taps)

        if b or c:
            return 1 + ((b if b and b != 0 else 0, c if c and c != 0 else 0.5) != (0, 0))

        return 1

    @property
    def kernel_size(self) -> int:
        return self._kernel_size(self.taps, self.b, self.c)
