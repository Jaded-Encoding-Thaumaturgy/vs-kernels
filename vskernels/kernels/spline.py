from __future__ import annotations

from math import comb
from typing import Any

from vstools import inject_self

from .complex import CustomComplexTapsKernel
from .helpers import poly3

__all__ = [
    'Spline',
    'Spline16',
    'Spline36',
    'Spline64',
]


class Spline(CustomComplexTapsKernel):
    """Spline resizer."""

    def __init__(self, taps: float = 2, **kwargs: Any) -> None:
        super().__init__(taps, **kwargs)

        if hasattr(self, '_static_coeffs'):
            self._coefs = self._static_coeffs
        else:
            self._coefs = self._splineKernelCoeff()

    def _naturalCubicSpline(self, values: list[int]) -> list[float]:
        import numpy as np  # type: ignore

        n = len(values) - 1

        rhs = values[:-1] + values[1:] + [0] * (2 * n)

        eqns = []
        # left value = sample
        eqns += [[0] * (4 * i) + [i ** 3, i ** 2, i, 1] + [0] * (4 * (n - i - 1)) for i in range(n)]
        # right value = sample
        eqns += [[0] * (4 * i) + [(i + 1) ** 3, (i + 1) ** 2, i + 1, 1] + [0] * (4 * (n - i - 1)) for i in range(n)]
        # derivatives match
        eqns += [[0] * (4 * i) + [3 * (i + 1) ** 2, 2 * (i + 1), 1, 0] + [-3 * (i + 1) ** 2, -2 * (i + 1), -1, 0] + [0] * (4 * (n - i - 2)) for i in range(n - 1)]
        # second derivatives match
        eqns += [[0] * (4 * i) + [6 * (i + 1), 2, 0, 0] + [-6 * (i + 1), -2, 0, 0] + [0] * (4 * (n - i - 2)) for i in range(n - 1)]
        eqns += [[0, 2, 0, 0] + [0] * (4 * (n - 1))]
        eqns += [[0] * (4 * (n - 1)) + [6 * n ** 2, 2 * n, 0, 0]]

        assert (len(rhs) == len(eqns))

        return list(np.linalg.solve(np.array(eqns), np.array(rhs)))

    def _splineKernelCoeff(self) -> list[float]:
        taps = self.kernel_radius

        coeffs = list[float]([taps])

        def _shiftPolynomial(coeffs: list[float], shift: float) -> list[float]:
            return [
                sum(c * comb(k, m) * (-shift) ** max(0, k - m) for k, c in enumerate(coeffs[::-1])) for m in range(len(coeffs))
            ][::-1]

        for i in range(taps):
            samplept = taps - i - 1
            samples = [0] * samplept + [1] + [0] * (2 * taps - samplept - 1)

            assert len(samples) == 2 * taps

            coeffs += _shiftPolynomial(
                self._naturalCubicSpline(samples)[4 * taps - 4:4 * taps], -(taps - 1) + i
            )

        return coeffs

    @inject_self
    def kernel(self, x: float) -> float:  # type: ignore
        x, taps = abs(x), self.kernel_radius

        if x >= taps:
            return 0.0

        tap = int(x)

        coefs = [taps, *self._coefs]

        a, b, c, d = coefs[4 * tap + 1:4 * tap + 5]

        return poly3(x, d, c, b, a)


class NaturalSpline(Spline):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(self._static_kernel_radius, **kwargs)  # type: ignore


class Spline16(NaturalSpline):
    """Spline16 resizer."""

    _static_kernel_radius = 2

    _static_coeffs = [
        1.0, -9.0 / 5.0, -1.0 / 5.0, 1.0,
        -1.0 / 3.0, 4.0 / 5.0, -7.0 / 15.0, 0.0
    ]


class Spline36(NaturalSpline):
    """Spline36 resizer."""

    _static_kernel_radius = 3

    _static_coeffs = [
        13.0 / 11.0, -453.0 / 209.0, -3.0 / 209.0, 1.0,
        -6.0 / 11.0, 270.0 / 209.0, -156.0 / 209.0, 0.0,
        1.0 / 11.0, -45.0 / 209.0, 26.0 / 209.0, 0.0,
    ]


class Spline64(NaturalSpline):
    """Spline64 resizer."""

    _static_kernel_radius = 4

    _static_coeffs = [
        49.0 / 41.0, -6387.0 / 2911.0, -3.0 / 2911.0, 1.0,
        -24.0 / 41.0, 4032.0 / 2911.0, -2328.0 / 2911.0, 0.0,
        6.0 / 41.0, -1008.0 / 2911.0, 582.0 / 2911.0, 0.0,
        -1.0 / 41.0, 168.0 / 2911.0, -97.0 / 2911.0, 0.0
    ]
