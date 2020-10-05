import heapq
from typing import Iterable, Tuple, Union, List, Optional

from melodia.core.note import Note
from melodia.core.sgnature import Signature


class Track:
    __slots__ = (
        '_signature',
        '_min_denominator',
        '_max_position',
        '_heap'
    )

    def __init__(
            self,
            signature: Union[Signature, Tuple[int, int]] = Signature(4, 4),
            content: Optional[Iterable[Tuple[Note, Union[Signature, Tuple[int, int], None]]]] = None,
    ):
        self._signature: Signature
        if isinstance(signature, Signature):
            self._signature = signature
        elif isinstance(signature, Iterable):
            self._signature = Signature(*signature)
        else:
            raise TypeError('signature must be a Signature object or a pair of integers')

        self._min_denominator = 1
        self._heap: List[Tuple[Signature, Note]] = []
        self._max_position: Signature = Signature(0, 1)

        if content is not None:
            for note, position in content:
                self.add(note, where=position)

    @property
    def signature(self) -> Signature:
        return self._signature

    def add(
            self,
            what: Union[Note, Iterable[Note]],
            where: Union[Signature, Tuple[int, int], None] = None
    ) -> None:
        if isinstance(what, Iterable):
            for x in what:
                self.add(x, where)
            return

        note: Note = what

        position: Signature
        if where is None:
            position = self._max_position
        elif isinstance(where, Signature):
            position = where
        elif isinstance(where, Iterable):
            position = Signature(*where)
        else:
            raise TypeError('where must be a Signature object or a pair of integers')

        # Condition is reversed since it is a denominator
        if position.denominator > self._min_denominator:
            self._min_denominator = position.denominator
            self._heap = [(s.to(self._min_denominator), n) for s, n in self._heap]

        position_transformed = position.to(self._min_denominator)

        heapq.heappush(self._heap, (position_transformed, note))

        end_position = position_transformed + note.duration
        if end_position > self._max_position:
            self._max_position = end_position

    def __iter__(self) -> Iterable[Tuple[Signature, Note]]:
        return iter(sorted(self._heap))

    def __repr__(self) -> str:
        name = self.__class__.__name__
        signature = f'({self._signature.nominator}, {self._signature.denominator})'

        contents = []
        for position, note in self:
            contents.append(f'({repr(note)}, ({position.nominator}, {position.denominator}))')

        return f'{name}(signature={signature}, content=[{", ".join(contents)}])'

    def __str__(self) -> str:
        return f'Track {str(self._signature)} with {len(self._heap)} notes'
