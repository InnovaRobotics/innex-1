# Local validation — 22 October 2026

This implementation extends the PR #11 skeleton on branch
`inx-140-drive-bridge-local`. These results record local validation before submission.
The wire format remains compatible with the PR #10/#12 firmware reference.

## Environment

- Ubuntu 24.04 on WSL, Python 3.12.3, ROS 2 Jazzy.
- System pySerial 3.5 and g++ for the offline C++ compatibility harness.
- Windows source mirror: `Innova robot/src/innex_drive_bridge`.
- Working ROS package: `~/innex_ws/src/innex-1/src/innex_drive_bridge`.

## Results

| Check | Result |
|---|---|
| `colcon build --symlink-install` | All 3 ROS packages built successfully |
| Bridge package tests after the final code change | 46 tests, zero errors/failures/skips |
| Existing model and simulation tests | 31 tests, zero errors/failures/skips |
| Installed launch startup and Ctrl+C | Passed as a regression test |
| PR #10 reference receiver compatibility | Actual C++ receiver compiled and accepted host frames |
| Source/documentation language scan | No Chinese comments or text in this package |

Before submission, the complete workspace was rebuilt and tested again with the
final implementation. All 77 tests passed, including 46 bridge-package tests and
31 existing model/simulation tests, with zero errors, failures or skips.

Generated lint checks emit Python 3.12 warnings about forking from a process with
threads. These warnings are from the lint tool invocation; no test failed or was
skipped.

## Tested behaviour

- Straight, reverse and turning conversions; curvature-preserving saturation.
- Invalid geometry, non-finite inputs, overflow and unsupported axes.
- Exact 500 ms core deadline, conservative runtime margin, delayed command
  lifetime, old/future/zero timestamps and frame rejection.
- Golden CRC frame, signed targets and firmware-side sequence/CRC verification.
- Startup zero, periodic targets, timeout zero and shutdown zero.
- Persistent sequence reservation, duplicate-process lock and corrupt state.
- Real pySerial writes to newly allocated virtual terminals, partial writes,
  queue detection, unplug and latched communication faults.
- Actual Jazzy DDS subscription QoS and message delivery.
- Safety send timer continuing with a paused simulation clock.
- Installed launch using dry-run defaults and clean shutdown under Ctrl+C.

## Limits

No physical USB device was opened. No Jetson was changed, no firmware was flashed
and no real motor commands were sent. Physical wheel direction/speed, electrical
defaults and end-to-end stopping latency remain unverified. The existing v1
protocol has no acknowledgement or session/freshness handshake; persistent host
sequences are not a replacement for that firmware/host design work. Review with
INX-144 and complete the supervised bench test before claiming task acceptance.
