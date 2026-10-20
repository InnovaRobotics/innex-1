# Draft drive protocol v1 — not approved for rover deployment

Agree this draft with INX-140 before integration. The companion Python codec
in `tools/protocol.py` implements the host encoding, not a ROS bridge.
All multi-byte fields are little-endian. A frame is exactly 18 bytes:

| Offset | Size | Meaning |
|---|---|---|
| 0 | 2 | ASCII `DR` |
| 2 | 1 | Version 1 |
| 3 | 1 | Reserved, must be zero |
| 4 | 4 | Unsigned sequence number |
| 8 | 4 | Signed left target, milliradians/second |
| 12 | 4 | Signed right target, milliradians/second |
| 16 | 2 | CRC-16/CCITT-FALSE of bytes 0–15 |

CRC: polynomial 0x1021, initial 0xffff, no reflection, no final XOR.
`123456789` produces 0x29b1. Positive means forward on both sides; the future
hardware adapter must compensate for wiring direction. The prototype rejects
values outside +/-1000 mrad/s (1 rad/s). This is a conservative test bound,
not a measured or approved motor speed limit. Targets are absolute, not increments.

At startup, only a zero/zero command can arm the core; a subsequent newer command
can request motion. At age >=250 ms, both targets become zero and the core
disarms. A fresh zero is required before further motion. Timeout uses local
monotonic milliseconds, not ROS time. Duplicates, old frames and incomplete
frames never refresh it. A malformed complete frame or an out-of-range command
stops the core immediately. Noise can cause extra stops; this favours stopping
over continuing motion. Partial frames expire after a 250 ms inter-byte gap.

Sequence comparison: delta = new - previous modulo 2^32; accept only
0 < delta < 2^31. Never clear the last accepted sequence on timeout/disconnect.
On bridge-only restart, recover the continuing sequence through a future session
protocol; resetting the bridge counter to zero is not supported. Power-cycling
the Teensy clears RAM and requires a fresh zero command.

Integration blockers: agree a session/freshness handshake so delayed data or a
previous host session cannot arm a freshly booted device. CRC detects corruption,
not sender identity or message age. Sequence alone cannot detect a delayed but
increasing backlog. Do not deploy this draft to a rover before resolving that.
The host must enforce its own 500 ms command timeout and send at a regular rate
(proposed 50 Hz), using only fresh commands and bounded queues. That host watchdog
is outside this firmware implementation.

Timing: the core transitions at exactly 250 ms when ticked. A polling loop adds
its scheduling and output-adapter latency, so this does not prove the bench
requirement of stopping physical outputs within 250 ms. Before motor deployment,
measure the worst-case latency and use an independently scheduled stop or a
conservative earlier internal deadline to meet the end-to-end 250 ms bound.
Never lengthen the existing timeout.
