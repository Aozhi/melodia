Tone
====

Tone is the smallest building block of the library which encapsulates pitch from the chromatic scale.
Pitch can be expressed as an integer from minus infinity to plus infinity where 0
corresponds to the C0 (16.351597831287414 Hz).

.. code-block:: python

   Tone(0)

To construct tone from notation one can use :func:`~melodia.core.tone.Tone.from_notation` method.
Pitch name must be uppercase.

.. code-block:: python

   Tone.from_notation('C0')

Sharp (#) and flat (b) symbols are supported. Octave number can be positive or negative.

.. code-block:: python

   Tone.from_notation('B#3')

.. code-block:: python

   Tone.from_notation('Ab-1')

Any number of sharps and flats can be used.

.. code-block:: python

   Tone.from_notation('E#b##bb#10')

:func:`~melodia.core.tone.Tone.to_notation` performs opposite translation.

.. code-block:: python

   Tone(40).to_notation()
   # 'E3'

.. code-block:: python

   Tone.from_notation('Ab3').to_notation()
   # 'G#3'

.. code-block:: python

   Tone.from_notation('E#b##bb#10').to_notation()
   # 'F10'

If you want to transpose down, use ``transpose_down=True``.

.. code-block:: python

   Tone.from_notation('Ab3').to_notation(transpose_down=True)
   # 'Ab3'

:func:`~melodia.core.tone.Tone.to_frequency` translates tone to frequency in Hz.

.. code-block:: python

   Tone.from_notation('A4').to_frequency()
   # 440.0

.. code-block:: python

   Tone.from_notation('C1').to_frequency()
   # 32.70319566257483

Tones can be compared.

.. code-block:: python

   Tone.from_notation('C1') < Tone.from_notation('C#1')
   # True
