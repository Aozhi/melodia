import pytest

from melodia.core import Signature, Note
from melodia.io.midi import MIDIWriter


def test_midi_basics():
    with pytest.raises(ValueError):
        MIDIWriter(pulses_per_quarter=0)

    with pytest.raises(ValueError):
        MIDIWriter(pulses_per_quarter=-10)

    with pytest.raises(ValueError):
        MIDIWriter(pulses_per_quarter=65536)

    with pytest.raises(ValueError):
        MIDIWriter(channel=-1)

    with pytest.raises(ValueError):
        MIDIWriter(channel=16)


def test_midi_signature_to_pulses():
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(0, 1)) == 0
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(1, 1)) == 4
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(1, 2)) == 2
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(1, 4)) == 1
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(1, 8)) == 0
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(1, 16)) == 0

    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(0, 16)) == 0
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(1, 16)) == 0
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(2, 16)) == 0
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(3, 16)) == 0
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(4, 16)) == 1
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(5, 16)) == 1
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(6, 16)) == 1
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(7, 16)) == 1
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(8, 16)) == 2
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(9, 16)) == 2
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(10, 16)) == 2
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(11, 16)) == 2
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(12, 16)) == 3
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(13, 16)) == 3
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(14, 16)) == 3
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(15, 16)) == 3
    assert MIDIWriter(pulses_per_quarter=1)._signature_to_pulses(Signature(16, 16)) == 4

    assert MIDIWriter(pulses_per_quarter=32)._signature_to_pulses(Signature(1, 8)) == 16

    assert MIDIWriter(pulses_per_quarter=1000)._signature_to_pulses(Signature(1, 2)) == 2000


def test_midi_format_note_on():
    midi_c4 = MIDIWriter(middle_c='C4', channel=3)

    with pytest.raises(ValueError):
        midi_c4._format_note_on(Note('C-2'))

    with pytest.raises(ValueError):
        midi_c4._format_note_on(Note('C10'))

    with pytest.raises(ValueError):
        midi_c4._format_note_on(Note('D11'))

    midi_c3 = MIDIWriter(middle_c='C3', channel=3)

    midi_c3._format_note_on(Note('C-2'))

    with pytest.raises(ValueError):
        midi_c3._format_note_on(Note('C-3'))

    assert midi_c3._format_note_on(Note('C3', velocity=1.0)) == b'\x93\x3c\x7f'
    assert midi_c3._format_note_on(Note('C4', velocity=0.0)) == b'\x93\x48\x00'

    assert midi_c4._format_note_on(Note('C4', velocity=0.0)) == b'\x93\x3c\x00'

    n = Note('C4')
    n._velocity = 2.0

    assert midi_c4._format_note_on(n) == b'\x93\x3c\x7f'

    n._velocity = -10.0

    assert midi_c4._format_note_on(n) == b'\x93\x3c\x00'


def test_midi_format_note_off():
    midi_c4 = MIDIWriter(middle_c='C4', channel=3)

    with pytest.raises(ValueError):
        midi_c4._format_note_off(Note('C-2'))

    with pytest.raises(ValueError):
        midi_c4._format_note_off(Note('C10'))

    with pytest.raises(ValueError):
        midi_c4._format_note_off(Note('D11'))

    midi_c3 = MIDIWriter(middle_c='C3', channel=3)

    midi_c3._format_note_off(Note('C-2'))

    with pytest.raises(ValueError):
        midi_c3._format_note_off(Note('C-3'))

    assert midi_c3._format_note_off(Note('C3', velocity=1.0)) == b'\x83\x3c\x40'
    assert midi_c3._format_note_off(Note('C4', velocity=0.0)) == b'\x83\x48\x40'

    assert midi_c4._format_note_off(Note('C4', velocity=0.0)) == b'\x83\x3c\x40'

    n = Note('C4')
    n._velocity = 2.0

    assert midi_c4._format_note_off(n) == b'\x83\x3c\x40'

    n._velocity = -10.0

    assert midi_c4._format_note_off(n) == b'\x83\x3c\x40'


def test_midi_format_var_len():
    format_var_len = MIDIWriter._format_var_len

    assert format_var_len(0x00000000) == bytes.fromhex('00')
    assert format_var_len(0x00000040) == bytes.fromhex('40')
    assert format_var_len(0x0000007F) == bytes.fromhex('7F')
    assert format_var_len(0x00000080) == bytes.fromhex('8100')
    assert format_var_len(0x00002000) == bytes.fromhex('C000')
    assert format_var_len(0x00003FFF) == bytes.fromhex('FF7F')
    assert format_var_len(0x00004000) == bytes.fromhex('818000')
    assert format_var_len(0x00100000) == bytes.fromhex('C08000')
    assert format_var_len(0x001FFFFF) == bytes.fromhex('FFFF7F')
    assert format_var_len(0x00200000) == bytes.fromhex('81808000')
    assert format_var_len(0x08000000) == bytes.fromhex('C0808000')
    assert format_var_len(0x0FFFFFFF) == bytes.fromhex('FFFFFF7F')


def test_midi_format_signature():
    midi = MIDIWriter()

    assert midi._format_signature(Signature(0, 1), 16, 32) == b'\xff\x58\x04\x00\x00\x10\x20'
    assert midi._format_signature(Signature(3, 4), 16, 32) == b'\xff\x58\x04\x03\x02\x10\x20'
    assert midi._format_signature(Signature(127, 170141183460469231731687303715884105728), 16, 32) == \
           b'\xff\x58\x04\x7f\x7f\x10\x20'

    assert midi._format_signature(Signature(255, 170141183460469231731687303715884105728), 16, 32) == \
           b'\xff\x58\x04\xff\x7f\x10\x20'

    with pytest.raises(OverflowError):
        midi._format_signature(Signature(512, 512), 16, 32)

    with pytest.raises(OverflowError):
        midi._format_signature(Signature(1, 4), -16, 32)

    with pytest.raises(OverflowError):
        midi._format_signature(Signature(1, 4), 16, -32)

    with pytest.raises(OverflowError):
        midi._format_signature(Signature(1, 4), 300, 32)

    with pytest.raises(OverflowError):
        midi._format_signature(Signature(1, 4), 16, 300)


def test_midi_format_chunk():
    format_chunk = MIDIWriter._format_chunk

    assert format_chunk(b'MThd', b'\x00\x7F\x00\x80\x90\xFF\x76') == \
           b'MThd\x00\x00\x00\x07\x00\x7F\x00\x80\x90\xFF\x76'

    assert format_chunk(b'MThd', b'') == b'MThd\x00\x00\x00\x00'
    assert format_chunk(b'MThd', b'\x00') == b'MThd\x00\x00\x00\x01\x00'

    with pytest.raises(AssertionError):
        format_chunk(b'', b'')

    with pytest.raises(AssertionError):
        format_chunk(b'a', b'')

    with pytest.raises(AssertionError):
        format_chunk(b'ab', b'')

    with pytest.raises(AssertionError):
        format_chunk(b'abc', b'')

    assert format_chunk(b'abcd', b'') == b'abcd\x00\x00\x00\x00'

    with pytest.raises(AssertionError):
        format_chunk(b'abcde', b'')


def test_midi_format_header_chunk():
    midi = MIDIWriter(pulses_per_quarter=1)

    assert midi._format_header_chunk(0, 1) == b'MThd\x00\x00\x00\x06\x00\x00\x00\x01\x00\x01'
    assert midi._format_header_chunk(1, 110) == b'MThd\x00\x00\x00\x06\x00\x01\x00\x6e\x00\x01'
    assert midi._format_header_chunk(1, 0xffff) == b'MThd\x00\x00\x00\x06\x00\x01\xff\xff\x00\x01'

    midi = MIDIWriter(pulses_per_quarter=0x2007)

    assert midi._format_header_chunk(2, 0x1996) == b'MThd\x00\x00\x00\x06\x00\x02\x19\x96\x20\x07'

    with pytest.raises(AssertionError):
        midi._format_header_chunk(3, 0x1996)

    with pytest.raises(AssertionError):
        midi._format_header_chunk(4, 0x1996)

    with pytest.raises(AssertionError):
        midi._format_header_chunk(-1, 0x1996)
