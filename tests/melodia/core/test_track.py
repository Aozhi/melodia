import pytest

from melodia.core import Track, Signature, Note


def test_track_basics():
    Track()
    Track((1, 4))
    Track(Signature(1, 4))

    with pytest.raises(ValueError):
        Track((1, 6))


def test_track_signature():
    t = Track((3, 8))
    assert t.signature.nominator == 3
    assert t.signature.denominator == 8


def test_track_length():
    assert Track().length == Signature(0, 1)

    t = Track()
    t.add(Note(0, (10, 4)))
    assert t.length == Signature(10, 4)

    t.add(Note(0, (30, 8)), (40, 2))
    assert t.length == Signature(190, 8)

    t.add(Note(0, (1, 4)))
    assert t.length == Signature(192, 8)


def test_track_add():
    t = Track()
    assert list(t) == []

    t.add(Note(0, (1, 4)))
    assert list(t) == [(Signature(0, 1), Note(0, (1, 4)))]

    t.add([Note(0, (1, 4)), Note(1, (1, 4)), Note(-1, (1, 4))])
    assert list(t) == [
        (Signature(0, 1), Note(0, (1, 4))),
        (Signature(1, 4), Note(-1, (1, 4))),
        (Signature(1, 4), Note(0, (1, 4))),
        (Signature(1, 4), Note(1, (1, 4))),
    ]

    t.add(Note(42, (8, 1)), (13, 1))
    assert list(t) == [
        (Signature(0, 1), Note(0, (1, 4))),
        (Signature(1, 4), Note(-1, (1, 4))),
        (Signature(1, 4), Note(0, (1, 4))),
        (Signature(1, 4), Note(1, (1, 4))),
        (Signature(13, 1), Note(42, (8, 1)))
    ]
    assert list(t) == [
        (Signature(0, 1), Note(0, (1, 4))),
        (Signature(1, 4), Note(-1, (1, 4))),
        (Signature(1, 4), Note(0, (1, 4))),
        (Signature(1, 4), Note(1, (1, 4))),
        (Signature(13, 1), Note(42, (8, 1)))
    ]
    assert list(t) == [
        (Signature(0, 1), Note(0, (1, 4))),
        (Signature(1, 4), Note(-1, (1, 4))),
        (Signature(1, 4), Note(0, (1, 4))),
        (Signature(1, 4), Note(1, (1, 4))),
        (Signature(13, 1), Note(42, (8, 1)))
    ]