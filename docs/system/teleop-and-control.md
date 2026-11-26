# Teleop and rover control

Every command that turns a wheel, lowers the bucket ladder or tips the dump bed passes through this subsystem. Teleop and rover control translate velocity and mechanism commands from either the operator's gamepad or the autonomy stack into physical motor signals, count wheel encoder pulses for [Localisation](localisation.md), and bring the rover to a stop whenever any link, computer or cable fails.

[`innex_teleop`](../../src/innex_teleop/README.md) reads the wired gamepad on the laptop, [`innex_drive_bridge`](../../src/innex_drive_bridge/README.md) converts `/cmd_vel` into USB serial wheel frames on the Jetson, and [`teensy_drive`](../../firmware/teensy_drive/README.md) parses those frames on the Teensy 4.1.

## Command path

A motion command starts either at the operator's gamepad on the mission control laptop or inside the autonomy software on the Jetson. Both publish the same message type: `geometry_msgs/msg/TwistStamped` on `/cmd_vel` in the `base_link` frame, specifying forward linear speed (in m/s) and yaw turn rate (in rad/s).

An onboard **command multiplexer (mux)** sits ahead of the drive bridge so each motor or actuator accepts input from one source at a time. If the gamepad and route follower published straight to the drive bridge simultaneously, the wheels would alternate rapidly between whichever message arrived last. A single selector prevents conflicting commands, lets an operator stop command override autonomy immediately, and blocks stray gamepad packets during a hands-free attempt.

From the selector, `innex_drive_bridge` converts body velocity into left and right wheel angular speed **setpoints** (in milliradians per second) and sends them at 50 Hz over USB serial to the Teensy 4.1. A setpoint specifies an absolute target (`500 mrad/s`) instead of a relative change (`+50 mrad/s`). Absolute targets keep wheel speeds predictable across dropped packets, because the next message states the exact target speed without accumulating missed steps.

## Serial packet format

A raw USB byte stream has no built-in message boundaries, and electrical noise from motor power cables can corrupt bits in transit. If the Teensy misinterpreted shifted bytes as a high-speed wheel target, the rover could move unexpectedly. [`PROTOCOL.md`](../../firmware/teensy_drive/PROTOCOL.md) prevents this by packing every command into a fixed 18-byte little-endian frame (`DR` version 1). Below is the startup arming frame (`seq = 1`, `left = 0`, `right = 0`) split into its six fields:

```text
44 52   01   00   01 00 00 00   00 00 00 00   00 00 00 00   be 37
^^^^^   ^^   ^^   ^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^^
 "DR"   v1  rsvd      seq       left mrad/s   right mrad/s  CRC-16
```

Reading from left to right: `44 52` (ASCII `DR`) and version `01` mark the frame header; `seq` is an unsigned 32-bit counter that increments with every packet; the two signed 32-bit integers hold left and right wheel targets; and `be 37` is a **CRC-16** checksum computed across bytes 0 to 15. If line noise flips a bit, the checksum fails and `DriveCore` on the Teensy disarms immediately. At power-up or after any timeout, `DriveCore` rejects non-zero targets until it receives a valid `(0, 0)` frame, preventing sudden motion if a cable connects while a sender is active.

## Stop at three layers

No single computer can detect its own freeze. If Linux hangs on the Jetson, a software timer inside the Jetson stops alongside it; if Wi-Fi drops in the arena, releasing a button on the laptop never reaches the rover. INNEX-1 therefore enforces stopping across three independent layers, where each layer catches failures in everything upstream of it:

1. Enable button on the laptop (`innex_teleop`): the gamepad node publishes `/cmd_vel` only while the operator holds LB/L1. Releasing the button sends one zero command and stops publishing, halting normal driving without waiting for a timeout.
2. Drive bridge on the Jetson (`innex_drive_bridge`, 500 ms watchdog): if no `/cmd_vel` arrives within 500 ms on the Jetson's monotonic clock, the bridge sends `(0, 0)` frames at 50 Hz. This catches a disconnected laptop, a dropped Wi-Fi link or a crashed teleop node.
3. Firmware on the Teensy 4.1 (`teensy_drive`, 250 ms watchdog): if 250 ms pass on `millis()` without a valid, advancing serial frame, `DriveCore` sets both targets to zero and disarms. Each Sabertooth 2x32 also enforces its own hardware serial timeout (100 to 250 ms) on the UART line from the Teensy. Together, this layer catches a frozen Jetson, a crashed bridge, a loose USB cable or corrupted serial data.

A timer that requires regular input and disables outputs when input stops is called a **watchdog**. On any fault or timeout, every layer sets outputs to zero instead of holding the previous value. Never disable or lengthen a watchdog timeout (see [Rover safety](../safety.md#during-a-run)). Accounting for the 500 ms bridge timeout, serial transmission and motor deceleration, stopping from the last valid command takes roughly 600 ms (at 0.25 m/s, the rover travels about 15 cm before braking starts).

Simulation models Layer 2 with `cmd_vel_watchdog`, which sits ahead of Gazebo's `DiffDrive` plugin and sends zero after 500 ms of silence. See [Simulation](simulation.md#the-gazebo-drive-plugin).

## Command freshness

Suppose Wi-Fi stalls for two seconds while the operator steers clear of a boulder, queuing twenty velocity messages in a buffer. Replaying that two-second backlog once the link recovers would drive the rover along outdated commands into the obstacle.

Two mechanisms prevent delayed replay. First, `innex_drive_bridge` (and `cmd_vel_watchdog` in simulation) subscribes to `/cmd_vel` with best-effort QoS and a queue depth of 1, discarding older buffered packets so only the most recent command is processed. Second, the bridge measures command age on the Jetson's local monotonic clock instead of comparing laptop and Jetson wall clocks, avoiding false timeouts when the two computers' clocks differ slightly. On the USB link, `DriveCore` checks the 32-bit sequence number and ignores duplicate or out-of-order frames without resetting its 250 ms watchdog.

## Skid-steer kinematics

INNEX-1 has six fixed paddle wheels and no steering linkages. Like a tracked vehicle, a **skid-steer** rover turns by driving its left three wheels and right three wheels at different speeds. Equal speeds drive straight; equal and opposite speeds turn on the spot.

Given forward velocity `v`, yaw rate `omega` (positive turning left under REP 103) and track width `track` between left and right wheel centres, each side's linear wheel speed is:

```text
left wheel speed  = v - (track / 2) * omega
right wheel speed = v + (track / 2) * omega
```

Dividing linear speed by the wheel radius gives angular velocity in radians per second. Because the front and rear axles sit half a metre ahead of and behind the middle axle, turning a rigid six-wheel chassis drags the front and rear tyres sideways across the surface. That lateral resistance reduces the actual turn rate relative to the `0.675 m` geometric track (in simulation, Gazebo uses a calibrated `0.717 m` effective wheel separation to match true yaw; on loose sand, slip increases further). [Localisation](localisation.md) covers how the gyroscope and LiDAR compensate for wheel slip.

## Quadrature encoders

To measure wheel rotation, each Gimson drive motor carries a Hall-effect **quadrature encoder**. A single-channel pulse sensor can measure rotation speed, whereas determining whether the wheel rolled forwards or backwards requires a second channel.

A quadrature encoder outputs two square-wave channels offset by a quarter cycle (90 degrees). When the wheel rotates forwards, channel A rises before channel B; in reverse, channel B rises before channel A. Hardware counters on the Teensy count every edge, track direction automatically and report cumulative counts for **wheel odometry**. Because Teensy 4.1 pins operate at 3.3 V only and are damaged by 5 V inputs, 5 V motor encoder signals must step down to 3.3 V before reaching the board.

## Excavation and dump actuators

The bucket ladder lowers into the sand, runs its 24 V BLDC chain drive to collect regolith, and raises clear of the surface. Dumping at the berm follows five steps:

1. Open the dump door.
2. Raise the dump bed.
3. Hold the raised position while sand slides clear.
4. Lower the dump bed.
5. Close the dump door.

All watchdog timeouts and single-source rules apply equally to the bucket ladder and dump actuators: if commands stop arriving, every actuator halts immediately. The Teensy enforces hardware limit switches and actuator travel bounds while the mission node on the Jetson coordinates the five-step sequence.

## Hardware E-stop

The latching red E-stop button disconnects battery power physically from all motor controllers and active subsystems. Treat it as an emergency hardware cut-off, never as normal braking; a rover that needs the E-stop to halt cleanly has a defect in its software stop path. Because resetting the E-stop must never resume motion automatically, the Teensy must detect when motor power drops and remain disarmed until a separate start command arrives.

## Rules and constraints

- Convert `/cmd_vel` commands in `base_link` into left and right wheel setpoints, operate excavation and dump actuators within end stops, and route all commands through one active source at a time.
- Stop every motor and actuator on enable-button release, link timeout or fault, and require a separate start command after any E-stop reset ([E-stop](../rules.md#e-stop), [Rover safety](../safety.md)).
- Accept zero commands from mission control during hands-free autonomy attempts ([Hands-free rules](../rules.md#hands-free-rules)).

## Further reading

- [`innex_teleop` README](../../src/innex_teleop/README.md), [`innex_drive_bridge` README](../../src/innex_drive_bridge/README.md) and [`teensy_drive` PROTOCOL.md](../../firmware/teensy_drive/PROTOCOL.md)
- [Quality of service settings](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
- [ros2_control diff_drive_controller](https://control.ros.org/jazzy/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html)
- [Teensy USB serial](https://www.pjrc.com/teensy/td_serial.html)
- [PlatformIO unit testing](https://docs.platformio.org/en/latest/advanced/unit-testing/index.html)
- [teleop_twist_joy](https://index.ros.org/p/teleop_twist_joy/) and [twist_mux](https://index.ros.org/p/twist_mux/)
