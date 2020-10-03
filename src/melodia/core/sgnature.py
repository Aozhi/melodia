from typing import Tuple


class Signature:
    __slots__ = ('_nominator', '_denominator')

    def __init__(self, nominator: int, denominator: int):
        if not (nominator > 0 and denominator > 0 and (denominator & (denominator - 1) == 0)):
            raise ValueError(
                'Invalid time signature '
                '(both components must be positive and the second one must be a power of two)'
            )

        self._nominator = nominator
        self._denominator = denominator

    @property
    def nominator(self) -> int:
        return self._nominator

    @property
    def denominator(self) -> int:
        return self._denominator

    def to(self, denominator: int) -> 'Signature':
        if not (denominator > 0 and (denominator & (denominator - 1) == 0)):
            raise ValueError('Invalid denominator (must be a positive power of two)')

        if denominator == self._denominator:
            return Signature(self._nominator, self._denominator)

        if denominator > self._denominator:
            nominator = denominator // self._denominator * self._nominator
            return Signature(nominator, denominator)

        raise ValueError(f'New denominator must be >= {self._denominator}')

    def _to_common_denominator(self, other: 'Signature') -> Tuple[int, int, int]:
        n1, d1 = self._nominator, self._denominator
        n2, d2 = other._nominator, other._denominator

        if d1 == d2:
            return n1, n2, d1

        if d1 > d2:
            return n1, d1 // d2 * n2, d1

        return n2, d2 // d1 * n1, d2

    def __str__(self) -> str:
        return f'{self._nominator}/{self._denominator}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._nominator}, {self._denominator})'

    def __eq__(self, other: 'Signature') -> bool:
        n1, n2, _ = self._to_common_denominator(other)
        return n1 == n2

    def __le__(self, other: 'Signature') -> bool:
        n1, n2, _ = self._to_common_denominator(other)
        return n1 <= n2

    def __lt__(self, other: 'Signature') -> bool:
        n1, n2, _ = self._to_common_denominator(other)
        return n1 < n2

    def __ge__(self, other: 'Signature') -> bool:
        n1, n2, _ = self._to_common_denominator(other)
        return n1 >= n2

    def __gt__(self, other: 'Signature') -> bool:
        n1, n2, _ = self._to_common_denominator(other)
        return n1 > n2

    def __add__(self, other: 'Signature') -> 'Signature':
        n1, n2, d = self._to_common_denominator(other)
        return Signature(n1 + n2, d)

    def __mul__(self, other: 'Signature') -> 'Signature':
        n1, n2, d = self._to_common_denominator(other)
        return Signature(n1 * n2, d)

    def __abs__(self) -> 'Signature':
        return Signature(abs(self._nominator), self._denominator)
