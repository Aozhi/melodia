import pytest

from melodia.core.note import Note


def test_note_init():
    with pytest.raises(ValueError):
        Note(0, 2.0)

    with pytest.raises(ValueError):
        Note(1000, -0.5)

    Note(0, 0.0)
    Note(1000, 1.0)

    assert Note(0) == Note(0, 1.0)
    assert Note(100) == Note(100, 1.0)


def test_note_eq():
    assert Note(0, 0.0) == Note(0, 0.0)
    assert Note(5, 0.34) == Note(5, 0.34)

    assert Note(0, 0.0) != Note(0, 0.1)
    assert Note(0, 0.0) != Note(1, 0.1)


def test_note_str():
    for i in range(30):
        note = Note(i)
        assert str(note) == note.to_notation()


def test_note_from_notation():
    for notation, pitch in [
        ('C', 0),
        ('C#', 1),
        ('D', 2),
        ('D#', 3),
        ('E', 4),
        ('F', 5),
        ('F#', 6),
        ('G', 7),
        ('G#', 8),
        ('A', 9),
        ('A#', 10),
        ('B', 11),
        ('C1', 12),
        ('C#1', 13),
        ('Db', 1),
        ('Eb', 3),
        ('Fb', 4),
        ('E#', 5),
        ('Ab', 8),
        ('C2', 24),
        ('C3', 36),
        ('C#3', 37),
        ('Db3', 37),
        ('C-1', -12),
        ('C#-1', -11),
        ('B-1', -1)
    ]:
        assert Note.from_notation(notation).pitch == pitch


def test_note_to_notation():
    assert Note.from_notation('C#').to_notation() == 'C#0'
    assert Note.from_notation('C#b').to_notation() == 'C0'
    assert Note.from_notation('C##b').to_notation() == 'C#0'
    assert Note.from_notation('C#b#').to_notation() == 'C#0'
    assert Note.from_notation('Cb##').to_notation() == 'C#0'
    assert Note.from_notation('Ab##43').to_notation() == 'A#43'
    assert Note.from_notation('Ab##-43').to_notation() == 'A#-43'

    assert Note.from_notation('C#').to_notation(transpose_down=True) == 'Db0'
    assert Note.from_notation('C#b').to_notation(transpose_down=True) == 'C0'
    assert Note.from_notation('C##b').to_notation(transpose_down=True) == 'Db0'
    assert Note.from_notation('C#b#').to_notation(transpose_down=True) == 'Db0'
    assert Note.from_notation('Cb##').to_notation(transpose_down=True) == 'Db0'
    assert Note.from_notation('Ab##43').to_notation(transpose_down=True) == 'Bb43'
    assert Note.from_notation('Ab##-43').to_notation(transpose_down=True) == 'Bb-43'


def test_note_to_frequency():
    assert Note.from_notation('A-1').to_frequency() == 13.75
    assert Note.from_notation('A0').to_frequency() == 27.5
    assert Note.from_notation('A1').to_frequency() == 55.0
    assert Note.from_notation('A2').to_frequency() == 110.0
    assert Note.from_notation('A3').to_frequency() == 220.0
    assert Note.from_notation('A4').to_frequency() == 440.0
    assert Note.from_notation('A5').to_frequency() == 880.0
    assert Note.from_notation('A6').to_frequency() == 1760.0
    assert Note.from_notation('A7').to_frequency() == 3520.0
    assert Note.from_notation('A8').to_frequency() == 7040.0
    assert Note.from_notation('A9').to_frequency() == 14080.0

    assert abs(Note.from_notation('C5').to_frequency() - 523.2511306011972) < 1e-3
    assert abs(Note.from_notation('F4').to_frequency() - 349.2282314330039) < 1e-4


def test_note_octave():
    for c in 'ABCDEFG':
        for o in range(-5, 5):
            assert Note.from_notation(f'{c}{o}').octave == o


def test_note_with_velocity():
    n1 = Note(58, velocity=0.4)
    n2 = n1.with_velocity(0.6)

    assert n1.velocity == 0.4
    assert n2.velocity == 0.6
    assert n2.pitch == n1.pitch


def test_note_with_transposed():
    n1 = Note.from_notation('C4')
    n2 = n1.transposed(1)

    assert n1.to_notation() == 'C4'
    assert n2.to_notation() == 'C#4'

    assert Note.from_notation('C4').transposed(2).to_notation() == 'D4'
    assert Note.from_notation('C4').transposed(-1).to_notation() == 'B3'
    assert Note.from_notation('C4').transposed(-2).to_notation() == 'A#3'

    n = Note(152)

    assert n.transposed(1).transposed(5).transposed(-3) == n.transposed(3)
