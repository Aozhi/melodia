from typing import Tuple, Union, Iterable

from melodia.core.signature import Signature
from melodia.core.tone import Tone


class Note:
    """
    Note represents musical note with three main characteristics: tone, velocity and duration.
    """
    __slots__ = ('_tone', '_velocity', '_duration')

    def __init__(
            self,
            tone: Union[Tone, int, str],
            duration: Union[Signature, Tuple[int, int]] = Signature(1, 4),
            velocity: float = 0.75
    ):
        """
        Initializes Note object. Tone can be a Tone object, an integer or a string.
        In the case of an integer, Tone constructor is called.
        In the case of a string, Tone.from_notation is called.
        Duration can be a Signature object or a pair of integers.
        In the case of a pair of integers Signature constructor is called.
        Velocity must be a float in the range [0.0, 1.0] where 0.0 is the minimum velocity and
        1.0 is the maximum velocity. By default velocity is 0.75 (as in many DAWs).

        :param tone: tone of the note, must be Tone object, integer or string
        :param duration: duration of the note, must be Signature or pair of integers (default: (1, 4))
        :param velocity: float number in the range [0.0, 1.0] (default: 0.75)
        """
        self._tone: Tone
        if isinstance(tone, Tone):
            self._tone = tone
        elif isinstance(tone, int):
            self._tone = Tone(tone)
        elif isinstance(tone, str):
            self._tone = Tone.from_notation(tone)
        else:
            raise TypeError('tone must be a Tone object, an integer or a string')

        self._duration: Signature
        if isinstance(duration, Signature):
            self._duration = duration
        elif isinstance(duration, Iterable):
            self._duration = Signature(*duration)
        else:
            raise TypeError('duration must be a Signature object or a pair of integers')

        if not 0.0 <= velocity <= 1.0:
            raise ValueError('velocity must be in range [0.0, 1.0]')

        self._velocity: float = velocity

    @property
    def tone(self) -> Tone:
        """
        Returns tone of the note.

        :return: tone of the note
        """
        return self._tone

    @property
    def velocity(self) -> float:
        """
        Returns velocity of the note.

        :return: velocity of the note.
        """
        return self._velocity

    @property
    def duration(self) -> Signature:
        """
        Returns duration of the note.

        :return: duration of the note
        """
        return self._duration

    def transposed(self, transposition: int) -> 'Note':
        """
        Returns note with transposed tone. Velocity and duration remains the same.

        :param transposition: integer number of semitones to transpose tone
        :return: note with transposed tone
        """
        return Note(
            tone=self._tone.transposed(transposition),
            velocity=self._velocity,
            duration=self._duration
        )

    def _as_triplet(self) -> Tuple[Tone, Signature, float]:
        return self._tone, self._duration, self._velocity

    def __str__(self) -> str:
        """
        Returns human-readable representation of the note.

        :return: human-readable representation of the note
        """
        return f'Note {str(self._duration)} {str(self._tone)} ({self._velocity:.3f})'

    def __repr__(self) -> str:
        """
        Returns string representation of the note.

        :return: string representation of the note
        """
        name = self.__class__.__name__
        pitch = self._tone.pitch
        velocity = self._velocity
        duration = f'({self._duration.nominator}, {self._duration.denominator})'

        return f'{name}(tone={pitch}, duration={duration}, velocity={velocity}) '

    def __eq__(self, other: 'Note') -> bool:
        """
        Compares two notes for equality. Notes are equal if all their components are equal.

        :param other: other note
        :return: True if notes are equal, False otherwise
        """
        return self._as_triplet() == other._as_triplet()

    def __le__(self, other: 'Note') -> bool:
        """
        Compares two notes. Notes are compared as triplets (pitch, duration, velocity).

        :param other: other note
        :return: True if this note is less or equal than other note, False otherwise
        """
        return self._as_triplet() <= other._as_triplet()

    def __lt__(self, other: 'Note') -> bool:
        """
        Compares two notes. Notes are compared as triplets (pitch, duration, velocity).

        :param other: other note
        :return: True if this note is less than other note, False otherwise
        """
        return self._as_triplet() < other._as_triplet()

    def __ge__(self, other: 'Note') -> bool:
        """
        Compares two notes. Notes are compared as triplets (pitch, duration, velocity).

        :param other: other note
        :return: True if this note is greater or equal than other note, False otherwise
        """
        return self._as_triplet() >= other._as_triplet()

    def __gt__(self, other: 'Note') -> bool:
        """
        Compares two notes. Notes are compared as triplets (pitch, duration, velocity).

        :param other: other note
        :return: True if this note is greater than other note, False otherwise
        """
        return self._as_triplet() > other._as_triplet()
