# innex_drive_bridge

Python ROS 2 Jazzy implementation of the INX-140 host bridge, extending the
node skeleton originally introduced in PR #11.

The node subscribes to `geometry_msgs/msg/TwistStamped` on `/cmd_vel`, converts
body velocity into wheel targets and periodically encodes the unchanged 18-byte
protocol from firmware PRs #10 and #12. It uses best-effort, keep-last depth 1
and volatile durability. The default dry-run mode never opens a serial device.

This completes the host software implementation and automated desktop checks,
not the rover bench acceptance. The existing firmware has no session handshake
or acknowledgement and still has a dry-run motor backend. Do not describe this
as a hardware-validated or deployment-ready drive system.

## Build and run

From the Ubuntu 24.04 workspace root:

```bash
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -y
colcon build --symlink-install --packages-select innex_drive_bridge
source install/setup.bash
ros2 launch innex_drive_bridge drive_bridge.launch.py
```

Expect `dry_run=True` and zero targets. Stop with Ctrl+C. Direct invocation with
`ros2 run innex_drive_bridge bridge_node` also defaults to dry-run. The launch
accepts `params_file:=/absolute/path/to/config.yaml`; it installs the supplied
configuration in `share/innex_drive_bridge/config/drive_bridge.yaml`.

To edit files on WSL, use the repository directory
`~/innex_ws/src/innex-1/src/innex_drive_bridge`. Build from `~/innex_ws`.

## Test

```bash
colcon test --packages-select innex_drive_bridge
colcon test-result --verbose
```

Run tests from the workspace root as shown above, not a raw pytest command from
the workspace root: generated lint checks expect the package working directory.
The compatibility tests require `g++` (provided by Ubuntu `build-essential`).

Tests exercise geometry, scaling, NaN/overflow rejection, timestamps, exact
500 ms expiry, delayed messages, CRC and the reference firmware, persistent
sequence reservations, partial writes, unplug, actual DDS input and a paused
simulation clock. Serial tests allocate only temporary `/dev/pts` virtual ports;
they never open physical USB devices. ROS tests use a separate process-specific
ROS_DOMAIN_ID.

## Runtime behaviour

- Wheel conversion uses `(v - w * track / 2) / radius` on the left and the plus
  sign on the right. Both speeds are scaled together to retain curvature when
  bounded, then converted from rad/s to integer mrad/s.
- The +/-1 rad/s limit preserves the firmware prototype bound. Geometry comes
  from the provisional URDF and must be measured before rover use.
- Require `header.frame_id=base_link`, a nonzero increasing timestamp and finite
  planar velocities. Unsupported axes must be zero. Invalid input clears motion.
  The publisher and bridge need synchronised ROS/system clocks.
- Delayed input gets only its remaining lifetime; receiving a 400 ms old command
  does not grant it another 500 ms. An already stale/future/repeated stamp stops
  motion. The monotonic watchdog remains active if ROS time pauses or jumps.
- The send timer uses STEADY_TIME, default 50 Hz. An early stop margin reserves
  one period, a 10 ms write budget and 5 ms slack (35 ms at 50 Hz). Thus default
  motion expiry is conservatively 465 ms after the original message timestamp.
  Linux scheduling and USB latency are not hard real time; measure actual stopping
  time on the bench. Neither the 500 ms nor the firmware 250 ms timeout is increased.
- Start by transmitting zero and discard input received before that write.
  Continue sending zero while idle, timed out or invalid. On shutdown, attempt a
  final zero and close without an unbounded flush.
- Any serial error, queued previous write or partial write latches a fault,
  discards motion and closes the port. No automatic reconnect or motion retry is
  performed. Inspect the link and restart explicitly. The firmware's independent
  250 ms watchdog handles loss of the bridge, including SIGKILL or host failure.

## Configuration and sequence recovery

All declared bridge parameters are read-only at runtime. Device paths belong in
the YAML file, not in source code. Serial mode requires all of:

- `dry_run: false` and `legacy_protocol_reviewed: true` after team review;
- an explicitly selected `serial_port` and no simulation time;
- a writable persistent `sequence_state_file` unique to this Teensy/bridge pair.

The process exclusively locks that file and reserves 65536 sequence values
before sending. A host restart skips the unused part, so a still-running Teensy
can accept a newer zero command without resetting its counter. Never delete or
copy/reset this file to recover from an error. Corrupt state fails closed.
If another sender has been used, more than half the uint32 sequence space has
been skipped without reception, or the file is lost, v1 has no safe automatic
resynchronisation: coordinate recovery with the firmware owner.

Opening/closing a port or writing zero does not prove that the Teensy received
it. Persistent sequences do not solve stale data following a Teensy reboot.
CRC is not authentication. The v1 protocol still needs a reviewed session and
freshness handshake on BOTH ends before real rover deployment. This bridge keeps
the wire protocol unchanged rather than silently inventing an incompatible one.

## Files

| File | Responsibility |
|---|---|
| `bridge_node.py` | ROS subscription, read-only parameters and steady send timer |
| `kinematics.py` | Geometry validation and bounded wheel conversion |
| `control.py` | Timestamp ordering, command freshness and monotonic watchdog |
| `protocol.py` | Firmware-compatible encoder and offline decoder |
| `sequence.py` | Exclusive persistent sequence reservation |
| `transport.py` | Dry-run output or bounded exclusive POSIX serial writes |
| `sender.py` | Startup/shutdown zero, periodic sending and fault latching |
| `config/drive_bridge.yaml` | Default dry-run settings |
| `launch/drive_bridge.launch.py` | Parameter-file launch entry point |
| `test/firmware_reference` | Actual PR #10 receiver used by compatibility tests |

## Hardware acceptance still required

Agree the architecture and protocol with INX-144 and the team. Complete the actual
motor-output adapter in the firmware. Under AGENTS.md and docs/safety.md, a person
must be present with the E-stop reachable, the wheels off the ground (or the area
clear), and a fixed run duration agreed. Verify target reception, startup,
bridge timeout, USB unplug and measured stopping latency. End each run with zero.
No flashing or motor commands were performed during this implementation.

## Official references checked

- [Jazzy QoS API](https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/qos.py)
- [Jazzy Node and create_timer API](https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/node.py)
- [Jazzy TwistStamped definition](https://github.com/ros2/common_interfaces/blob/jazzy/geometry_msgs/msg/TwistStamped.msg)
- [pySerial 3.5 API](https://github.com/pyserial/pyserial/blob/v3.5/documentation/pyserial_api.rst)

The Linux pySerial backend is the intended transport. Other platforms are not
claimed to work because file locking and virtual-terminal tests use POSIX APIs.
