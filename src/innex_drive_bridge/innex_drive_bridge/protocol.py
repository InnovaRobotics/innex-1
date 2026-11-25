"""Encode the unchanged 18-byte protocol from firmware PRs 10 and 12."""

import binascii
import struct

FRAME_SIZE = 18
LIMIT_MRAD_S = 1000


def encode(sequence: int, left_mrad_s: int, right_mrad_s: int) -> bytes:
    """Encode absolute wheel targets using little-endian CRC-16/CCITT-FALSE."""
    if type(sequence) is not int or not 0 <= sequence <= 0xFFFFFFFF:
        raise ValueError('Sequence must be a uint32 integer')
    for value in (left_mrad_s, right_mrad_s):
        if type(value) is not int or not -LIMIT_MRAD_S <= value <= LIMIT_MRAD_S:
            raise ValueError('Wheel targets must be integer mrad/s within +/-1000')
    payload = struct.pack('<2sBBIii', b'DR', 1, 0, sequence, left_mrad_s, right_mrad_s)
    return payload + struct.pack('<H', binascii.crc_hqx(payload, 0xFFFF))


def decode(frame: bytes):
    """Validate and decode a frame for offline diagnostics and tests."""
    if len(frame) != FRAME_SIZE:
        raise ValueError('Expected exactly 18 bytes')
    magic, version, reserved, sequence, left, right, crc = struct.unpack('<2sBBIiiH', frame)
    if magic != b'DR' or version != 1 or reserved != 0:
        raise ValueError('Unsupported frame header')
    if crc != binascii.crc_hqx(frame[:16], 0xFFFF):
        raise ValueError('CRC mismatch')
    if not -1000 <= left <= 1000 or not -1000 <= right <= 1000:
        raise ValueError('Target outside prototype range')
    return sequence, left, right
