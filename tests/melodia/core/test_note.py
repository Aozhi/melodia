import pytest

from melodia.core import Note, Tone, Signature


def test_note_basics():
    assert Note(Tone(60)) == Note(60)
    assert Note(Tone.from_notation('A4')) == Note('A4')

    assert Note(Tone(60), Signature(3, 4)) == Note(60, (3, 4))

    Note('A4', velocity=0.5)

    with pytest.raises(ValueError):
        Note('re')

    with pytest.raises(TypeError):
        Note('A4', '1/4')

    with pytest.raises(ValueError):
        Note('A4', velocity=-1.0)

    with pytest.raises(ValueError):
        Note('A4', velocity=1.1)


def test_note_properties():
    n = Note('B#6', (3, 8), 0.1415)

    assert n.tone == Tone.from_notation('B#6')
    assert n.duration.nominator == 3
    assert n.duration.denominator == 8
    assert n.velocity == 0.1415


def test_note_transposed():
    n1 = Note('A4')
    n2 = n1.transposed(+3)

    assert n1.tone == Tone.from_notation('A4')
    assert n2.tone == Tone.from_notation('C5')

    assert n1.duration.nominator == n2.duration.nominator
    assert n1.duration.denominator == n2.duration.denominator
    assert n1.velocity == n2.velocity


def test_note_with_duration():
    n1 = Note('A4', (3, 8))
    n2 = n1.with_duration((7, 4))

    assert n1.tone == n2.tone

    assert n1.duration == Signature(3, 8)
    assert n2.duration == Signature(7, 4)

    assert n1.velocity == n2.velocity


def test_note_with_velocity():
    n1 = Note('A4', (3, 8), velocity=0.43)
    n2 = n1.with_velocity(0.86)

    assert n1.tone == n2.tone
    assert n1.duration.nominator == n2.duration.nominator
    assert n1.duration.denominator == n2.duration.denominator

    assert n1.velocity == 0.43
    assert n2.velocity == 0.86


def test_note_eq():
    assert Note('C4') == Note('C4')
    assert Note('C4') != Note('C5')

    assert Note('C4', (1, 2), 0.3) == Note('C4', (2, 4), 0.3)
    assert Note('C4', (1, 2), 0.3) != Note('C4', (2, 4), 0.4)


def test_note_comp():
    assert Note('C#4') >= Note('C4')
    assert Note('C#4') > Note('C4')
    assert Note('C#4') <= Note('D4')
    assert Note('C#4') < Note('D4')
