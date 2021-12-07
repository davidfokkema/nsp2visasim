import gzip
import json
import re
import time

import pkg_resources

import pyvisa

# mimic errors attribute of pyvisa
from pyvisa import errors


SIM_DEVICES = {"ASRL::SIMLED::INSTR": "sim_led.json.gz"}


class ResourceManager(pyvisa.ResourceManager):
    """Fake PyVISA ResourceManager."""

    def list_resources(self):
        """List VISA resources.

        Returns:
            tuple: A tuple of all connected VISA devices
        """
        # pyvisa returns a tuple
        resources = list(super().list_resources())
        resources.extend(SIM_DEVICES.keys())
        return tuple(resources)

    def open_resource(self, resource, *args, **kwargs):
        """Open a VISA instrument.

        Args:
            resource (str): Name of the VISA resource

        Returns:
            Resource or SimulatedDevice: a VISA Resource or a SimulatedDevice
        """
        if resource not in SIM_DEVICES.keys():
            return super().open_resource(resource, *args, **kwargs)
        else:
            return SimulatedDevice(SIM_DEVICES[resource])


class SimulatedDevice:
    """A simulated VISA Device.

    The simulation is based on actual data. Output voltages are recorded and
    input voltages are played back from the data.
    """

    def __init__(self, datafile):
        """Initialize the simulated device

        Args:
            datafile (str): Name of the file that contains the prerecorded
                experimental data. The file must be included in this package.
        """
        compressed_data = pkg_resources.resource_string("nsp2visasim", datafile)
        self.data = json.loads(gzip.decompress(compressed_data))
        self.setting = 0
        self.idxs = {}
        self.open()

    def open(self):
        """Open the device."""
        self._is_open = True

    def close(self):
        """Close the device."""
        self._is_open = False

    def query(self, query):
        """Write a command to the device and return the response.

        Args:
            query (str): the command to send to the device.

        Returns:
            str: the device's response.
        """
        if not self._is_open:
            raise errors.InvalidSession()

        if re.match("\*IDN\?", query):
            return "Simulated Arduino VISA firmware (LED experiment)"
        elif match := re.match("OUT:CH0 (?P<value>\d+)", query):
            # set output value
            self.setting = int(match["value"])
            return match["value"]
        elif match := re.match("OUT:CH0:VOLT (?P<voltage>\d*\.?\d*|\d+)", query):
            # set output voltage
            voltage = match["voltage"]
            self.setting = int(1023 * float(voltage) / 3.3)
            return voltage
        elif match := re.match("OUT:CH0\?", query):
            # get output value
            return str(self.setting)
        elif match := re.match("OUT:CH0:VOLT\?", query):
            # get output voltage
            return str(self.setting / 1023 * 3.3)
        elif match := re.match("MEAS:CH(?P<channel>\d+)\?", query):
            # get input value
            return self._get_input_value(match["channel"])
        elif match := re.match("MEAS:CH(?P<channel>\d+):VOLT\?", query):
            # get input voltage
            value = int(self._get_input_value(match["channel"]))
            return f"{value / 1023 * 3.3:.4f}"

    def _get_input_value(self, channel):
        """Simulate get value from input channel

        Args:
            channel (str): analog channel number
        """
        ch_idx = f"ch{channel}"
        idx = self.idxs.setdefault(self.setting, {}).setdefault(ch_idx, 0)

        setting_key = str(self.setting)
        try:
            value = self.data[setting_key][ch_idx][idx]
        except IndexError:
            value = self.data[setting_key][ch_idx][0]
            self.idxs[self.setting][ch_idx] = 1
        else:
            self.idxs[self.setting][ch_idx] += 1

        # simulate a slow response
        time.sleep(0.001)
        return value
