from pythondaq.controllers.arduino_device import ArduinoVISADevice

device = ArduinoVISADevice("ASRL::SIMLED::INSTR")
# device = ArduinoVISADevice("ASRL/dev/cu.usbmodem14501::INSTR")
print(f"{device.get_identification()=}")
print(f"{device.set_output_value(0, 768)=}")
print(f"{device.get_output_value(0)=}")
print(f"{device.set_output_voltage(0, 2.5)=}")
print(f"{device.get_output_voltage(0)=}")
print(f"{device.get_input_value(1)=}")
print(f"{device.get_input_voltage(1)=}")
