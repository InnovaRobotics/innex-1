"""Convert body velocity into wheel targets and pack 18-byte Teensy frames."""

import binascii
import math
import struct

FRAME_SIZE = 18
LIMIT_MRAD_S = 1000
MAX_WHEEL_RAD_S = LIMIT_MRAD_S / 1000.0


def wheel_targets(
    linear_x: float,
    angular_z: float,
    radius: float = 0.153,
    track: float = 0.675,
    max_wheel_rad_s: float = MAX_WHEEL_RAD_S,
) -> tuple[int, int]:
    """Return integer (left, right) mrad/s, scaling both wheels together at the cap."""
    for value in (radius, track, max_wheel_rad_s):
        if not math.isfinite(value) or value <= 0:
            raise ValueError('Geometry and wheel limit must be finite and positive')

    if max_wheel_rad_s > MAX_WHEEL_RAD_S:
        raise ValueError(f'Wheel limit exceeds firmware cap ({MAX_WHEEL_RAD_S} rad/s)')

    if not math.isfinite(linear_x) or not math.isfinite(angular_z):
        raise ValueError('Body velocities must be finite')

    left = (linear_x - angular_z * track / 2.0) / radius
    right = (linear_x + angular_z * track / 2.0) / radius

    if not math.isfinite(left) or not math.isfinite(right):
        raise ValueError('Wheel conversion overflowed')

    scale = max(1.0, abs(left) / max_wheel_rad_s, abs(right) / max_wheel_rad_s)
    return round(left / scale * 1000), round(right / scale * 1000)


def encode(sequence: int, left_mrad_s: int, right_mrad_s: int) -> bytes:
    """Encode sequence and wheel targets with little-endian CRC-16/CCITT-FALSE."""
    if type(sequence) is not int or not 0 <= sequence <= 0xFFFFFFFF:
        raise ValueError('Sequence must be a uint32 integer')

    for value in (left_mrad_s, right_mrad_s):
        if type(value) is not int or not -LIMIT_MRAD_S <= value <= LIMIT_MRAD_S:
            raise ValueError(f'Wheel targets must be integer mrad/s within +/-{LIMIT_MRAD_S}')

    payload = struct.pack('<2sBBIii', b'DR', 1, 0, sequence, left_mrad_s, right_mrad_s)
    return payload + struct.pack('<H', binascii.crc_hqx(payload, 0xFFFF))


def decode(frame: bytes) -> tuple[int, int, int]:
    """Validate and unpack an 18-byte frame into (sequence, left_mrad_s, right_mrad_s)."""
    if len(frame) != FRAME_SIZE:
        raise ValueError(f'Expected {FRAME_SIZE} bytes')

    magic, version, reserved, sequence, left, right, crc = struct.unpack('<2sBBIiiH', frame)

    if magic != b'DR' or version != 1 or reserved != 0:
        raise ValueError('Unsupported frame header')

    if crc != binascii.crc_hqx(frame[:16], 0xFFFF):
        raise ValueError('CRC mismatch')

    if not -LIMIT_MRAD_S <= left <= LIMIT_MRAD_S or not -LIMIT_MRAD_S <= right <= LIMIT_MRAD_S:
        raise ValueError('Target outside firmware range')

    return sequence, left, right
