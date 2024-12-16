# nsp2visasim

This package contains a simulation of an Arduino VISA device connected to a small circuit to measure the voltage versus current characteristics of a LED. It is created for a [programming course](https://natuurkundepracticumamsterdam.github.io/ecpc/) in the physics and astronomy joint degree bachelor programme at the Vrije Universiteit and the University of Amsterdam. Students use the actual device and circuit while on campus. This package simulates [this firmware](https://github.com/davidfokkema/arduino-visa-firmware).


## Usage

In your controller code, replace:

```python
import pyvisa
```

with:

```python
try:
      from nsp2visasim import sim_pyvisa as pyvisa
except ModuleNotFoundError:
      import pyvisa
```

Then, if you use Poetry, add it to your existing project with:

```console
poetry add --group dev nsp2visasim
```

If you don't use Poetry, install `nsp2visasim` with:

```console
pip install nsp2visasim
```

You now appear to have an additional VISA device connected to your system. If an
actual Arduino is attached, you can choose to open the simulation or the actual
Arduino by selecting the correct port name. Your code should work exactly the
same as before.

A session might look like this:

```console
$ diode list                               
The following devices are connected to your computer:

ASRL/dev/cu.URT1::INSTR
ASRL/dev/cu.URT2::INSTR
ASRL/dev/cu.Bluetooth-Incoming-Port::INSTR
ASRL/dev/cu.usbmodem14501::INSTR
ASRL::SIMLED::INSTR

$ diode info SIMLED
Device identification: Simulated Arduino VISA firmware (LED experiment)

$ diode measure SIMLED -v 2.5 -n 10
Measured current through diode: 3.048 +- 0.030 mA @ 1.805 +- 0.011 V.
```