import gzip
import importlib.resources
import json
import re
import time

import pyvisa

# mimic errors attribute of pyvisa
from pyvisa import errors

SIM_DEVICES = {
    "ASRL::SIMLED::INSTR": ("LED experiment", "sim_led.json.gz"),
    "ASRL::SIMPV::INSTR": ("photovoltaic cell", "sim_pv.json.gz"),
    "ASRL::SIMPV_BRIGHT::INSTR": (
        "photovoltaic cell under bright light",
        "sim_pv_bright.json.gz",
    ),
}


class ResourceManager(pyvisa.ResourceManager):
    """Fake PyVISA ResourceManager."""

    def list_resources(self, query="?*::INSTR"):
        """List VISA resources.

        Returns a tuple of connected devices matching query. The default query
        matches all devices.

        Args:
            query (str, optional): A VISA Resource Regular expression. Device
                names must match this query. Defaults to "?*::INSTR".

        Returns:
            tuple: A tuple of all connected VISA devices
        """
        # pyvisa returns a tuple
        resources = list(super().list_resources(query))

        # translate Resource Regular Expression -> Python regex
        pattern = query.replace("?", ".")
        # find matching simulated devices
        sim_devices = SIM_DEVICES.keys()
        for device in sim_devices:
            if re.match(pattern, device):
                resources.append(device)

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
            return SimulatedDevice(*SIM_DEVICES[resource])


class SimulatedDevice:
    """A simulated VISA Device.

    The simulation is based on actual data. Output voltages are recorded and
    input voltages are played back from the data.
    """

    def __init__(self, description, datafile):
        """Initialize the simulated device

        Args:
            description (str): Short description of the simulation which will be
                included in the info string.
            datafile (str): Name of the file that contains the prerecorded
                experimental data. The file must be included in this package.
        """
        self.description = description
        compressed_data = (
            importlib.resources.files("nsp2visasim") / datafile
        ).read_bytes()
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

        if re.match(r"\*IDN\?", query):
            return f"Simulated Arduino VISA firmware ({self.description})"
        elif match := re.match(r"OUT:CH0 (?P<value>\d+)", query):
            # set output value
            self.setting = int(match["value"])
            return match["value"]
        elif match := re.match(r"OUT:CH0:VOLT (?P<voltage>\d*\.?\d*|\d+)", query):
            # set output voltage
            voltage = match["voltage"]
            self.setting = int(1023 * float(voltage) / 3.3)
            return voltage
        elif match := re.match(r"OUT:CH0\?", query):
            # get output value
            return str(self.setting)
        elif match := re.match(r"OUT:CH0:VOLT\?", query):
            # get output voltage
            return str(self.setting / 1023 * 3.3)
        elif match := re.match(r"MEAS:CH(?P<channel>\d+)\?", query):
            # get input value
            return self._get_input_value(match["channel"])
        elif match := re.match(r"MEAS:CH(?P<channel>\d+):VOLT\?", query):
            # get input voltage
            value = int(self._get_input_value(match["channel"]))
            return f"{value / 1023 * 3.3:.4f}"

    def _get_input_value(self, channel):
        """Simulate measure value from input channel.

        The simulated measurement is retrieved from a prerecorded dataset from
        an actual device. Data was recorded for each output voltage setting, on
        all relevant channels, and performed multiple times. So this simulation
        still works if you want to repeat single measurements; new data is
        returned for each measurement. Data repeats after all recorded data is
        exhausted. This means that this method will keep track of what values it
        has already returned.

        Args:
            channel (str): analog channel number
        """
        ch_idx = f"ch{channel}"
        # self.idxs keeps track of which new data to return for a specific
        # setting and a specific channel
        idx = self.idxs.setdefault(self.setting, {}).setdefault(ch_idx, 0)

        # the output voltage wraps after 1023
        setting_key = str(self.setting % 1024)
        try:
            # retrieve new data for the setting and channel, idx keeps track of
            # which 'new' value to retrieve
            value = self.data[setting_key][ch_idx][idx]
        except IndexError:
            # all recorded data has been exhausted, start from the beginning
            value = self.data[setting_key][ch_idx][0]
            self.idxs[self.setting][ch_idx] = 1
        else:
            # increment the index to keep the data fresh
            self.idxs[self.setting][ch_idx] += 1

        # simulate a slow response
        time.sleep(0.001)
        return value
