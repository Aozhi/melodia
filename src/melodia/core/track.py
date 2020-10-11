import heapq
from typing import Iterable, Tuple, Union, List, Optional

from melodia.core.note import Note
from melodia.core.signature import Signature


class Track:
    """
    Track represents collection of notes where each note has its position.
    Two or more notes with different tones can share same position.
    """
    __slots__ = (
        '_signature',
        '_max_denominator',
        '_max_position',
        '_heap',
        '_sorted'
    )

    def __init__(
            self,
            signature: Union[Signature, Tuple[int, int]] = Signature(4, 4),
            content: Optional[Iterable[Tuple[Note, Union[Signature, Tuple[int, int], None]]]] = None,
    ):
        """
        Initializes Track object.

        :param signature: time signature of the track (default: (4, 4))
        :param content: optional content of the track as a list of pairs (note, position) (default: None)
        """
        self._signature: Signature
        if isinstance(signature, Signature):
            self._signature = signature
        elif isinstance(signature, Iterable):
            self._signature = Signature(*signature)
        else:
            raise TypeError('signature must be a Signature object or a pair of integers')

        self._max_denominator = 1
        self._heap: List[Tuple[Signature, Note]] = []
        self._max_position: Signature = Signature(0, 1)

        self._sorted = True

        if content is not None:
            for note, position in content:
                self.add(note, where=position)

    @property
    def signature(self) -> Signature:
        """
        Returns time signature of the track.

        :return: time signature of the track
        """
        return self._signature

    @property
    def length(self) -> Signature:
        """
        Returns length of the track.
        Length of the track is defined as the position after which
        no note will be played. In other words it is the right-most ending of the note.

        :return: length of the track
        """
        return self._max_position

    def add(
            self,
            what: Union[Note, Iterable[Note]],
            where: Union[Signature, Tuple[int, int], None] = None
    ) -> None:
        """
        Adds note or multiple notes to the track to the specified position.
        In the case of the multiple notes, all the notes will be placed in the same position.
        If position is not specified, note or notes will be placed at the end of the track
        (after the right-most ending of the note).

        :param what: one note or iterable of notes
        :param where: position where note or multiple notes will be placed (default: None)
        :return: None
        """
        position: Signature
        if where is None:
            position = self._max_position
        elif isinstance(where, Signature):
            position = where
        elif isinstance(where, Iterable):
            position = Signature(*where)
        else:
            raise TypeError('where must be a Signature object or a pair of integers')

        if isinstance(what, Iterable):
            for x in what:
                self.add(what=x, where=position)
            return

        note: Note = what

        if position.denominator > self._max_denominator:
            self._max_denominator = position.denominator
            self._heap = [(s.to(self._max_denominator), n) for s, n in self._heap]

        position_transformed = position.to(self._max_denominator)

        heapq.heappush(self._heap, (position_transformed, note))
        self._sorted = False

        end_position = position_transformed + note.duration
        if end_position > self._max_position:
            self._max_position = end_position

    def __eq__(self, other: 'Track') -> bool:
        """
        Compares two tracks for equality. Tracks are equal if their signatures and contents are equal.

        :param other: other track
        :return: True if tracks are equal, False otherwise
        """

        if self._signature != other._signature:
            return False

        for (ap, an), (bp, bn) in zip(self, other):
            if an != bn or ap != bp:
                return False

        return True


    def __iter__(self) -> Iterable[Tuple[Signature, Note]]:
        """
        Returns track iterator. Iterator yields pairs (position, note) in order of ascending positions.
        Position is the Signature object and note is the Note object.

        :return: iterator of (position, note) pairs
        """
        if not self._sorted:
            self._heap.sort()
            self._sorted = True

        return iter(self._heap)

    def __str__(self) -> str:
        """
        Returns human-readable string representation of the track.

        :return: human-readable string representation of the track
        """
        return f'Track {str(self._signature)} with {len(self._heap)} notes'

    def __repr__(self) -> str:
        """
        Returns string representation of the track.

        :return: string representation of the track
        """
        name = self.__class__.__name__
        signature = f'({self._signature.nominator}, {self._signature.denominator})'

        contents = []
        for position, note in self:
            contents.append(f'({repr(note)}, ({position.nominator}, {position.denominator}))')

        return f'{name}(signature={signature}, content=[{", ".join(contents)}])'
