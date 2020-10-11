Melodia
=======

.. image:: https://readthedocs.org/projects/melodia/badge/?version=latest
   :target: https://melodia.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
   
.. image:: https://github.com/meownoid/melodia/workflows/tests/badge.svg
   :target: https://github.com/meownoid/melodia/actions
   :alt: Tests Status

Melodia is a Python library for MIDI music creation.

It provides four core concepts – tone, time signature, note and track and various
abstractions built on them, such as chords and chord progressions. Library contains
MIDI writer which allows to output tracks to MIDI files in order to export them to
any DAW.

Installation
------------

Melodia is fully typed and requires Python 3.7 or greater.

.. code-block:: shell

   pip install melodia
    
Documentation
-------------

Documentation is available at `melodia.readthedocs.io <https://melodia.readthedocs.io/>`_.


Example
--------

.. code-block:: python

   from melodia.core.track import Track
   from melodia.music import chord
   from melodia.io import midi

   track = Track(signature=(4, 4))

   track.add(chord.maj('C3', (1, 1)))
   track.add(chord.maj('D3', (1, 1)))
   track.add(chord.min('A3', (1, 1)))
   track.add(chord.maj7('G3', (1, 1)))

   with open('chords.mid', 'wb') as f:
       midi.dump(track, f)

.. image:: https://storage.yandexcloud.net/meownoid-pro-static/external/github/melodia/ableton-chords.png
   :alt: Ableton Live 10 with imported chords
