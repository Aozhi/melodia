import random

from melodia.core import Track, Note
from melodia.io import midi


def random_track_without_overlaps():
    track = Track(signature=(random.randint(0, 100), 16))

    p = 0
    for _ in range(random.randint(100, 300)):
        note = Note(random.randint(30, 90), (random.randint(0, 100), 16), velocity=1.0)
        p += 200
        track.add(note, (p, 16))

    return track


def test_midi_serialize():
    empty_track = Track(signature=(17, 16))
    assert empty_track == midi.loads(midi.dumps(empty_track))

    one_note_track = Track(signature=(17, 16), content=[(Note(0, (3, 8), 1.0), (7, 16))])
    assert one_note_track == midi.loads(midi.dumps(one_note_track))

    for _ in range(10):
        track = random_track_without_overlaps()
        assert track == midi.loads(midi.dumps(track))
