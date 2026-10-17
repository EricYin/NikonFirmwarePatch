"""Card configuration format; this module does not access a card."""
import struct
import zlib
from z8prores.package import require

CONFIG_NAME = 'Z8PRE.CFG'


def build_config(frames=30, c30=True, diagnostic_footer=False, capture_mode='raw-jpeg'):
    require(isinstance(frames, int) and 1 <= frames <= 30, 'Frames must be 1..30')
    require(capture_mode in ('raw-jpeg', 'raw-only'), 'Capture mode must be raw-jpeg or raw-only')
    b = bytearray(64)
    b[:16] = b'Z8PRECFGv2'.ljust(16, b'\0')
    flags = 1 | 0x10 | (2 if c30 else 0) | (8 if diagnostic_footer else 0)
    if capture_mode == 'raw-only':
        flags |= 0x20 | 4 | 0x40
    struct.pack_into('<4I', b, 16, flags, frames, 1500000, 0)
    struct.pack_into('<I', b, 60, zlib.crc32(b[:60]))
    return bytes(b)
