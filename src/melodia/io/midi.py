from typing import BinaryIO, List, Tuple

from melodia.core.note import Note
from melodia.core.sgnature import Signature
from melodia.core.tone import Tone
from melodia.core.track import Track

_middle_c_delta = 60 - Tone.from_notation('C3').pitch
_pulses_per_quarter = 96
_pulses_per_whole = _pulses_per_quarter * 4


def _signature_to_pulses(signature: Signature) -> int:
    normalized = signature.normalized()

    return _pulses_per_whole // normalized.denominator * normalized.nominator


def _format_var_len(x: int) -> bytes:
    buffer = x & 0x7f
    x >>= 7
    while x > 0:
        buffer <<= 8
        buffer |= 0x80
        buffer += (x & 0x7f)
        x >>= 7

    return buffer.to_bytes(buffer.bit_length() // 8 + 1, 'little')


def _format_signature(signature: Signature, cc: int, bb: int) -> bytes:
    nn = signature.nominator
    dd = signature.denominator.bit_length() - 1

    return b''.join([
        b'\xFF\x58\x04',
        nn.to_bytes(1, 'big'),
        dd.to_bytes(1, 'big'),
        cc.to_bytes(1, 'big'),
        bb.to_bytes(1, 'big')
    ])


def _format_tempo(tempo: int) -> bytes:
    return b''.join([
        b'\xFF\x51\x03',
        tempo.to_bytes(3, 'big')
    ])


def _format_note_on(note: Note, channel: int) -> bytes:
    assert 0 <= channel <= 15

    status = 0x90 | channel
    pitch = note.tone.pitch + _middle_c_delta

    if not 0 <= pitch <= 127:
        raise ValueError(f'Tone {str(note.tone)} can not be written to midi file')

    velocity = int(note.velocity * 127)

    assert 0 <= velocity <= 127

    return b''.join([
        status.to_bytes(1, 'big'),
        pitch.to_bytes(1, 'big'),
        velocity.to_bytes(1, 'big')
    ])


def _format_note_off(note: Note, channel: int) -> bytes:
    assert 0 <= channel <= 15

    status = 0x80 | channel
    pitch = note.tone.pitch + _middle_c_delta

    if not 0 <= pitch <= 127:
        raise ValueError(f'Tone {str(note.tone)} can not be written to midi file')

    velocity = 64

    return b''.join([
        status.to_bytes(1, 'big'),
        pitch.to_bytes(1, 'big'),
        velocity.to_bytes(1, 'big')
    ])


def _format_chunk(kind: bytes, body: bytes) -> bytes:
    assert len(kind) == 4
    return b''.join([kind, len(body).to_bytes(4, 'big'), body])


def _header_chunk(
        kind: int,
        n_tracks: int,
        ticks_per_quarter_note: int
):
    assert kind in (0, 1, 2)
    assert n_tracks > 0
    assert ticks_per_quarter_note < 0x7FFF

    body = b''.join([
        kind.to_bytes(2, 'big'),
        n_tracks.to_bytes(2, 'big'),
        ticks_per_quarter_note.to_bytes(2, 'big')
    ])

    return _format_chunk(b'MThd', body)


class MIDIWriter:
    __slots__ = ('_bpm', '_channel')

    def __init__(self, bpm: float, channel: int):
        self._bpm = bpm
        self._channel = channel

    def dump(self, track: Track, file: BinaryIO) -> None:
        absolute_note_events: List[Tuple[int, bytes]] = []
        for position, note in track:
            note_on_absolute_time = _signature_to_pulses(position)
            note_on_event = _format_note_on(note, channel=self._channel)
            note_off_absolute_time = note_on_absolute_time + _signature_to_pulses(note.duration)
            note_off_event = _format_note_off(note, channel=self._channel)

            absolute_note_events.append((note_on_absolute_time, note_on_event))
            absolute_note_events.append((note_off_absolute_time, note_off_event))

        absolute_note_events.sort(key=lambda x: x[0])

        delta_events: List[Tuple[int, bytes]] = [
            # Time signature
            (0, _format_signature(track.signature, cc=_pulses_per_quarter, bb=8)),
            # Tempo
            (0, _format_tempo(int(60000000 / self._bpm)))
        ]

        last_absolute_time = 0
        for absolute_time, note_event in absolute_note_events:
            delta_events.append((absolute_time - last_absolute_time, note_event))
            last_absolute_time = absolute_time

        # End of track
        delta_events.append((0, b'\xFF\x2F\x00'))

        # Header
        file.write(_header_chunk(
            kind=0,
            n_tracks=1,
            ticks_per_quarter_note=_pulses_per_quarter
        ))

        # Track
        track_body: List[bytes] = []
        for delta_time, event in delta_events:
            track_body.append(_format_var_len(delta_time))
            track_body.append(event)
        file.write(_format_chunk(b'MTrk', b''.join(track_body)))


def dump(track: Track, file: BinaryIO, bpm: float = 120.0, channel: int = 0):
    MIDIWriter(bpm=bpm, channel=channel).dump(track, file)
