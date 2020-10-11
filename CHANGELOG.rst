Changelog
=========

1.2 - Unreleased
----------------

Added
#####

- New module ``melodia.processing`` which should contain algorithms of track processing
- New function ``melodia.processing.track.randomize_velocities``
- New method ``Note.with_duration``
- New method ``Note.with_velocity``
- New method ``Track.__len__`` which returns number of notes in the track

Fixed
#######

- Fixed chord docstrings

1.1 - 11.10.2020
----------------

Added
#####

- MIDI reader capable of reading files written by melodia MIDI writer: ``melodia.io.midi.MIDIWriter``
- Methods ``load`` and ``loads`` in ``melodia.io.midi``
- Chords module: ``melodia.music.chord``
- Tests for MIDI writer
- Tests for MIDI reader
- Documentation for Tone class

Changed
#######

- Fixed typo in the internal package name: ``melodia.core.sgnature`` to ``melodia.core.signature``

1.0 - 06.10.2020
----------------

Added
#####

- Tone class: ``melodia.core.Tone``
- Signature class: ``melodia.core.Signature``
- Note class: ``melodia.core.Note``
- Track class: ``melodia.core.Track``
- MIDI writer: ``melodia.io.midi.MIDIWriter``
