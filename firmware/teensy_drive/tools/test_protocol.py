import binascii
import struct
import unittest

from protocol import encode


class ProtocolTests(unittest.TestCase):
    def test_zero_golden_frame(self):
        self.assertEqual(encode(1, 0, 0).hex(), "44520100010000000000000000000000be37")

    def test_signed_units_and_crc(self):
        frame = encode(0xFFFFFFFF, -300, 400)
        self.assertEqual(len(frame), 18)
        self.assertEqual(struct.unpack("<Iii", frame[4:16]), (0xFFFFFFFF, -300, 400))
        self.assertEqual(struct.unpack("<H", frame[16:])[0], binascii.crc_hqx(frame[:16], 0xFFFF))

    def test_reject_invalid_inputs(self):
        for args in [(-1, 0, 0), (2**32, 0, 0), (1, 1001, 0), (1, 0, -1001)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                encode(*args)


if __name__ == "__main__":
    unittest.main()
