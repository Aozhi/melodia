# Melodia

Melodia is a Python library for working with music.

### Installation

Melodia requires Python 3.6 or greater.

```shell script
pip install melodia
```

### Documentation

### Examples

#### Notes

Note can be defined from its notation and duration.

```python
from melodia.core import Note

n1 = Note('C4', (1, 4))
n2 = Note('A#5', (3, 8))
n3 = Note('Gb-1', (1, 1))
```

#### Notes and tracks


```python
from melodia.core import Note, Track

track = Track(signature=(4, 4))
track.add(Note('C4', (1, 4)))
track.add(Note('C4', (1, 4)))
track.add(Note('C#4', (1, 4)))
track.add(Note('D4', (1, 4)))
track.add(Note('C4', (1, 4)))
track.add(Note('D4', (1, 4)))
track.add(Note('C#4', (1, 4)))
track.add(Note('G3', (1, 2)))
track.add(Note('C4', (1, 2)))
track.add(Note('C4', (1, 1)))
```

#### Writing MIDI
ANy track can be saved as a midi file and then exported to any DAW>

```python
from melodia.io import midi

with open('track.mid', 'wb') as f:
    midi.dump(track, f)
```