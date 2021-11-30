nsp2visasim
===========

This package contains a simulation of an Arduino VISA device connected to a
small circuit to measure the voltage versus current characteristics of a LED. It
is created for a programming course in the physics and astronomy joint degree
bachelor programme at the Vrije Universiteit and the University of Amsterdam.
Students use the actual device and circuit while on campus but can use this
simulation to finish up their work at home.


Usage
-----

In your controller code, replace:

.. code-block:: python

   import pyvisa

with:

.. code-block:: python

   try:
       from nsp2visasim import sim_pyvisa as pyvisa
   except ModuleNotFoundError:
       import pyvisa


Then, if you use Poetry, add it to your existing project with:

.. code-block:: console

   $ poetry add --dev nsp2visasim

If you don't use Poetry, install ``nsp2visasim`` with:

.. code-block:: console

   $ pip install nsp2visasim

You now appear to have an additional VISA device connected to your system. If an
actual Arduino is attached, you can choose to open the simulation or the actual
Arduino by selecting the correct port name. Your code should work exactly the
same as before.
