"""Menu-controlled capture configuration; this module never accesses a card."""
import struct
import zlib

CONFIG_NAME = 'Z8PRE.CFG'


def build_config(diagnostic_footer=False):
    b = bytearray(64)
    b[:16] = b'Z8PRECFGv3'.ljust(16, b'\0')
    # Enable C15/C30, stock registration and ordinary Image quality menu control.
    # 30 is the history-window ceiling, not a post-release burst limit.
    flags = 0x93 | (8 if diagnostic_footer else 0)
    struct.pack_into('<4I', b, 16, flags, 30, 1500000, 0)
    struct.pack_into('<I', b, 60, zlib.crc32(b[:60]))
    return bytes(b)
