from copy import deepcopy
from spidev import SpiDev

MAX7219_NOOP_REG = 0x0
MAX7219_DIGIT0_REG = 0x1
MAX7219_DIGIT1_REG = 0x2
MAX7219_DIGIT2_REG = 0x3
MAX7219_DIGIT3_REG = 0x4
MAX7219_DIGIT4_REG = 0x5
MAX7219_DIGIT5_REG = 0x6
MAX7219_DIGIT6_REG = 0x7
MAX7219_DIGIT7_REG = 0x8
MAX7219_DECODEMODE_REG = 0x9
MAX7219_INTENSITY_REG = 0xA
MAX7219_SCANLIMIT_REG = 0xB
MAX7219_SHUTDOWN_REG = 0xC
MAX7219_DISPLAY_TEST_REG = 0xF
MAX7219_DECODE_NONE = 0x0
MAX7219_SCAN_ALL = 0x7
MAX7219_DISPLAY_TEST_NO = 0x0
MAX7219_SHUTDOWN_NO = 0x1

DEFAULT_BRIGHTNESS = 4

# 'No operation' tuple: 0x0 sent to register MAX7219_NOOP_REG
_NO_OP_DATA = [MAX7219_NOOP_REG, 0x0]

_spi = SpiDev()

def _spi_open():
    _spi.open(0, 0)

def _spi_close():
    _spi.close()

def _send_bytes(datalist):
    # Send sequence of bytes (should be [register,data] tuples) via SPI port, then raise CS
    # Included for ease of remembering the syntax rather than the native spidev command,
    # but also to avoid reassigning to 'datalist' argument
    _spi.xfer2(datalist[:])

class DisplayUnit(object):

    def __init__(self, blocks_per_row, blocks_per_column):
        self.blocks_per_row = blocks_per_row
        self.blocks_per_column = blocks_per_column
        self.blocks = range(self.blocks_per_row * self.blocks_per_column)
        self.rows = range(self.blocks_per_column * 8)
        self.columns = range(self.blocks_per_row * 8)
        self.buffer = [[0 for _col in self.rows] for _row in self.columns]

    def send_to(self, block, register, data):
        if block in self.blocks:
            padded_data = _NO_OP_DATA * (len(self.blocks) - block - 1) + [register, data] + _NO_OP_DATA * block
            _send_bytes(padded_data)

    def send_to_all(self, register, data):
        _send_bytes([register, data] * len(self.blocks))

    def clear_blocks(self, blocks):
        # Clear one or more specified MAX7219 matrices (argument(s) to be specified as a list even if just one)
        for block in blocks:
            if block in self.blocks:
                for digit in range(8):
                    self.send_to(block, digit + 1, 0)

    def clear_all_blocks(self):
        # Clear all of the connected MAX7219 matrices
        for digit in range(8):
            self.send_to_all(digit + 1, 0)

    def set_brightness(self, intensity):
        # Set a specified set_brightness level on all of the connected MAX7219 matrices
        # Intensity: 0-15 with 0=dimmest, 15=brightest; in practice the full range does not represent a large difference
        intensity = int(max(0, min(15, intensity)))
        self.send_to_all(MAX7219_INTENSITY_REG, intensity)

    def clone_buffer(self):
        # returns the whole buffer array
        return deepcopy(self.buffer)

    def clear_buffer(self):
        for x in self.columns:
            for y in self.rows:
                self.buffer[x][y] = 0

    def send_buffer(self):
        for block_col in range(8):
            column_data = []
            for block in reversed(self.blocks):
                buffer_row = self.buffer[(block // self.blocks_per_column) * 8 + block_col]
                column_offset = (block % self.blocks_per_column) * 8
                data_byte = 0x00
                if buffer_row[column_offset + 0]:
                    data_byte |= 0x80
                if buffer_row[column_offset + 1]:
                    data_byte |= 0x40
                if buffer_row[column_offset + 2]:
                    data_byte |= 0x20
                if buffer_row[column_offset + 3]:
                    data_byte |= 0x10
                if buffer_row[column_offset + 4]:
                    data_byte |= 0x08
                if buffer_row[column_offset + 5]:
                    data_byte |= 0x04
                if buffer_row[column_offset + 6]:
                    data_byte |= 0x02
                if buffer_row[column_offset + 7]:
                    data_byte |= 0x01
                column_data += [block_col + 1, data_byte]
            _send_bytes(column_data)

    def init(self):
        # Initialise all of the MAX7219 chips (see datasheet for details of registers)
        _spi_open()
        self.clear_all_blocks()
        self.send_to_all(MAX7219_SCANLIMIT_REG, MAX7219_SCAN_ALL)
        self.send_to_all(MAX7219_DECODEMODE_REG, MAX7219_DECODE_NONE)
        self.send_to_all(MAX7219_DISPLAY_TEST_REG, MAX7219_DISPLAY_TEST_NO)
        self.send_to_all(MAX7219_SHUTDOWN_REG, MAX7219_SHUTDOWN_NO)
        self.set_brightness(DEFAULT_BRIGHTNESS)

    def release(self):
        _spi_close()
