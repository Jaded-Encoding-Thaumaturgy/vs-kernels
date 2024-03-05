from math import floor, pi, sin

__all__ = [
    'sinc', 'poly3', 'round_halfup', 'bic_vals'
]


class bic_vals:
    @staticmethod
    def p0(b: float, c: float) -> float:
        return (6.0 - 2.0 * b) / 6.0

    @staticmethod
    def p2(b: float, c: float) -> float:
        return (-18.0 + 12.0 * b + 6.0 * c) / 6.0

    @staticmethod
    def p3(b: float, c: float) -> float:
        return (12.0 - 9.0 * b - 6.0 * c) / 6.0

    @staticmethod
    def q0(b: float, c: float) -> float:
        return (8.0 * b + 24.0 * c) / 6.0

    @staticmethod
    def q1(b: float, c: float) -> float:
        return (-12.0 * b - 48.0 * c) / 6.0

    @staticmethod
    def q2(b: float, c: float) -> float:
        return (6.0 * b + 30.0 * c) / 6.0

    @staticmethod
    def q3(b: float, c: float) -> float:
        return (-b - 6.0 * c) / 6.0


def sinc(x: float) -> float:
    return 1.0 if x == 0.0 else sin(x * pi) / (x * pi)


def poly3(x: float, c0: float, c1: float, c2: float, c3: float) -> float:
    return c0 + x * (c1 + x * (c2 + x * c3))


def round_halfup(x: float) -> float:
    return floor(x + 0.5) if x < 0 else floor(x + 0.49999999999999994)
