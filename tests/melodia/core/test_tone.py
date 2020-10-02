import pytest

from melodia.core.tone import Tone


def test_tone_eq():
    assert Tone(0) == Tone(0)
    assert Tone(0) != Tone(1)


def test_tone_str():
    for i in range(30):
        tone = Tone(i)
        assert str(tone) == tone.to_notation()


def test_tone_from_notation():
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
        assert Tone.from_notation(notation).pitch == pitch


def test_tone_to_notation():
    assert Tone.from_notation('C#').to_notation() == 'C#0'
    assert Tone.from_notation('C#b').to_notation() == 'C0'
    assert Tone.from_notation('C##b').to_notation() == 'C#0'
    assert Tone.from_notation('C#b#').to_notation() == 'C#0'
    assert Tone.from_notation('Cb##').to_notation() == 'C#0'
    assert Tone.from_notation('Ab##43').to_notation() == 'A#43'
    assert Tone.from_notation('Ab##-43').to_notation() == 'A#-43'

    assert Tone.from_notation('C#').to_notation(transpose_down=True) == 'Db0'
    assert Tone.from_notation('C#b').to_notation(transpose_down=True) == 'C0'
    assert Tone.from_notation('C##b').to_notation(transpose_down=True) == 'Db0'
    assert Tone.from_notation('C#b#').to_notation(transpose_down=True) == 'Db0'
    assert Tone.from_notation('Cb##').to_notation(transpose_down=True) == 'Db0'
    assert Tone.from_notation('Ab##43').to_notation(transpose_down=True) == 'Bb43'
    assert Tone.from_notation('Ab##-43').to_notation(transpose_down=True) == 'Bb-43'


def test_tone_to_frequency():
    assert Tone.from_notation('A-1').to_frequency() == 13.75
    assert Tone.from_notation('A0').to_frequency() == 27.5
    assert Tone.from_notation('A1').to_frequency() == 55.0
    assert Tone.from_notation('A2').to_frequency() == 110.0
    assert Tone.from_notation('A3').to_frequency() == 220.0
    assert Tone.from_notation('A4').to_frequency() == 440.0
    assert Tone.from_notation('A5').to_frequency() == 880.0
    assert Tone.from_notation('A6').to_frequency() == 1760.0
    assert Tone.from_notation('A7').to_frequency() == 3520.0
    assert Tone.from_notation('A8').to_frequency() == 7040.0
    assert Tone.from_notation('A9').to_frequency() == 14080.0

    assert abs(Tone.from_notation('C5').to_frequency() - 523.2511306011972) < 1e-3
    assert abs(Tone.from_notation('F4').to_frequency() - 349.2282314330039) < 1e-4


def test_tone_octave():
    for tone in 'ABCDEFG':
        for octave in range(-5, 5):
            assert Tone.from_notation(f'{tone}{octave}').octave == octave


def test_note_with_transposed():
    n1 = Tone.from_notation('C4')
    n2 = n1.transposed(1)

    assert n1.to_notation() == 'C4'
    assert n2.to_notation() == 'C#4'

    assert Tone.from_notation('C4').transposed(2).to_notation() == 'D4'
    assert Tone.from_notation('C4').transposed(-1).to_notation() == 'B3'
    assert Tone.from_notation('C4').transposed(-2).to_notation() == 'A#3'

    n = Tone(152)

    assert n.transposed(1).transposed(5).transposed(-3) == n.transposed(3)
