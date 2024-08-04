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

        coeffs = list[float]()

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

    @inject_self.cached
    def kernel(self, x: float) -> float:  # type: ignore
        x, taps = abs(x), self.kernel_radius

        if x >= taps:
            return 0.0

        tap = int(x)

        a, b, c, d = self._coefs[4 * tap:4 * tap + 4]

        return poly3(x, d, c, b, a)


class NaturalSpline(Spline):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(self._static_kernel_radius, **kwargs)  # type: ignore


class Spline16(NaturalSpline):
    """Spline16 resizer."""

    _static_kernel_radius = 2

    _static_coeffs = [
        0.9999999999999988, -1.799999999999999, -0.1999999999999993, 1.0000000000000004,
        -0.333333333333333, 1.7999999999999985, -3.066666666666665, 1.5999999999999994
    ]


class Spline36(NaturalSpline):
    """Spline36 resizer."""

    _static_kernel_radius = 3

    _static_coeffs = [
        1.1818181818181834, -2.1674641148325353, -0.014354066985642788, 1.0,
        -0.5454545454545451, 2.928229665071767, -4.9665071770334865, 2.583732057416266,
        0.09090909090909075, -0.760765550239233, 2.0765550239234405, -1.837320574162675
    ]


class Spline64(NaturalSpline):
    """Spline64 resizer."""

    _static_kernel_radius = 4

    _static_coeffs = [
        1.195121951219515, -2.1940913775334927, -0.0010305736860232173, 0.9999999999999929,
        -0.5853658536585364, 3.141188594984538, -5.326004809343863, 2.7701820680178617,
        0.1463414634146341, -1.2243215389900368, 3.3411198900721373, -2.9556853315011997,
        -0.02439024390243902, 0.27722432153898985, -1.0381312263826854, 1.277911370663001
    ]
