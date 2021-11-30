import json
import re
import time

import pkg_resources

import pyvisa

SIM_DEVICES = {"ASRL::SIMLED::INSTR": "sim_led.json"}


class ResourceManager(pyvisa.ResourceManager):
    """Fake PyVISA ResourceManager"""

    def __init__(self, backend=None):
        super().__init__()

    def list_resources(self):
        # pyvisa returns a tuple
        resources = list(super().list_resources())
        resources.extend(SIM_DEVICES.keys())
        return tuple(resources)

    def open_resource(self, resource, *args, **kwargs):
        if resource not in SIM_DEVICES.keys():
            return super().open_resource(resource, *args, **kwargs)
        else:
            return SimulatedDevice(SIM_DEVICES[resource])


class SimulatedDevice:
    def __init__(self, datafile):
        with pkg_resources.resource_stream("nsp2visasim", datafile) as f:
            self.data = json.load(f)
        self.setting = 0
        self.idxs = {}

    def query(self, query):
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

        time.sleep(0.002)
        return value