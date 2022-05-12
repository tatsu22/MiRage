import digitalio
from adafruit_bus_device import i2c_device
from util import timed_function
from pca950x import InputLine
from adafruit_mcp230xx.mcp23017 import MCP23017

class MCP2301x:

    def __init__(self, i2c_bus, addr):
        self.device = MCP23017(i2c_bus, address=addr)

        self.input_lines = []

        for bank in range(2):
            for line in range(8):
                self.input_lines.append(InputLine(bank, line))

        self.reset()

    def reset(self, invert=False):
        # set pullups on all registers
        for i in range(16):
            pin = self.device.get_pin(i)
            pin.direction = digitalio.Direction.INPUT
            pin.pull = digitalio.Pull.UP

        self.update()

    # @timed_function
    def update(self):
        for i in range(16):
            self.input_lines[i].set_value(not self.device.get_pin(i).value)
