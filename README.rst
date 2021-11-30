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
        