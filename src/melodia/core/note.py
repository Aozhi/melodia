from typing import Tuple, Union, Iterable

from melodia.core.sgnature import Signature
from melodia.core.tone import Tone


class Note:
    __slots__ = ('_tone', '_velocity', '_duration')

    def __init__(
            self,
            tone: Union[Tone, int, str],
            duration: Union[Signature, Tuple[int, int]] = Signature(1, 1),
            velocity: float = 0.9
    ):
        self._tone: Tone
        if isinstance(tone, Tone):
            self._tone = tone
        elif isinstance(tone, int):
            self._tone = Tone(tone)
        elif isinstance(tone, str):
            self._tone = Tone.from_notation(tone)
        else:
            raise ValueError('tone must be a Tone object, an integer or a string')

        self._duration: Signature
        if isinstance(duration, Signature):
            self._duration = duration
        elif isinstance(duration, Iterable):
            self._duration = Signature(*duration)
        else:
            raise ValueError('duration must be a Signature object or a pair of integers')

        if not 0.0 <= velocity <= 1.0:
            raise ValueError('velocity must be in range [0.0, 1.0]')

        self._velocity: float = velocity

    @property
    def tone(self) -> Tone:
        return self._tone

    @property
    def velocity(self) -> float:
        return self._velocity

    @property
    def duration(self) -> Signature:
        return self._duration

    def transposed(self, transposition: int) -> 'Note':
        return Note(
            tone=self._tone.transposed(transposition),
            velocity=self._velocity,
            duration=self._duration
        )

    def _as_triplet(self) -> Tuple[Tone, Signature, float]:
        return self._tone, self._duration, self._velocity

    def __repr__(self) -> str:
        name = self.__class__.__name__
        pitch = self._tone.pitch
        velocity = self._velocity
        duration = f'({self._duration.nominator}, {self._duration.denominator})'

        return f'{name}(tone={pitch}, duration={duration}, velocity={velocity}) '

    def __str__(self) -> str:
        return f'Note {str(self._duration)} {str(self._tone)} ({self._velocity:.3f})'

    def __eq__(self, other: 'Note') -> bool:
        return self._as_triplet() == other._as_triplet()

    def __le__(self, other: 'Note') -> bool:
        return self._as_triplet() <= other._as_triplet()

    def __lt__(self, other: 'Note') -> bool:
        return self._as_triplet() < other._as_triplet()

    def __ge__(self, other: 'Note') -> bool:
        return self._as_triplet() >= other._as_triplet()

    def __gt__(self, other: 'Note') -> bool:
        return self._as_triplet() > other._as_triplet()
