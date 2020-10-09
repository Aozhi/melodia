import io

import pytest

from melodia.core import Signature, Tone
from melodia.io.midi import _Reader, MIDIParsingError, MIDIReader


def test_reader():
    r1 = _Reader(b'abcdef')

    assert len(r1) == 6

    assert r1.read(2) == b'ab'
    assert r1.read(3) == b'cde'
    r1.shift(-2)
    assert r1.read(3) == b'def'

    assert len(r1) == 6

    with pytest.raises(MIDIParsingError):
        r1.read(1)

    with pytest.raises(MIDIParsingError):
        r1.read(10)

    with pytest.raises(MIDIParsingError):
        r1.read(1)

    assert len(r1) == 6

    assert r1.read(0) == b''

    r1.shift(-6)
    assert r1.read(6) == b'abcdef'

    with pytest.raises(MIDIParsingError):
        r1.read(1)


def test_midi_read_chunks():
    read_chunks = MIDIReader._read_chunks

    data = b'AAAA\x00\x00\x00\x01\xEF'

    with io.BytesIO(data) as f:
        result = list(read_chunks(f))

    assert len(result) == 1
    assert result[0][0] == b'AAAA'
    assert len(result[0][1]) == 1
    assert result[0][1].read(1) == b'\xEF'


def test_midi_parse_header():
    parse_header = MIDIReader._parse_header

    data = b'\x00\x01\x00\x02\x00\x03'
    assert parse_header(_Reader(data)) == (1, 2, 3)


def test_midi_time_to_signature():
    time_to_signature = MIDIReader._time_to_signature

    with pytest.raises(AssertionError):
        time_to_signature(0, 0)

    with pytest.raises(AssertionError):
        time_to_signature(0, -10)

    assert time_to_signature(1, 1) == Signature(1, 4)
    assert time_to_signature(2, 1) == Signature(2, 4)
    assert time_to_signature(3, 1) == Signature(3, 4)
    assert time_to_signature(4, 1) == Signature(4, 4)
    assert time_to_signature(5, 1) == Signature(5, 4)
    assert time_to_signature(6, 1) == Signature(6, 4)
    assert time_to_signature(7, 1) == Signature(7, 4)
    assert time_to_signature(8, 1) == Signature(8, 4)

    assert time_to_signature(5, 10) == Signature(1, 8)
    assert time_to_signature(10, 10) == Signature(1, 4)
    assert time_to_signature(100, 10) == Signature(10, 4)
    assert time_to_signature(1000, 10) == Signature(100, 4)
    assert time_to_signature(500, 10) == Signature(50, 4)

    assert time_to_signature(3, 96) == Signature(1, 128)


def test_midi_pitch_to_tone():
    midi = MIDIReader(middle_c='C3')
    assert midi._pitch_to_tone(60) == Tone.from_notation('C3')
    assert midi._pitch_to_tone(66) == Tone.from_notation('F#3')
    assert midi._pitch_to_tone(59) == Tone.from_notation('B2')
    assert midi._pitch_to_tone(83) == Tone.from_notation('B4')


def test_midi_read_var_len():
    read_var_len = MIDIReader._read_var_len

    for data, value in [
        (bytes.fromhex('00'), 0x00000000),
        (bytes.fromhex('7F'), 0x0000007F),
        (bytes.fromhex('8100'), 0x00000080),
        (bytes.fromhex('C08000'), 0x00100000),
        (bytes.fromhex('FFFF7F'), 0x001FFFFF),
        (bytes.fromhex('81808000'), 0x00200000),
        (bytes.fromhex('FFFFFF7F'), 0x0FFFFFFF)
    ]:
        assert read_var_len(_Reader(data)) == value
