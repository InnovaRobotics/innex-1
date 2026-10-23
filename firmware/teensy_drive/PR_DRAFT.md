# Add tested Teensy drive safety core

## What and why

Refs INX-150; coordinate the protocol with INX-140. This is a partial implementation.

Add a C++ Teensy drive prototype that starts with zero targets, requires a fresh
zero command before motion, rejects duplicate/older sequence numbers and disarms
after 250 ms without a valid command. Share the same core between desktop tests
and the Teensy firmware entry point. Include a draft binary protocol and matching
Python host encoder for discussion with INX-140.

The output backend is deliberately a dry run because motor-controller mode and
wiring are unconfirmed. This does not complete the motor-driving issue or INX-142.
Before rover use, agree session/freshness handling, implement and review the actual
motor adapter and safe electrical defaults, and measure end-to-end stop latency.

## Testing

- Ubuntu 24.04, Python 3.12.3, PlatformIO Core 6.1.18.
- `pio test -e native`: 10 cases passed, including CRC golden vector, startup,
  timeout boundary, rearming, sequence/timer wrap, invalid input and resynchronisation.
- Python unittest: 3 cases passed; host golden frame matches the C++ encoder.
- `pio run -e teensy41`: firmware compiled for Teensy 4.1 using pinned dependencies.
- `colcon build --symlink-install`: both existing ROS packages built.
- `colcon test` / `colcon test-result --verbose`: 31 tests, zero errors/failures.
- No board flashing, serial transmission or motor operation performed.

Full environment details and remaining bench checks are in VALIDATION.md.
The firmware sub-issue number is not yet known. Do not close INX-150 or INX-142:
the motor adapter, session handling and physical acceptance remain outstanding.
