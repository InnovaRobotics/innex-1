# Teensy drive prototype

**Status: desktop-tested prototype with a dry-run output backend. It cannot drive
motors. Do not mark the parent issue or wheel bench test complete.**

This directory contains the C++ safety core, USB message parser, desktop tests,
Teensy 4.1 firmware entry point and Python protocol encoder. Motor-controller mode,
wiring and session handling have not been confirmed. Consequently, `src/main.cpp`
only stores target values; it does not configure or write any motor pins.
This firmware is not ready for deployment with connected motors: high-impedance
pins do not guarantee that the controllers remain off.

## Use on Ubuntu 24.04 / WSL

Run these commands from the Git repository root. Install the tools once on your
development computer; do not install them on the Jetson.

```bash
sudo apt update
sudo apt install python3-venv build-essential
python3 -m venv ~/.venvs/innex-pio
source ~/.venvs/innex-pio/bin/activate
python -m pip install platformio==6.1.18
cd firmware/teensy_drive
```

1. Run the C++ tests without connecting a board:

```bash
pio test -e native
```

2. Test the host protocol encoder intended for the Jetson:

```bash
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/protocol.py 1 0 0
```

The second command only prints an 18-byte message in hexadecimal. It does not
open a serial port or send motor commands. Expected output:
`44 52 01 00 01 00 00 00 00 00 00 00 00 00 00 00 be 37`.

3. Compile the Teensy firmware without flashing it:

```bash
pio run -e teensy41
```

The resulting file is `.pio/build/teensy41/firmware.hex`.
**A successful build does not establish that the firmware can control real motors.**
No automatic upload or live serial-send commands are provided. PlatformIO downloads
the toolchain on its first run.

## Files and suggested reading order

| File | Purpose |
|---|---|
| `PROTOCOL.md` | Draft protocol and known limitations for joint review with INX-140 |
| `lib/DriveCore/DriveCore.h` | Public interface, 250 ms timeout and prototype target bounds |
| `lib/DriveCore/DriveCore.cpp` | CRC, parsing, sequence comparison, stopping and rearming |
| `test/test_drive_core/test_main.cpp` | Safety behaviour tests without hardware |
| `src/main.cpp` | Arduino setup/loop, bounded reads and the dry-run output adapter |
| `tools/protocol.py` | Companion Python host encoder; not a ROS node |
| `tools/test_protocol.py` | Python encoder tests |
| `platformio.ini` | Build configuration pinning Native 1.2.1 and Teensy 5.0.0 |

Behaviour: start stopped, arm on a fresh zero command, accept newer motion targets,
and stop and disarm after 250 ms without a new valid command. A fresh zero command
is required before motion can resume. Old and duplicate messages do not refresh
the watchdog; corrupt or out-of-range messages stop the core immediately.
The core has no Arduino API dependencies, so tests and firmware share the same
implementation.

## Remaining work and acceptance

- Agree the protocol with the INX-140 owner. The Python encoder is an integration
  starting point; this directory does not implement the ROS bridge.
- Add session and freshness handling to reject queued commands after a restart;
  see PROTOCOL.md.
- Confirm Sabertooth control mode, pins, electrical stop defaults, encoders and
  closed-loop speed control.
- Replace DryRunOutput with a real controller adapter. The stop path must actually
  stop all drive outputs.
- Measure worst-case loop latency, serial backlog and output stopping latency to
  meet the end-to-end 250 ms requirement.
- Implement the independent 500 ms timeout in the bridge; that ROS node is outside
  this directory.
- Run `colcon build`, `colcon test` and `colcon test-result --verbose` in Ubuntu.
- Before hardware testing, have the person present confirm the E-stop, wheels off
  the ground and fixed run duration under AGENTS.md and docs/safety.md. Send zero
  at the end. Flash only when explicitly requested and a person is present.
  No board was flashed and no motors were operated during this work.

Submit changes on a task branch through a PR. Do not push directly to main.

## Checked upstream references

- [PlatformIO Core 6.1.18](https://github.com/platformio/platformio-core/releases/tag/v6.1.18)
- [Teensy platform 5.0.0 / Teensyduino 1.59](https://github.com/platformio/platform-teensy/releases/tag/v5.0.0)
- [Native platform 1.2.1](https://github.com/platformio/platform-native/releases/tag/v1.2.1)
- [Shared core code in lib](https://docs.platformio.org/en/stable/advanced/unit-testing/structure/shared-code.html)
- [Teensy USB Serial API](https://www.pjrc.com/teensy/td_serial.html)

PJRC documents that USB Serial is initialised before setup and Serial.begin() is
optional. This entry point does not wait for a host or use delay, blocking reads
or application-level dynamic allocation.
