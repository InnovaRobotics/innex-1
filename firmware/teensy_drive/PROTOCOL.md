# Drive serial protocol v1

`innex_drive_bridge` (`src/innex_drive_bridge/innex_drive_bridge/protocol.py`) and `DriveCore` (`lib/DriveCore/`) exchange fixed 18-byte little-endian frames over Teensy USB serial:

| Offset | Size | Meaning |
|---|---|---|
| 0 | 2 | ASCII `DR` (`0x44 0x52`) |
| 2 | 1 | Protocol version (`1`) |
| 3 | 1 | Reserved (`0`) |
| 4 | 4 | Unsigned 32-bit sequence number |
| 8 | 4 | Signed 32-bit left wheel target (`-1000` to `1000` mrad/s) |
| 12 | 4 | Signed 32-bit right wheel target (`-1000` to `1000` mrad/s) |
| 16 | 2 | CRC-16/CCITT-FALSE over bytes 0 to 15 |

CRC-16 parameters: polynomial `0x1021`, initial value `0xffff`, no reflection, no final XOR (`123456789` gives `0x29b1`, and `(seq=1, left=0, right=0)` encodes as `44 52 01 00 01 00 00 00 00 00 00 00 00 00 00 00 be 37`). Targets are absolute setpoints, where positive values mean forward on both sides and `+/-1000` mrad/s (`1.0` rad/s) is the prototype cap until the block test (`INX-142`).

## Safety rules in `DriveCore`

- Startup and recovery require a valid `(0, 0)` frame before `DriveCore` arms and accepts non-zero targets.
- If `250` ms (`kTimeoutMs`) pass on `millis()` without a valid frame, both targets drop to `0` and `DriveCore` disarms.
- Sequence comparison uses `uint32_t(incoming - previous)` and accepts values in `1 .. 2^31 - 1`, ignoring duplicates and out-of-order frames without refreshing the `250` ms timer.
- Any frame with a bad header, bad CRC, or out-of-range target disarms `DriveCore` immediately; partial frames expire after a `250` ms inter-byte gap.
