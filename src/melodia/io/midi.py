import io
from collections import defaultdict
from dataclasses import dataclass
from operator import itemgetter
from typing import BinaryIO, List, Tuple, Union, Optional, Dict, Generator

from melodia.core.note import Note
from melodia.core.signature import Signature
from melodia.core.tone import Tone
from melodia.core.track import Track


class MIDIError(Exception):
    pass


class MIDIParsingError(MIDIError):
    pass


class _Reader:
    __slots__ = ('_data', '_idx')

    def __init__(self, data: bytes):
        self._data = data
        self._idx = 0

    def read(self, n: int) -> bytes:
        if len(self._data) - self._idx < n:
            self._idx = len(self._data)
            raise MIDIParsingError('Invalid MIDI file: unexpected end of data')
        result = self._data[self._idx:self._idx + n]
        self._idx += n
        return result

    def shift(self, n: int) -> None:
        self._idx += n

    def __len__(self) -> int:
        return len(self._data)


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
        is shifted by an octave in your software, try using value 'C4'.

        Beats per minute defines tempo of the track.

        MIDI channel can be any value from 0 to 15.

        :param pulses_per_quarter: number of pulses per quarter note (default: 96)
        :param middle_c: middle c tone (default: 'C3')
        :param bpm: beats per minute (default: 120.0)
        :param channel: MIDI channel to write to (default: 0)
        """
        if not 1 <= pulses_per_quarter <= 32767:
            raise ValueError('pulses_per_quarter must be in range [1, 32767]')

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

    def dumps(self, track: Track) -> bytes:
        """
        Serializes track to MIDI format and returns it as array of bytes.

        :param track: track to write
        :return: track serialized to MIDI format (array of bytes)
        """
        with io.BytesIO() as file:
            self.dump(track, file)
            return file.getbuffer().tobytes()


_event_lengths = [-1] * 0xFF

# Note off and note on events
for i in range(0x80, 0x9F + 1):
    _event_lengths[i] = 2

# After touch event
for i in range(0xA0, 0xAF + 1):
    _event_lengths[i] = 2

# Controller event
for i in range(0xB0, 0xBF + 1):
    _event_lengths[i] = 2

# Program change
for i in range(0xC0, 0xCF + 1):
    _event_lengths[i] = 1

# Channel pressure
for i in range(0xD0, 0xDF + 1):
    _event_lengths[i] = 1

# Pitch wheel
for i in range(0xE0, 0xEF + 1):
    _event_lengths[i] = 2

# MTC Quarter Frame
_event_lengths[0xF1] = 1

# Song Position Pointer
_event_lengths[0xF2] = 2

# Song Select
_event_lengths[0xF3] = 1

# Tune Request
_event_lengths[0xF6] = 0

# MIDI Clock
_event_lengths[0xF8] = 0

# Tick
_event_lengths[0xF8] = 0

# MIDI Start
_event_lengths[0xFA] = 0

# MIDI Stop
_event_lengths[0xFC] = 0

# MIDI Continue
_event_lengths[0xFB] = 0

# Active Sense
_event_lengths[0xFE] = 0


@dataclass(frozen=True)
class _Event:
    pass


@dataclass(frozen=True)
class _EventUnsupported(_Event):
    pass


@dataclass(frozen=True)
class _EventNoteOFF(_Event):
    channel: int
    pitch: int
    velocity: int


@dataclass(frozen=True)
class _EventNoteON(_Event):
    channel: int
    pitch: int
    velocity: int


@dataclass(frozen=True)
class _EventEndOfTrack(_Event):
    pass


@dataclass(frozen=True)
class _EventTimeSignature(_Event):
    nn: int
    dd: int
    cc: int
    bb: int


@dataclass(frozen=True)
class _EventGlobalChannel(_Event):
    channel: int


class MIDIReader:
    """
    MIDI reader capable of parsing MIDI Spec. 1.1 files into `~melodia.core.track.Track` objects.
    This reader DOES NOT IMPLEMENT full spec and supports only two MIDI events: Note ON and Note OFF.
    """
    __slots__ = (
        '_middle_c',
        '_middle_c_delta'
    )

    def __init__(
            self,
            middle_c: Union[Tone, int, str] = Tone.from_notation('C3')
    ):
        """
        Initializes MIDIReader object.

        Middle C is a tone corresponding to integer value 60 in the MIDI specification.
        For most of the modern software it is C3. If parsed track
        is shifted by an octave, try using value 'C4'.

        :param middle_c: middle c tone (default: 'C3')
        """
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

    @staticmethod
    def _read_chunks(file: BinaryIO) -> Generator[Tuple[bytes, _Reader], None, None]:
        while True:
            chunk_header = file.read(8)
            if len(chunk_header) == 0:
                break
            if len(chunk_header) < 8:
                raise MIDIParsingError('Invalid MIDI file: incomplete chunk header')
            chunk_name = chunk_header[:4]
            chunk_size = int.from_bytes(chunk_header[5:], 'big')
            chunk_body = file.read(chunk_size)
            if len(chunk_body) < chunk_size:
                raise MIDIParsingError('Invalid MIDI file: incomplete chunk body')
            yield chunk_name, _Reader(chunk_body)

    @staticmethod
    def _parse_header(data: _Reader) -> Tuple[int, int, int]:
        kind = int.from_bytes(data.read(2), 'big')
        n_tracks = int.from_bytes(data.read(2), 'big')
        division = int.from_bytes(data.read(2), 'big')
        return kind, n_tracks, division

    @staticmethod
    def _time_to_signature(time: int, ticks_per_quarter: int) -> Signature:
        assert ticks_per_quarter > 0, 'ticks_per_quarter must be positive'

        return Signature(time * 4096 // ticks_per_quarter, 4 * 4096).normalized()

    def _pitch_to_tone(self, pitch: int) -> Tone:
        return Tone(pitch - self._middle_c_delta)

    @staticmethod
    def _read_var_len(data: _Reader) -> int:
        result = int.from_bytes(data.read(1), 'big')

        if result & 0x80 == 0:
            return result

        result &= 0x7F

        while True:
            value = int.from_bytes(data.read(1), 'big')
            result = (result << 7) + (value & 0x7F)
            if value & 0x80 == 0:
                break

        return result

    @staticmethod
    def _read_8(data: _Reader) -> int:
        return int.from_bytes(data.read(1), 'big')

    @staticmethod
    def _read_16(data: _Reader) -> int:
        return int.from_bytes(data.read(2), 'big')

    @staticmethod
    def _read_24(data: _Reader) -> int:
        return int.from_bytes(data.read(3), 'big')

    @staticmethod
    def _read_32(data: _Reader) -> int:
        return int.from_bytes(data.read(4), 'big')

    def _parse_track(
            self,
            data: _Reader,
            ticks_per_quarter: int
    ) -> Dict[int, Track]:
        previous_status = None

        def read_event(status: Optional[int] = None) -> _Event:
            nonlocal previous_status

            if status is None:
                status = MIDIReader._read_8(data)

            if status == 0xFF:
                previous_status = status
                # New meta event
                kind = MIDIReader._read_8(data)
                length = MIDIReader._read_var_len(data)
                if kind == 0x2F:
                    # End of track
                    if length != 0x00:
                        raise MIDIParsingError(f'Invalid MIDI file: end of track event has length {length} != 0')
                    return _EventEndOfTrack()
                elif kind == 0x20:
                    # Meta channel
                    if length != 0x01:
                        raise MIDIParsingError(f'Invalid MIDI file: meta channel event has length {length} != 3')
                    channel = MIDIReader._read_8(data)
                    return _EventGlobalChannel(channel=channel)
                elif kind == 0x58:
                    # Time signature
                    if length != 0x04:
                        raise MIDIParsingError(f'Invalid MIDI file: time signature event has length {length} != 3')
                    nn = MIDIReader._read_8(data)
                    dd = MIDIReader._read_8(data)
                    cc = MIDIReader._read_8(data)
                    bb = MIDIReader._read_8(data)
                    return _EventTimeSignature(nn=nn, dd=dd, cc=cc, bb=bb)
                else:
                    # Skip unsupported meta event body
                    data.read(length)
                    return _EventUnsupported()
            elif status >= 0x80:
                previous_status = status
                # New event
                kind = status >> 4
                channel = status & 0xF
                if kind == 8:
                    pitch = MIDIReader._read_8(data)
                    velocity = MIDIReader._read_8(data)
                    return _EventNoteOFF(channel=channel, pitch=pitch, velocity=velocity)
                elif kind == 9:
                    pitch = MIDIReader._read_8(data)
                    velocity = MIDIReader._read_8(data)

                    if velocity == 0:
                        return _EventNoteOFF(channel=channel, pitch=pitch, velocity=velocity)

                    return _EventNoteON(channel=channel, pitch=pitch, velocity=velocity)
                elif status == 0xF0:
                    # System exclusive
                    value = 0
                    while value != 0xF7:
                        value = data.read(1)
                    return _EventUnsupported()
                else:
                    length = _event_lengths[status]
                    if length == -1:
                        raise MIDIParsingError(f'Unknown status {status}')
                    else:
                        data.read(length)
                    return _EventUnsupported()
            else:
                # Running status
                data.shift(-1)
                return read_event(status=previous_status)

        channel_events: Dict[int, List[Tuple[int, _Event]]] = defaultdict(list)
        channel_signatures: Dict[int, Signature] = {}
        global_channel: int = -1

        last_time = 0

        while True:
            delta_time = MIDIReader._read_var_len(data)
            absolute_time = last_time + delta_time
            last_time = absolute_time
            event = read_event()

            if isinstance(event, (_EventNoteON, _EventNoteOFF)):
                channel_events[event.channel].append((absolute_time, event))
                continue

            if isinstance(event, _EventEndOfTrack):
                break

            if isinstance(event, _EventGlobalChannel):
                global_channel = event.channel
                continue

            if isinstance(event, _EventTimeSignature):
                channel_signatures[global_channel] = Signature(event.nn, 1 << event.dd)
                continue

        # In case there is only signature
        if not channel_events:
            channel_events[0].append((0, _EventUnsupported()))

        result: Dict[int, Track] = {}

        for channel, events in channel_events.items():
            if channel in channel_signatures:
                signature = channel_signatures[channel]
            else:
                signature = channel_signatures.get(-1, Signature(4, 4))

            track = Track(signature=signature)
            running_notes: Dict[int, Tuple[int, _EventNoteON]] = {}

            for absolute_time, event in events:
                if isinstance(event, _EventNoteON):
                    if event.pitch in running_notes:
                        continue

                    running_notes[event.pitch] = (absolute_time, event)
                    continue

                if isinstance(event, _EventNoteOFF):
                    if event.pitch not in running_notes:
                        continue

                    note_beginning, note_on = running_notes[event.pitch]
                    del running_notes[event.pitch]

                    tone: Tone = self._pitch_to_tone(event.pitch)
                    duration: Signature = self._time_to_signature(
                        absolute_time - note_beginning,
                        ticks_per_quarter=ticks_per_quarter
                    )
                    velocity: float = max(0.0, min(1.0, note_on.velocity / 127.0))
                    position = self._time_to_signature(
                        note_beginning,
                        ticks_per_quarter=ticks_per_quarter
                    )

                    track.add(Note(tone, duration, velocity), position)
                    continue

            result[channel] = track

        return result

    def load(self, file: BinaryIO, channel: Optional[int] = None) -> Track:
        """
        Reads track from the MIDI file. MIDI file can contain up to 16 channels.
        If ``channel`` is specified, track from this channel is returned. If ``channel``
        is omitted, track composed of all channels is returned.

        :param file: binary file-like object
        :param channel: channel to read from (default: None)
        :return: parsed track
        """

        kind = None
        ticks_per_quarter = None
        tracks = None

        for chunk_kind, chunk_data in self._read_chunks(file):
            if chunk_kind == b'MThd':
                kind, n_tracks, division = self._parse_header(chunk_data)
                if kind != 0:
                    raise MIDIParsingError(f'Unsupported MIDI file: format is {kind}')
                if n_tracks != 1:
                    raise MIDIParsingError('Invalid MIDI file: multiple tracks in a single track file')
                if division > 0x7FFF:
                    raise MIDIParsingError('Unsupported MIDI file: unsupported division')
                ticks_per_quarter = division
            if chunk_kind == b'MTrk':
                if ticks_per_quarter is None:
                    raise MIDIParsingError('Invalid MIDI file: missing header chunk')
                tracks = self._parse_track(chunk_data, ticks_per_quarter)

        if kind is None:
            raise MIDIParsingError('Invalid MIDI file: missing header chunk')

        if tracks is None:
            raise MIDIParsingError('Invalid MIDI file: missing track chunk')

        if not tracks:
            return Track(signature=Signature(4, 4))

        if channel is None:
            max_signature = Signature(0, 1)

            for track in tracks.values():
                if track.signature > max_signature:
                    max_signature = track.signature

            common_track = Track(signature=max_signature)

            for track in tracks.values():
                for position, note in track:
                    common_track.add(note, position)

            return common_track

        if channel not in tracks:
            raise ValueError(f'No channel {channel} found')

        return tracks[channel]

    def loads(self, data: bytes, channel: Optional[int] = None) -> Track:
        """
        Reads track from the MIDI serialized byte array. MIDI file can contain up to 16 channels.
        If ``channel`` is specified, track from this channel is returned. If ``channel``
        is omitted, track composed of all channels is returned.

        :param data: byte array
        :param channel: channel to read from (default: None)
        :return: parsed track
        """
        with io.BytesIO(data) as f:
            return self.load(f, channel=channel)


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
    return MIDIWriter(bpm=bpm, channel=channel).dumps(track)


def load(file: BinaryIO, channel: Optional[int] = None) -> Track:
    """
    Reads track from the MIDI file. MIDI file can contain up to 16 channels.
    If ``channel`` is specified, track from this channel is returned. If ``channel``
    is omitted, track composed of all channels is returned.

    :param file: binary file-like object
    :param channel: channel to read from (default: None)
    :return: parsed track
    """
    return MIDIReader().load(file, channel=channel)


def loads(data: bytes, channel: Optional[int] = None) -> Track:
    """
    Reads track from the MIDI serialized byte array. MIDI file can contain up to 16 channels.
    If ``channel`` is specified, track from this channel is returned. If ``channel``
    is omitted, track composed of all channels is returned.

    :param data: byte array
    :param channel: channel to read from (default: None)
    :return: parsed track
    """
    return MIDIReader().loads(data, channel=channel)
