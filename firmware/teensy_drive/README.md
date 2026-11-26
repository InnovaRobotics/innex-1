# teensy_drive

Teensy 4.1 USB serial receiver and 250 ms hardware watchdog for INNEX-1 wheel commands (`INX-144`).

`src/main.cpp` uses a dry-run motor backend (`DryRunOutput`) and does not drive physical motor pins until the Sabertooth 2x32 wiring is integrated. When flashed onto a bare Teensy 4.1, `LED_BUILTIN` lights whenever `DriveCore` is armed with a non-zero wheel target and turns off on `(0, 0)`, USB disconnect, or the 250 ms timeout, allowing USB bench verification without motors attached.

## Build and test on Ubuntu 24.04

Install PlatformIO in a local virtual environment on your development machine (never on the Jetson):

```bash
sudo apt update && sudo apt install -y python3-venv build-essential
python3 -m venv ~/.venvs/innex-pio
~/.venvs/innex-pio/bin/pip install platformio==6.1.18
```

Run the 10 C++ unit tests on your machine without a board:

```bash
cd firmware/teensy_drive
~/.venvs/innex-pio/bin/pio test -e native
```

Compile the Teensy 4.1 firmware image (`.pio/build/teensy41/firmware.hex`) without flashing:

```bash
~/.venvs/innex-pio/bin/pio run -e teensy41
```

In ROS 2 CI, `src/innex_drive_bridge/test/test_protocol.py` also compiles `lib/DriveCore/DriveCore.cpp` with `g++` on every pull request to verify wire and speed-limit compatibility against the Python host encoder.

## Files

| File | Purpose |
|---|---|
| `PROTOCOL.md` | 18-byte `DR` v1 frame layout, CRC-16, and arming rules |
| `lib/DriveCore/DriveCore.h` | `Core` interface, `250` ms timeout, and `+/-1000` mrad/s cap |
| `lib/DriveCore/DriveCore.cpp` | Frame parser, CRC-16, sequence check, and watchdog |
| `src/main.cpp` | Non-blocking Teensy `loop()`, `LED_BUILTIN` bench indicator, and `DryRunOutput` |
| `test/test_drive_core/test_main.cpp` | Desktop Unity tests for arming, timeout, wraparound, and corruption |

## Integrating the Sabertooth 2x32 controllers

Before replacing `DryRunOutput` in `src/main.cpp` and running the block test (`INX-142`) under [Rover safety](../../docs/safety.md):

1. Daisy-chain all Sabertooth 2x32 `S1` inputs onto one Teensy hardware UART transmit pin (such as `Serial1` TX on pin 1) using checksummed Packet Serial addresses (`128`, `129`, `130`), and set each Sabertooth's built-in hardware serial timeout (`100` to `250` ms) in DEScribe so the motor drivers stop in hardware if the `S1` wire disconnects.
2. Keep every Teensy 4.1 pin at `3.3 V` or below (Teensy 4.1 pins are not `5 V` tolerant): step down any `5 V` motor Hall-encoder signals or Sabertooth `S2` lines to `3.3 V` before connecting them to the Teensy.
3. Map `+/-1000` open-loop to a conservative Sabertooth duty limit first for the block test (`INX-142`) before adding encoder feedback for localisation.
