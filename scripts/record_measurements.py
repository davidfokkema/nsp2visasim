import gzip
import json

from rich.progress import track

from pythondaq.models.diode_experiment import search_device
from pythondaq.controllers.arduino_device import ArduinoVISADevice


DEVICE = "usbmodem"
FILENAME = "measurements.json.gz"
N = 100


def main():
    port = search_device(DEVICE)
    device = ArduinoVISADevice(port)

    data = {}

    for value in track(range(0, 1024), "Taking measurements..."):
        device.set_output_value(0, value)
        data[value] = {"ch1": [], "ch2": []}
        for _ in range(N):
            data[value]["ch1"].append(device.get_input_value(1))
            data[value]["ch2"].append(device.get_input_value(2))
    device.set_output_value(0, 0)

    with gzip.open(FILENAME, "wt") as f:
        json.dump(data, f)


if __name__ == "__main__":
    main()
