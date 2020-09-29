import re
from typing import Dict

_notation_regex = re.compile(r'(?P<note>[ABCDEFG])(?P<transposition>[#b]*)(?P<octave>-?\d+)?')
_note_mapping: Dict[str, int] = {
    'C': 0,
    'D': 2,
    'E': 4,
    'F': 5,
    'G': 7,
    'A': 9,
    'B': 11
}
_reverse_note_mapping: Dict[int, str] = {v: k for k, v in _note_mapping.items()}


class Note:
    """
    Note represents sound of some pitch from chromatic scale
    and some velocity which correlates with the note loudness.
    """
    __slots__ = ('_pitch', '_velocity')

    def __init__(self, pitch: int, velocity: float = 1.0):
        """
        Initialize Note object. Takes two arguments: pitch and velocity.
        Pitch must be an integer number corresponding to note number in chromatic scale.
        For example, C0 is 0, C#0 is 1, D0 is 2, C1 is 12, A4 is 57.

        >>> Note(0).to_notation()
        'C0'

        >>> Note(1).to_notation()
        'C#0'

        >>> Note(57).to_notation()
        'A4'

        If you want to initialize note from notation (for example from string 'Db3'), use
        `Note.from_notation` instead.

        Velocity must be a real number in range [0.0, 1.0] where 0.0 is the minimun velocity and
        1.0 is the maximum velocity. By default velocity is 1.0.

        :param pitch: any integer number corresponding to note number in chromatic scale
        :param velocity: real number in range [0.0, 1.0] (default: 1.0)
        """
        if not 0.0 <= velocity <= 1.0:
            raise ValueError('Velocity must be a float in range [0.0, 1.0]')

        self._pitch = pitch
        self._velocity = velocity

    @property
    def pitch(self) -> int:
        """
        Returns pitch of the note.

        :return: pitch of the note
        """
        return self._pitch

    @property
    def velocity(self) -> float:
        """
        Returns velocity of the note.

        :return: velocity of the note
        """
        return self._velocity

    @property
    def octave(self) -> int:
        """
        Returns octave of the note.

        >>> Note.from_notation('C5').octave
        5

        >>> Note.from_notation('F-2').octave
        -2

        :return: octave of the note
        """

        return self._pitch // 12

    @classmethod
    def from_notation(cls, notation: str, velocity: float = 1.0) -> 'Note':
        """
        Parses note from notation. Multiple transposition characters ('#' or 'b') are allowed.
        Note name should be uppercase to avoid ambiguity. Octave number can be negative.
        Raises ValueError if notation can not be parsed.

        >>> Note.from_notation('C')
        Note(pitch=0, velocity=1.0)

        >>> Note.from_notation('A4')
        Note(pitch=57, velocity=1.0)

        >>> Note.from_notation('Db3')
        Note(pitch=37, velocity=1.0)

        >>> Note.from_notation('G#5')
        Note(pitch=68, velocity=1.0)

        >>> Note.from_notation('G#b#bb#5')
        Note(pitch=67, velocity=1.0)

        :param notation: notation string
        :param velocity: real number in range [0.0, 1.0] (default: 1.0)
        :return: Note with pitch derived from notation and specified velocity
        """
        match = _notation_regex.match(notation)

        if match is None:
            raise ValueError('Invalid notation')

        base_pitch = _note_mapping[match.group('note')]
        transposition = sum(+1 if t == '#' else -1 for t in match.group('transposition'))
        octave_raw = match.group('octave')
        octave = int(octave_raw) if octave_raw else 0

        pitch: int = 12 * octave + base_pitch + transposition

        return cls(pitch, velocity)

    def to_notation(self, transpose_down: bool = False) -> str:
        """
        Formats note to notation.

        >>> Note(0).to_notation()
        'C0'

        >>> Note(13).to_notation()
        'C#1'

        >>> Note(13).to_notation(transpose_down=True)
        'Db1'

        >>> Note(113).to_notation()
        'F9'

        >>> Note(113).to_notation(transpose_down=True)
        'F9'

        :param transpose_down: transpose notes down with flat ('b') instead of transposing up with sharp ('#')
        :return: note notation
        """
        base_pitch = self._pitch % 12
        octave = self._pitch // 12
        if base_pitch in _reverse_note_mapping:
            note = _reverse_note_mapping[base_pitch]
            transposition = ''
        else:
            if transpose_down:
                note = _reverse_note_mapping[base_pitch + 1]
                transposition = 'b'
            else:
                note = _reverse_note_mapping[base_pitch - 1]
                transposition = '#'

        return f'{note:s}{transposition:s}{octave:d}'

    def to_frequency(self, base: float = 440.0) -> float:
        """
        Returns frequency of the note based on the frequency of the A4 note.

        :param base: frequency of the base note (A4) in Hz (default: 440.0)
        :return: frequency of the note in Hz
        """

        return base * 2 ** ((self._pitch - 57) / 12)

    def with_velocity(self, velocity: float) -> 'Note':
        """
        Returns copy of the current note with specified velocity.

        :param velocity: real number in range [0.0, 1.0]
        :return: copy of the current note with specified velocity
        """
        return Note(pitch=self._pitch, velocity=velocity)

    def transposed(self, transposition: int) -> 'Note':
        """
        Returns transposed copy of the note.

        >>> Note.from_notation('C4').transposed(1).to_notation()
        'C#4'

        >>> Note.from_notation('C4').transposed(2).to_notation()
        'D4'

        >>> Note.from_notation('C4').transposed(-1).to_notation()
        'B3'

        >>> Note.from_notation('C4').transposed(-2).to_notation()
        'A#3'

        :param transposition: integer number of semitones to transpose note
        :return: transposed copy of the note
        """

        return Note(pitch=self._pitch + transposition, velocity=self._velocity)

    def __str__(self) -> str:
        return self.to_notation()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(pitch={self._pitch}, velocity={self._velocity})'

    def __eq__(self, other: 'Note') -> bool:
        return self._pitch == other._pitch and self._velocity == other._velocity
