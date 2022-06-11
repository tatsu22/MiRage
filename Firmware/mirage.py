import time
from pca950x import PCA950x
#from mcp23018 import MCP2301x
from util import timed_function

# TODO: remap these to follow my schem
physical_key_assignments = {
    (1, 3, 7): (0, 0),
    (1, 4, 0): (0, 1),
    (1, 4, 1): (0, 2),
    (1, 4, 2): (0, 3),
    (1, 4, 3): (0, 4),
    (1, 4, 4): (0, 5),
    (1, 4, 5): (0, 6),
    (1, 3, 0): (1, 0),
    (1, 3, 1): (1, 1),
    (1, 3, 2): (1, 2),
    (1, 3, 6): (1, 3),
    (1, 3, 5): (1, 4),
    (1, 3, 4): (1, 5),
    (1, 3, 3): (1, 6),
    (1, 2, 7): (2, 0),
    (1, 2, 6): (2, 1),
    (1, 2, 5): (2, 2),
    (1, 2, 4): (2, 3),
    (1, 2, 1): (2, 4),
    (1, 2, 2): (2, 5),
    (1, 2, 3): (2, 6),
    (1, 2, 0): (3, 0),
    (1, 1, 7): (3, 1),
    (1, 1, 6): (3, 2),
    (1, 1, 5): (3, 3),
    (1, 1, 4): (3, 4),
    (1, 1, 3): (3, 5),
    (1, 1, 2): (3, 6),
    (1, 1, 1): (4, 0),
    (1, 1, 0): (4, 1),
    (1, 0, 7): (4, 2),
    (1, 0, 6): (4, 3),
    (1, 0, 5): (4, 4),
    (1, 0, 4): (4, 5),
    (1, 0, 2): (5, 0),
    (1, 0, 3): (5, 1),
    (1, 0, 0): (5, 2),
    (1, 0, 1): (5, 3),
    (0, 0, 2): (0, 7),
    (0, 0, 3): (0, 8),
    (0, 0, 4): (0, 9),
    (0, 0, 5): (0, 10),
    (0, 0, 6): (0, 11),
    (0, 0, 7): (0, 12),
    (0, 1, 0): (0, 13),
    (0, 1, 1): (1, 7),
    (0, 1, 2): (1, 8),
    (0, 1, 3): (1, 9),
    (0, 1, 4): (1, 10),
    (0, 1, 5): (1, 11),
    (0, 1, 6): (1, 12),
    (0, 1, 7): (1, 13),
    (0, 3, 6): (2, 7),
    (0, 3, 7): (2, 8),
    (0, 4, 0): (2, 9),
    (0, 2, 3): (2, 10),
    (0, 2, 2): (2, 11),
    (0, 2, 1): (2, 12),
    (0, 2, 0): (2, 13),
    (0, 3, 2): (3, 7),
    (0, 3, 1): (3, 8),
    (0, 3, 0): (3, 9),
    (0, 2, 7): (3, 10),
    (0, 2, 6): (3, 11),
    (0, 2, 5): (3, 12),
    (0, 2, 4): (3, 13),
    (0, 4, 3): (4, 6),
    (0, 4, 2): (4, 7),
    (0, 4 ,1): (4, 8),
    (0, 3, 5): (4, 9),
    (0, 3, 4): (4, 10),
    (0, 3, 3): (4, 11),
    (0, 4, 6): (5, 4),
    (0, 4, 7): (5, 5),
    (0, 4, 4): (5, 6),
    (0, 4, 5): (5, 7)

# EXAMPLE
#  (which PCA9505, which bank, which line): (row, col)
#    (0, 0, 6): (0, 2),
}

class IOAssociation:
    __slots__ = 'input_line', 'row', 'col'

    def __init__(self, input_line, row, col):
        self.input_line = input_line
        self.row = row
        self.col = col


class KeyGrid:
    def __init__(self, i2c, keymap, keys=physical_key_assignments):
        self.io_expanders = []
        self.key_associations = []

        self.i2c = i2c  # Should already be locked
        self.keymap = keymap
        self.keys = keys

        self.key_down_timestamps = {}
        self.keys_held = []
        self.recent_key_clicks = {}

        self.click_timeout = 0.1  # Release the key within this many seconds to fire a click
        self.double_click_timeout = 0.2  # Click again within this many seconds to fire a double click

    def setup(self):
        self.io_expanders.append(PCA950x(self.i2c, 0x20)) # TODO: Uncomment when we make the first half
        self.io_expanders.append(PCA950x(self.i2c, 0x24)) # TODO: Uncomment when we make the second half
        #self.io_expanders.append(MCP2301x(self.i2c, 0x20))

        for io_expander in self.io_expanders:
            io_expander.reset()

        for index, io_expander in enumerate(self.io_expanders):
            for input_line in io_expander.input_lines:
                coords = index, input_line.bank, input_line.line

                if coords in self.keys:
                    row, col = self.keys[coords]
                    is_a_key = True
#                elif coords in self.buttons:
#                    row, col = self.buttons[coords]
#                    is_a_key = False
                else:
                    continue

                self.key_associations.append(IOAssociation(input_line, row, col))

    # @timed_function
    def update(self):
        for index, io_expander in enumerate(self.io_expanders):
            io_expander.update()

        for line in self.key_associations:
            if line.input_line.fell:  # Key pressed down
                print('Row {}, col {} pressed'.format(line.row, line.col))
                self.keymap.fire_operation(line.row, line.col, 'press')
#                if self.clicky_displays is not None:
#                    for display in self.clicky_displays:
#                        display.on_keystroke(0x00)  # TODO: Only do something if a key was pressed, and pass in which key

                self.key_down_timestamps[line] = time.monotonic()

            elif line.input_line.rose:
                if line in self.key_down_timestamps:
                    hold_length = time.monotonic() - self.key_down_timestamps[line]
                    print('Held for', hold_length)
                else:
                    hold_length = 666
                    print('WEIRD SHIT - Key rose without previously falling')

                del self.key_down_timestamps[line]

                print('Row {}, col {} went high after {}ms'.format(line.row, line.col, hold_length))

                if hold_length <= self.click_timeout:
                    is_double_click = False

                    print("That's a click")

                    if line in self.recent_key_clicks:
                        if time.monotonic() - self.recent_key_clicks[line]\
                            <= self.double_click_timeout:
                            del self.recent_key_clicks[line]
                            is_double_click = True
                    else:
                        self.recent_key_clicks[line] = time.monotonic()

                    # TODO: When both a click and double click are assigned, clicking once should delay til DC threshold passed

                    if is_double_click:
                        # print("Row {}, col {} double-clicked".format(line.row, line.col))
                        self.keymap.fire_operation(line.row, line.col, 'double-click')
                    else:
                        # print('Row {}, col {} clicked'.format(line.row, line.col))
                        self.keymap.fire_operation(line.row, line.col, 'click')

                if line in self.keys_held:
                    # print('Row {}, col {} no longer held'.format(line.row, line.col))
                    self.keymap.fire_operation(line.row, line.col, 'end hold')
                    self.keys_held.remove(line)

                # print('Row {}, col {} released'.format(line.row, line.col))
                self.keymap.fire_operation(line.row, line.col, 'release')

            elif not line.input_line.value:
                if line in self.key_down_timestamps\
                    and time.monotonic() - self.key_down_timestamps[line] > self.click_timeout:
                    if line in self.keys_held:
                        self.keymap.fire_operation(line.row, line.col, 'continue hold')
                    else:
                        # print('Row {}, col {} now held'.format(line.row, line.col))
                        self.keys_held.append(line)
                        self.keymap.fire_operation(line.row, line.col, 'start hold')

        trash = []
        for line, timestamp in self.recent_key_clicks.items():
            if time.monotonic() - timestamp > self.double_click_timeout:
                trash.append(line)

        for line in trash:
            del self.recent_key_clicks[line]
