import pytest

from nsp2visasim import __version__
from nsp2visasim import sim_pyvisa as pyvisa


def test_version():
    assert __version__ == "1.4.0"


@pytest.fixture()
def sim_led_device() -> pyvisa.SimulatedDevice:
    rm = pyvisa.ResourceManager("@py")
    return rm.open_resource("ASRL::SIMLED::INSTR")


def test_list_devices() -> None:
    rm = pyvisa.ResourceManager("@py")
    devices = rm.list_resources()
    assert "ASRL::SIMLED::INSTR" in devices


def test_device(sim_led_device: pyvisa.SimulatedDevice) -> None:
    sim_led_device.query("OUT:CH0 0")
    assert int(sim_led_device.query("MEAS:CH1?")) < 10
    sim_led_device.query("OUT:CH0 1023")
    assert int(sim_led_device.query("MEAS:CH1?")) > 900


def test_device_overflow(sim_led_device: pyvisa.SimulatedDevice) -> None:
    sim_led_device.query("OUT:CH0 1024")
    assert int(sim_led_device.query("MEAS:CH1?")) < 10
