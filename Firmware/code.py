print('Top of the code to ya')

import board
import busio
import time
import usb_hid
# from adafruit_hid.keyboard import Keyboard
from bitmap_keyboard import BitmapKeyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
#from pca950x import PCA950x
from mirage import KeyGrid
from keymapping import Keymap
#from clicky_buttons import *
from util import timed_function
import parser

print('MiRage keyboard go!')

i2c = busio.I2C(board.SCL, board.SDA, frequency=576000)
#i2c1 = busio.I2C(board.SCL, board.SDA, frequency=576000)
# usb_keyboard = Keyboard(usb_hid.devices)
usb_keyboard = BitmapKeyboard(usb_hid.devices)
hid_keyboard_locale = KeyboardLayoutUS(usb_keyboard)

while not i2c.try_lock():
    print('Failed to lock I2C')
    time.sleep(0.5)

#while not i2c1.try_lock():
#    print('Failed to lock I2C1')
#    time.sleep(0.5)

print("I2C addresses found on bus 0:", [hex(device_address)
              for device_address in i2c.scan()])

#print("I2C addresses found on bus 1:", [hex(device_address)
#              for device_address in i2c1.scan()])

i2c.unlock()
#i2c1.unlock()

try:
    # parser.debug_line_callback = cool_ass_parsing_visualizer

    keymap = Keymap(usb_keyboard, hid_keyboard_locale)
    keymap.load('/MiRage Keymaps')  # TODO: Detect and automatically switch to Rage pad

    parser.debug_line_callback = None

    # selector = LayerSelector(oleds[1], 1, keymap, wrap_enabled=True)
    # selector.add_layer('base layer')
    # selector.add_layer('function layer')

    keeb = KeyGrid(i2c, keymap)
    keeb.setup()

    print("ALL READY! It's time to c-c-c-c-clack!")

    while True:
        #benchmark = time.monotonic_ns()

        keeb.update()

        keymap.enact_queues()

        """
        try:
            print('Refresh rate: {:.0f}Hz'.format(1/(time.monotonic_ns() - benchmark)*1000000000))
        except ZeroDivisionError:
            pass
        """

finally:
    print('it ded')
    i2c.unlock()
#    i2c1.unlock()
    usb_keyboard.release_all()
