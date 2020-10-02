from typing import Tuple, Union

from melodia.core.tone import Tone


class Note:
    __slots__ = ('_tone', '_velocity', '_signature')

    def __init__(
            self,
            tone: Union[Tone, int, str],
            velocity: float,
            signature: Tuple[int, int]
    ):
        if isinstance(tone, Tone):
            self._tone = tone
        elif isinstance(tone, int):
            self._tone = Tone(tone)
        elif isinstance(tone, str):
            self._tone = Tone.from_notation(tone)
        else:
            raise ValueError('tone must be Tone object, integer or string')

        if not 0.0 <= velocity <= 1.0:
            raise ValueError('velocity must be in range [0.0, 1.0]')

        self._velocity = velocity

        if not signature[0] > 0 or not signature[1] > 0:
            raise ValueError('signature must be a pair of positive integers')

        self._signature = signature

    @property
    def tone(self) -> Tone:
        return self._tone

    @property
    def velocity(self) -> float:
        return self._velocity

    @property
    def signature(self) -> Tuple[int, int]:
        return self._signature

    def transposed(self, transposition: int) -> 'Note':
        return Note(
            tone=self._tone.transposed(transposition),
            velocity=self._velocity,
            signature=self._signature
        )

    def __repr__(self):
        name = self.__class__.__name__
        pitch = self._tone.pitch
        velocity = self._velocity
        signature = f'({self._signature[0]}, {self._signature[1]})'

        return f'{name}(tone={pitch}, velocity={velocity}, signature={signature}) '

    def __str__(self):
        signature = f'{self._signature[0]}/{self._signature[1]}'

        return f'{signature} {self._tone.to_notation()} ({self._velocity:.3f})'
