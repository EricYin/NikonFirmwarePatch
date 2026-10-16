"""Card configuration format; this module does not access a card."""
import struct
import zlib
from z8prores.package import require

CONFIG_NAME = 'Z8PRE.CFG'


def build_config(frames=30, c30=True, diagnostic_footer=False):
    require(isinstance(frames, int) and 1 <= frames <= 30, 'Frames must be 1..30')
    b = bytearray(64)
    b[:16] = b'Z8PRECFGv1'.ljust(16, b'\0')
    flags = 1 | (2 if c30 else 0) | (8 if diagnostic_footer else 0)
    struct.pack_into('<4I', b, 16, flags, frames, 1500000, 0)
    struct.pack_into('<I', b, 60, zlib.crc32(b[:60]))
    return bytes(b)
