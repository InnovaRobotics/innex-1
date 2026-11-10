"""Draft INX-140 host codec. Offline only: never opens a serial device."""
import argparse
import binascii
import struct

LIMIT_MRAD_S = 1000


def encode(sequence: int, left_mrad_s: int, right_mrad_s: int) -> bytes:
    if not 0 <= sequence <= 0xFFFFFFFF:
        raise ValueError("sequence must fit uint32")
    if any(abs(v) > LIMIT_MRAD_S for v in (left_mrad_s, right_mrad_s)):
        raise ValueError("prototype limit is +/-1000 mrad/s")
    payload = struct.pack("<2sBBIii", b"DR", 1, 0, sequence, left_mrad_s, right_mrad_s)
    return payload + struct.pack("<H", binascii.crc_hqx(payload, 0xFFFF))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sequence", type=int)
    parser.add_argument("left", type=int, help="milliradians per second")
    parser.add_argument("right", type=int, help="milliradians per second")
    args = parser.parse_args()
    print(encode(args.sequence, args.left, args.right).hex(" "))
