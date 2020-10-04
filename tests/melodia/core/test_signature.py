import pytest

from melodia.core import Signature


def test_signature_basics():
    Signature(0, 1)
    Signature(1, 2)
    Signature(2, 4)
    Signature(3, 4)
    Signature(4, 4)
    Signature(1000, 4)

    with pytest.raises(ValueError):
        Signature(-1, 4)

    with pytest.raises(ValueError):
        Signature(0, 0)

    with pytest.raises(ValueError):
        Signature(0, -1)

    with pytest.raises(ValueError):
        Signature(1, 5)

    with pytest.raises(ValueError):
        Signature(1, 333)

    s = Signature(43, 4)

    assert s.nominator == 43
    assert s._denominator == 4


def test_signature_to():
    s1 = Signature(1, 2)
    s2 = s1.to(8)

    assert s1.nominator == 1
    assert s1.denominator == 2
    assert s2.nominator == 4
    assert s2.denominator == 8


def test_signature_normalized():
    s1 = Signature(6, 8)
    s2 = s1.normalized()

    assert s1.nominator == 6
    assert s1.denominator == 8
    assert s2.nominator == 3
    assert s2.denominator == 4


def test_signature_eq():
    assert Signature(0, 1) == Signature(0, 4)
    assert Signature(1, 4) == Signature(8, 32)
    assert Signature(3, 2) == Signature(6, 4)


def test_signature_comp():
    assert Signature(2, 4) >= Signature(1, 2)
    assert Signature(2, 4) <= Signature(1, 2)
    assert Signature(2, 4) > Signature(1, 4)
    assert Signature(2, 4) >= Signature(1, 4)
    assert Signature(2, 4) < Signature(3, 4)
    assert Signature(2, 4) <= Signature(3, 4)


def test_signature_sum():
    assert Signature(0, 1) + Signature(0, 1) == Signature(0, 1)
    assert Signature(1, 2) + Signature(1, 2) == Signature(1, 1)
    assert Signature(1, 2) + Signature(1, 4) == Signature(3, 4)


def test_signature_mul():
    assert Signature(1, 4) * Signature(2, 2) == Signature(2, 8)
    assert Signature(3, 4) * Signature(5, 4) == Signature(15, 16)
    assert Signature(1, 1) * Signature(2, 1) == Signature(2, 1)


def test_signature_abs():
    assert abs(Signature(3, 8)) == Signature(3, 8)
