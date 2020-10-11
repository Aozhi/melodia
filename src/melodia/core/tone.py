import re
from typing import Dict

_notation_regex = re.compile(r'(?P<tone>[ABCDEFG])(?P<transposition>[#b]*)(?P<octave>-?\d+)?')
_tone_mapping: Dict[str, int] = {
    'C': 0,
    'D': 2,
    'E': 4,
    'F': 5,
    'G': 7,
    'A': 9,
    'B': 11
}
_reverse_tone_mapping: Dict[int, str] = {v: k for k, v in _tone_mapping.items()}


class Tone:
    """
    Tone represents pitch from chromatic scale.
    """
    __slots__ = ('_pitch',)

    def __init__(self, pitch: int):
        """
        Initializes Tone object. Takes pitch as only argument.
        Pitch must be an integer number corresponding to tone number in chromatic scale.
        For example, C0 is 0, C#0 is 1, D0 is 2, C1 is 12, A4 is 57.

        >>> Tone(0).to_notation()
        'C0'

        >>> Tone(1).to_notation()
        'C#0'

        >>> Tone(57).to_notation()
        'A4'

        If you want to initialize tone from notation (for example from string 'Db3'), use
        `Tone.from_notation` instead.

        :param pitch: any integer number corresponding to tone number in chromatic scale
        """
        if not isinstance(pitch, int):
            raise ValueError('Pitch must be an integer, to construct tone from notation use Tone.from_notation')

        self._pitch = pitch

    @property
    def pitch(self) -> int:
        """
        Returns pitch of the tone.

        :return: pitch of the tone
        """
        return self._pitch

    @property
    def octave(self) -> int:
        """
        Returns octave of the tone.

        >>> Tone.from_notation('C5').octave
        5

        >>> Tone.from_notation('F-2').octave
        -2

        :return: octave of the tone
        """

        return self._pitch // 12

    @classmethod
    def from_notation(cls, notation: str) -> 'Tone':
        """
        Parses tone from notation. Multiple transposition characters ('#' or 'b') are allowed.
        Tone name should be uppercase to avoid ambiguity. Octave number can be negative.
        Raises ValueError if notation can not be parsed.

        >>> Tone.from_notation('C')
        Tone(pitch=0)

        >>> Tone.from_notation('A4')
        Tone(pitch=57)

        >>> Tone.from_notation('Db3')
        Tone(pitch=37)

        >>> Tone.from_notation('G#5')
        Tone(pitch=68)

        >>> Tone.from_notation('G#b#bb#5')
        Tone(pitch=67)

        :param notation: notation string
        :return: Tone with pitch derived from notation
        """
        match = _notation_regex.match(notation)

        if match is None:
            raise ValueError('Invalid notation')

        base_pitch = _tone_mapping[match.group('tone')]
        transposition = sum(+1 if t == '#' else -1 for t in match.group('transposition'))
        octave_raw = match.group('octave')
        octave = int(octave_raw) if octave_raw else 0

        return cls(12 * octave + base_pitch + transposition)

    def to_notation(self, transpose_down: bool = False) -> str:
        """
        Formats tone to notation.

        >>> Tone(0).to_notation()
        'C0'

        >>> Tone(13).to_notation()
        'C#1'

        >>> Tone(13).to_notation(transpose_down=True)
        'Db1'

        >>> Tone(113).to_notation()
        'F9'

        >>> Tone(113).to_notation(transpose_down=True)
        'F9'

        :param transpose_down: transpose tones down with flat symbol ('b')
        instead of transposing up with sharp symbol ('#')
        :return: tone notation
        """
        base_pitch = self._pitch % 12
        octave = self._pitch // 12
        if base_pitch in _reverse_tone_mapping:
            tone = _reverse_tone_mapping[base_pitch]
            transposition = ''
        else:
            if transpose_down:
                tone = _reverse_tone_mapping[base_pitch + 1]
                transposition = 'b'
            else:
                tone = _reverse_tone_mapping[base_pitch - 1]
                transposition = '#'

        return f'{tone:s}{transposition:s}{octave:d}'

    def to_frequency(self, base: float = 440.0) -> float:
        """
        Returns frequency of the tone based on the frequency of the A4 tone.

        :param base: frequency of the base tone (A4) in Hz (default: 440.0)
        :return: frequency of the tone in Hz
        """

        return base * 2 ** ((self._pitch - 57) / 12)

    def transposed(self, transposition: int) -> 'Tone':
        """
        Returns transposed copy of the tone.

        >>> Tone.from_notation('C4').transposed(1).to_notation()
        'C#4'

        >>> Tone.from_notation('C4').transposed(2).to_notation()
        'D4'

        >>> Tone.from_notation('C4').transposed(-1).to_notation()
        'B3'

        >>> Tone.from_notation('C4').transposed(-2).to_notation()
        'A#3'

        :param transposition: integer number of semitones to transpose tone
        :return: transposed copy of the tone
        """

        return Tone(pitch=self._pitch + transposition)

    def __str__(self) -> str:
        """
        Returns human-readable string representation of the tone.

        :return: string interpretation of the tone
        """
        return self.to_notation()

    def __repr__(self) -> str:
        """
        Returns string representation of the tone.

        :return: string representation of the tone
        """
        return f'{self.__class__.__name__}(pitch={self._pitch})'

    def __eq__(self, other: 'Tone') -> bool:
        """
        Compares two tones for equality. Tones are equal if their pitches are equal.

        :param other: other tone
        :return: True of tones have equal pitches, False otherwise
        """
        return self._pitch == other._pitch

    def __le__(self, other: 'Tone') -> bool:
        """
        Compares two tones by their pitches.

        :param other: other tone
        :return: True if this pitch tone is less or equal than other tone pitch, False otherwise
        """
        return self._pitch <= other._pitch

    def __lt__(self, other: 'Tone') -> bool:
        """
        Compares two tones by their pitches.

        :param other: other tone
        :return: True if this pitch tone is less than other tone pitch, False otherwise
        """
        return self._pitch < other._pitch

    def __ge__(self, other: 'Tone') -> bool:
        """
        Compares two tones by their pitches.

        :param other: other tone
        :return: True if this pitch tone is greater or equal than other tone pitch, False otherwise
        """
        return self._pitch >= other._pitch

    def __gt__(self, other: 'Tone') -> bool:
        """
        Compares two tones by their pitches.

        :param other: other tone
        :return: True if this pitch tone is greater than other tone pitch, False otherwise
        """
        return self._pitch > other._pitch
