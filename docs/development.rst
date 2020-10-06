Development
===========

Running tests
-------------

.. code-block:: shell

   PYTHONPATH=src pytest

Building documentation
----------------------

.. code-block:: shell

   cd docs
   make apidoc
   make html

Installing locally
------------------

.. code-block:: shell

   python setup.py install

Building packages
-----------------
.. code-block:: shell

   python setup.py sdist bdist_wheel
