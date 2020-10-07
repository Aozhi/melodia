import io
from operator import itemgetter
from typing import BinaryIO, List, Tuple, Union

from melodia.core.note import Note
from melodia.core.sgnature import Signature
from melodia.core.tone import Tone
from melodia.core.track import Track


class MIDIWriter:
    """
    MIDI writer capable of writing `Track` objects to MIDI Spec. 1.1 files.
    It can be used to export your software-defined tracks to any DAW.
    """
    __slots__ = (
        '_pulses_per_quarter',
        '_pulses_per_whole',
        '_middle_c',
        '_middle_c_delta',
        '_bpm',
        '_channel'
    )

    def __init__(
            self,
            pulses_per_quarter: int = 96,
            middle_c: Union[Tone, int, str] = Tone.from_notation('C3'),
            bpm: float = 120.0,
            channel: int = 0
    ):
        """
        Initializes MIDIWriter object.

        Pulses per quarter note defines maximum resolution of the MIDI events.
        With this parameter equal to 1 one can not have notes shorter than 1/4.
        Default value should be suitable for any software and track.

        Middle C is a tone corresponding to integer value 60 in the MIDI specification.
        For most of the modern software it is C3. If resulting MIDI files
        is shifted by an octave in your software, use value 'C4'.

        Beats per minute defines tempo of the track.

        MIDI channel can be any value from 0 to 15.

        :param pulses_per_quarter: number of pulses per quarter note (default: 96)
        :param middle_c: middle c tone (default: 'C3')
        :param bpm: beats per minute (default: 120.0)
        :param channel: MIDI channel to write to (default: 0)
        """
        if not 1 <= pulses_per_quarter <= 65535:
            raise ValueError('pulses_per_quarter must be in range [1, 65535]')

        if not 0 <= channel <= 15:
            raise ValueError('channel must be in range [0, 15]')

        self._pulses_per_quarter: int = pulses_per_quarter
        self._pulses_per_whole: int = pulses_per_quarter * 4

        self._middle_c = middle_c

        self._middle_c_delta: int
        if isinstance(middle_c, Tone):
            self._middle_c_delta = 60 - middle_c.pitch
        elif isinstance(middle_c, int):
            self._middle_c_delta = 60 - Tone(middle_c).pitch
        elif isinstance(middle_c, str):
            self._middle_c_delta = 60 - Tone.from_notation(middle_c).pitch
        else:
            raise TypeError('middle_c must be a Tone object, an integer or a string')

        self._bpm = bpm
        self._channel = channel

    def _signature_to_pulses(self, signature: Signature) -> int:
        normalized = signature.normalized()

        return self._pulses_per_whole * normalized.nominator // normalized.denominator

    def _format_note_on(self, note: Note) -> bytes:
        status = 0x90 | self._channel
        pitch = note.tone.pitch + self._middle_c_delta

        if not 0 <= pitch <= 127:
            raise ValueError(f'Tone {str(note.tone)} can not be written '
                             f'to midi file with middle c equals to {str(self._middle_c)}')

        velocity = max(0, min(127, int(note.velocity * 127)))

        return b''.join([
            status.to_bytes(1, 'big'),
            pitch.to_bytes(1, 'big'),
            velocity.to_bytes(1, 'big')
        ])

    def _format_note_off(self, note: Note) -> bytes:
        status = 0x80 | self._channel
        pitch = note.tone.pitch + self._middle_c_delta

        if not 0 <= pitch <= 127:
            raise ValueError(f'Tone {str(note.tone)} can not be written '
                             f'to midi file with middle c equals to {str(self._middle_c)}')

        velocity = 64

        return b''.join([
            status.to_bytes(1, 'big'),
            pitch.to_bytes(1, 'big'),
            velocity.to_bytes(1, 'big')
        ])

    @staticmethod
    def _format_var_len(x: int) -> bytes:
        buffer = x & 0x7f
        x >>= 7
        while x > 0:
            buffer <<= 8
            buffer |= 0x80
            buffer += (x & 0x7f)
            x >>= 7

        return buffer.to_bytes(buffer.bit_length() // 8 + 1, 'little')

    @staticmethod
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

    @staticmethod
    def _format_tempo(tempo: int) -> bytes:
        return b''.join([
            b'\xFF\x51\x03',
            tempo.to_bytes(3, 'big')
        ])

    @staticmethod
    def _format_chunk(kind: bytes, body: bytes) -> bytes:
        assert len(kind) == 4, 'kind must be exactly 4 bytes long'
        return b''.join([kind, len(body).to_bytes(4, 'big'), body])

    def _format_header_chunk(
            self,
            kind: int,
            n_tracks: int
    ):
        assert kind in (0, 1, 2), 'kind must be 0, 1 or 2'

        body = b''.join([
            kind.to_bytes(2, 'big'),
            n_tracks.to_bytes(2, 'big'),
            self._pulses_per_quarter.to_bytes(2, 'big')
        ])

        return MIDIWriter._format_chunk(b'MThd', body)

    def dump(self, track: Track, file: BinaryIO) -> None:
        """
        Writes track to MIDI file.

        :param track: track to write
        :param file: binary file-like object
        :return: None
        """
        absolute_note_events: List[Tuple[int, bytes]] = []
        for position, note in track:
            note_on_absolute_time = self._signature_to_pulses(position)
            note_on_event = self._format_note_on(note)
            note_off_absolute_time = note_on_absolute_time + self._signature_to_pulses(note.duration)
            note_off_event = self._format_note_off(note)

            absolute_note_events.append((note_on_absolute_time, note_on_event))
            absolute_note_events.append((note_off_absolute_time, note_off_event))

        absolute_note_events.sort(key=itemgetter(0))

        delta_events: List[Tuple[int, bytes]] = [
            # Time signature
            (0, self._format_signature(track.signature, cc=self._pulses_per_quarter, bb=8)),
            # Tempo
            (0, self._format_tempo(int(60000000 / self._bpm)))
        ]

        last_absolute_time = 0
        for absolute_time, note_event in absolute_note_events:
            delta_events.append((absolute_time - last_absolute_time, note_event))
            last_absolute_time = absolute_time

        # End of track
        delta_events.append((0, b'\xFF\x2F\x00'))

        # Write header to file
        file.write(self._format_header_chunk(kind=0, n_tracks=1))

        # Write track to file
        track_body: List[bytes] = []
        for delta_time, event in delta_events:
            track_body.append(self._format_var_len(delta_time))
            track_body.append(event)
        file.write(self._format_chunk(b'MTrk', b''.join(track_body)))


def dump(track: Track, file: BinaryIO, bpm: float = 120.0, channel: int = 0) -> None:
    """
    Writes track to MIDI file. If you need more adjustable parameters, use `MIDIWriter` class.

    :param track: track to write
    :param file: binary file-like object
    :param bpm: beats per minute
    :param channel: MIDI channel to use
    :return: None
    """
    MIDIWriter(bpm=bpm, channel=channel).dump(track, file)


def dumps(track: Track, bpm: float = 120.0, channel: int = 0) -> bytes:
    """
    Serializes track to MIDI format and returns it as array of bytes.

    :param track: track to write
    :param bpm: beats per minute
    :param channel: MIDI channel to use
    :return: track serialized to MIDI format (array of bytes)
    """
    with io.BytesIO() as file:
        dump(track, file, bpm=bpm, channel=channel)
        return file.getbuffer().tobytes()
