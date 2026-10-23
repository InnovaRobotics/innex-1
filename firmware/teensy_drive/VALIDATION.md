# Validation — 20 October 2026

Environment: Ubuntu 24.04 on WSL, Python 3.12.3, ROS 2 Jazzy,
PlatformIO Core 6.1.18. No physical hardware connected or commanded.

| Command | Result |
|---|---|
| `pio test -e native` | 10 C++ cases passed |
| `python3 -m unittest discover -s tools -p 'test_*.py' -v` | 3 cases passed |
| `pio run -e teensy41` | firmware.elf and firmware.hex built successfully |
| `colcon build --symlink-install` in existing WSL workspace | 2 packages built |
| `colcon test` and `colcon test-result --verbose` | 31 tests, 0 errors, 0 failures, 0 skipped |

Build packages: Native 1.2.1; Teensy platform 5.0.0; Teensyduino framework
1.159.0 (1.59); ARM toolchain 1.110301.0 (11.3.1); Teensy tools 1.162.0.
These are pinned in platformio.ini. Native tests used Unity 2.6.1.

The change is prepared on the task branch `inx-150-teensy-drive-core`.
PR_DRAFT.md contains the proposed review description.

Not verified: physical motor outputs, actual wheel direction or speed, USB
unplug response on hardware, end-to-end <=250 ms stopping, controller startup
electrical state, stale-session protection, and the INX-140 ROS bridge.
These are explicit integration/bench tasks, not claims of this prototype.
