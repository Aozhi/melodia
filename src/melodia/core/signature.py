from typing import Tuple


class Signature:
    """
    Signature represents time signature which can be used as time signature or as duration.
    """
    __slots__ = ('_nominator', '_denominator')

    def __init__(self, nominator: int, denominator: int):
        """
        Initializes Signature object. Nominator (first argument) must be non-negative.
        Denominator (second argument) should be a positive power of two.

        >>> Signature(0, 1)
        Signature(0, 1)

        >>> Signature(1, 4)
        Signature(1, 4)

        >>> Signature(3, 8)
        Signature(3, 8)

        :param nominator: signature nominator
        :param denominator: signature denominator
        """
        if not (nominator >= 0 and denominator > 0 and (denominator & (denominator - 1) == 0)):
            raise ValueError(
                'Invalid time signature '
                '(the nominator must be non-negative and the denominator must be a positive power of two)'
            )

        self._nominator = nominator
        self._denominator = denominator

    @property
    def nominator(self) -> int:
        """
        Returns the nominator of the signature.

        :return: nominator of the signature
        """
        return self._nominator

    @property
    def denominator(self) -> int:
        """
        Returns the denominator of the signature.

        :return: denominator of the signature
        """
        return self._denominator

    def to(self, denominator: int) -> 'Signature':
        """
        Returns new signature with required denominator and nominator scaled accordingly.
        New denominator must be greater or equal to the current one.

        >>> Signature(1, 2).to(4)
        Signature(2, 4)

        >>> Signature(0, 1).to(8)
        Signature(0, 8)

        >>> Signature(1, 1).to(8)
        Signature(8, 8)

        :param denominator: required new denominator
        :return: new signature with required denominator and nominator scaled accordingly
        """
        if not (denominator > 0 and (denominator & (denominator - 1) == 0)):
            raise ValueError('Invalid denominator (must be a positive power of two)')

        if denominator == self._denominator:
            return Signature(self._nominator, self._denominator)

        if denominator > self._denominator:
            nominator = denominator // self._denominator * self._nominator
            return Signature(nominator, denominator)

        raise ValueError(f'New denominator must be >= {self._denominator}')

    def normalized(self) -> 'Signature':
        """
        Returns normalized copy of this signature Signature is normalized when
        nominator and denominator does not have common divisors.

        >>> Signature(1, 4).normalized()
        Signature(1, 4)

        >>> Signature(2, 4).normalized()
        Signature(1, 2)

        >>> Signature(16, 4).normalized()
        Signature(4, 1)

        :return: normalized copy of this signature.
        """
        n, d = self._nominator, self._denominator

        while n & 1 == 0 and d > 1:
            n >>= 1
            d >>= 1

        return Signature(n, d)

    def _to_common_denominator(self, other: 'Signature') -> Tuple[int, int, int]:
        n1, d1 = self._nominator, self._denominator
        n2, d2 = other._nominator, other._denominator

        if d1 == d2:
            return n1, n2, d1

        if d1 > d2:
            return n1, d1 // d2 * n2, d1

        return n2, d2 // d1 * n1, d2

    def __str__(self) -> str:
        """
        Returns human-readable string representation of the signature.

        :return: human-readable string representation of the signature
        """
        return f'{self._nominator}/{self._denominator}'

    def __repr__(self) -> str:
        """
        Returns string representation of the signature.

        :return: string representation of the signature
        """
        return f'{self.__class__.__name__}({self._nominator}, {self._denominator})'

    def __eq__(self, other: 'Signature') -> bool:
        """
        Compares two signatures for equality.
        Signatures are transformed to the common denominator and then their nominators are compared.

        :param other: other signature
        :return: True if signatures equal, False otherwise
        """
        n1, n2, _ = self._to_common_denominator(other)
        return n1 == n2

    def __le__(self, other: 'Signature') -> bool:
        """
        Compares two signatures.
        Signatures are transformed to the common denominator and then their nominators are compared.

        :param other: other signature
        :return: True if this signature is less or equal than other signature
        """
        n1, n2, _ = self._to_common_denominator(other)
        return n1 <= n2

    def __lt__(self, other: 'Signature') -> bool:
        """
        Compares two signatures.
        Signatures are transformed to the common denominator and then their nominators are compared.

        :param other: other signature
        :return: True if this signature is less than other signature
        """
        n1, n2, _ = self._to_common_denominator(other)
        return n1 < n2

    def __ge__(self, other: 'Signature') -> bool:
        """
        Compares two signatures.
        Signatures are transformed to the common denominator and then their nominators are compared.

        :param other: other signature
        :return: True if this signature is greater or equal than other signature
        """
        n1, n2, _ = self._to_common_denominator(other)
        return n1 >= n2

    def __gt__(self, other: 'Signature') -> bool:
        """
        Compares two signatures.
        Signatures are transformed to the common denominator and then their nominators are compared.

        :param other: other signature
        :return: True if this signature is greater than other signature
        """
        n1, n2, _ = self._to_common_denominator(other)
        return n1 > n2

    def __add__(self, other: 'Signature') -> 'Signature':
        """
        Returns sum of two signatures.
        Before summation signatures are transformed to the common denominator.

        :param other: other signature
        :return: sum of two signatures
        """
        n1, n2, d = self._to_common_denominator(other)
        return Signature(n1 + n2, d)

    def __mul__(self, other: 'Signature') -> 'Signature':
        """
        Returns multiplication of two signatures.

        :param other: other signature
        :return: multiplication of two signatures
        """
        return Signature(self._nominator * other._nominator, self._denominator * other._denominator)

    def __abs__(self) -> 'Signature':
        """
        Returns absolute value of the signature.

        :return: absolute value of the signature
        """
        return Signature(abs(self._nominator), self._denominator)
