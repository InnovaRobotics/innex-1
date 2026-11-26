# Teleop and rover control

Every command that turns a wheel, lowers the bucket ladder or tips the dump bed passes through this subsystem. Teleop and rover control translate velocity and mechanism commands from either the operator's gamepad or the autonomy software into physical motor signals, count wheel encoder pulses for [Localisation](localisation.md), and force the rover to a stop whenever any link, computer or cable fails.

On `main` today, [`innex_teleop`](../../src/innex_teleop/README.md) reads a wired gamepad and publishes `/cmd_vel`, [`innex_drive_bridge`](../../src/innex_drive_bridge/README.md) converts `/cmd_vel` into `18`-byte USB serial frames on the Jetson with a `500 ms` watchdog, and [`teensy_drive`](../../firmware/teensy_drive/README.md) parses those frames on the Teensy 4.1 with a `250 ms` watchdog (`DryRunOutput` until Sabertooth bench wiring is connected). An onboard command selector (mux), wheel encoder feedback and bucket-ladder/dump-bed commands remain to be added.

## How a command reaches the wheels

A motion command begins either at the operator's gamepad on the mission control laptop or inside the autonomy stack on the Jetson. Both express motion in the same format: a `geometry_msgs/msg/TwistStamped` message on `/cmd_vel` in the `base_link` frame, giving forward linear speed (in m/s) and yaw turn rate (in rad/s).

Before autonomy joins teleop on the rover, an onboard **command multiplexer (mux)** has to sit ahead of the drive bridge and pick one active source at a time. Imagine what happens if the gamepad node and the route follower both publish straight to `/cmd_vel` together: the wheels jerk back and forth between whichever packet arrived last. Putting one selector in front of the bridge prevents conflicting commands, lets an operator stop override autonomy at once, and blocks stray gamepad input during a hands-free run.

From there, `innex_drive_bridge` converts the body velocity into left and right wheel angular speed **setpoints** (in milliradians per second) and streams them at `50 Hz` over USB serial to the Teensy 4.1. A setpoint states an absolute target (`spin at 500 mrad/s`) instead of a relative nudge (`spin 50 mrad/s faster`). Absolute targets keep the rover predictable across dropped packets, because the next frame states the exact wheel speed wanted without compounding missed steps.

## Inside the 18-byte serial frame

A raw USB byte stream has no natural packet boundaries, and electrical noise from motor wiring can flip bits in flight. If the Teensy misread a shifted byte as a full-speed wheel command, a 58.5 kg rover would lunge unpredictably. [`PROTOCOL.md`](../../firmware/teensy_drive/PROTOCOL.md) prevents that by wrapping every command into a fixed `18`-byte little-endian packet (`DR` version 1). Here is the startup arming packet (`seq = 1`, `left = 0`, `right = 0`) broken into its six fields:

```text
44 52   01   00   01 00 00 00   00 00 00 00   00 00 00 00   be 37
^^^^^   ^^   ^^   ^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^^
 "DR"   v1  rsvd      seq       left mrad/s   right mrad/s  CRC-16
```

Walk across the fields from left to right. `44 52` (ASCII `DR`) and version `01` mark the start of a frame; `seq` is a 32-bit counter that increases on every packet; the two signed 32-bit integers carry left and right wheel targets (capped at `+/-1000 mrad/s` until the block test); and `be 37` is a **CRC-16** checksum computed across the first 16 bytes. If noise alters a single bit, the checksum fails and `DriveCore` on the Teensy disarms at once. At startup or after any timeout, `DriveCore` refuses non-zero targets until it first receives a valid `(0, 0)` frame, so plugging a cable into a running host cannot launch the wheels unexpectedly.

## Stop at three layers

No single computer can catch its own freeze. If a kernel hang locks up the Jetson, a timer running on the Jetson freezes alongside it; if Wi-Fi drops in the arena, letting go of a button on the laptop never reaches the rover. That is why INNEX-1 stops across three independent layers, where each layer catches failures in everything upstream of it:

1. Dead-man enable button on the laptop (`innex_teleop`): the gamepad node publishes `/cmd_vel` only while the operator holds LB/L1. Releasing the button sends one zero command and stops publishing, halting normal driving without waiting for a timeout.
2. Drive bridge on the Jetson (`innex_drive_bridge`, `500 ms` watchdog): if no `/cmd_vel` arrives within `500 ms` on the Jetson's monotonic clock, the bridge switches to sending `(0, 0)` frames at `50 Hz`. This catches a dead laptop, a dropped Wi-Fi link or a crashed gamepad node.
3. Firmware on the Teensy 4.1 (`teensy_drive`, `250 ms` watchdog): if `250 ms` pass on `millis()` without a valid, advancing serial frame, `DriveCore` zeroes both targets and disarms. Each Sabertooth 2x32 also carries its own hardware serial timeout (`100` to `250 ms`) on the wire from the Teensy. Together, this layer catches a frozen Jetson, a crashed bridge, a pulled USB cable or corrupt bytes.

A timer that expects regular input and shuts outputs off the instant input goes quiet is called a **watchdog**. On any fault or timeout, every layer forces outputs to zero instead of holding the last speed. Never disable or lengthen a watchdog timeout (see [Rover safety](../safety.md#during-a-run)). Accounting for the `500 ms` bridge timeout plus serial transit and deceleration, stopping from the last valid command takes roughly `600 ms` on hardware (at `0.25 m/s`, the rover rolls about `15 cm` before braking begins).

Simulation models Layer 2 directly. Because Gazebo's `DiffDrive` plugin holds its last command forever on its own, `innex_sim` places a `cmd_vel_watchdog` node in front of Gazebo that sends zero after `500 ms` of silence. See [Simulation](simulation.md#the-gazebo-drive-plugin).

## Why old commands must not arrive late

Picture Wi-Fi stalling for two seconds while the operator steers around a boulder, with twenty velocity packets backed up in a send buffer. If the link recovers and replays that two-second queue in order, the rover executes turns from two seconds ago and drives straight into the obstacle.

Two rules prevent stale replay. First, `innex_drive_bridge` (and `cmd_vel_watchdog` in sim) subscribes to `/cmd_vel` with best-effort QoS and a queue depth of `1`, discarding older waiting packets so only the newest command survives. Second, the bridge measures command age using arrival time on the Jetson's local monotonic clock instead of comparing laptop and Jetson wall clocks, avoiding false timeouts when the two machines' clocks drift apart by tens of milliseconds. On the serial link, `DriveCore` checks the 32-bit sequence number and ignores duplicates or out-of-order frames without refreshing its `250 ms` timer.

## Skid-steer turning

INNEX-1 has six fixed paddle wheels and no steering linkages. Like a tracked excavator, a **skid-steer** rover turns by driving its left three wheels and right three wheels at different speeds. Equal speeds drive straight; equal and opposite speeds spin the rover on the spot.

Given a forward speed `v`, a yaw rate `omega` (positive turning left under REP 103) and the track width `track` between left and right wheel centres, each side's linear target is:

```text
left wheel speed  = v - (track / 2) * omega
right wheel speed = v + (track / 2) * omega
```

Dividing each linear speed by the wheel radius gives wheel angular velocity in radians per second. Because the front and rear axles sit half a metre ahead of and behind the middle axle, spinning a rigid six-wheel base forces the front and rear tyres to scrub sideways across the ground. That sideways drag resists the turn, so the rover rotates less per wheel revolution than the geometric `0.675 m` track predicts (in simulation, Gazebo uses a calibrated `0.717 m` effective separation to match true yaw; on loose sand, slip is larger still). [Localisation](localisation.md) explains how the gyroscope and LiDAR compensate for that slip.

## Encoders and wheel odometry

To measure how far each wheel rotated, the Gimson drive motors carry Hall-effect **quadrature encoders**. Suppose an encoder produced only one stream of pulses as a motor spun: counting pulses would tell you speed, never whether the wheel spun forwards or backwards.

A quadrature encoder fixes that ambiguity by outputting two pulse channels offset by a quarter cycle (90 degrees). When the wheel rolls forwards, channel A rises before channel B; in reverse, channel B leads channel A. Counting every edge in hardware on the Teensy tracks both distance and direction, and combining left and right wheel distances produces **wheel odometry** for [Localisation](localisation.md). Note that Teensy 4.1 pins operate at `3.3 V` only and are damaged by `5 V` signals, so `5 V` encoder lines must step down to `3.3 V` before reaching the board.

## Dig and dump

The bucket ladder lowers into the sand, runs its 24 V BLDC chain drive to collect regolith, and raises clear of the ground. Dumping at the berm follows a five-step sequence:

1. Open the dump door.
2. Raise the dump bed.
3. Hold the raised position while sand slides clear.
4. Lower the dump bed.
5. Close the dump door.

Every watchdog and single-source rule applies to the excavation and dump actuators alongside the wheels: if commands stop arriving, all actuators stop at once. In the planned split, the Teensy enforces hardware limit switches and current/travel bounds while the mission node on the Jetson steps through the sequence.

## The E-stop

The latching red E-stop button cuts battery power physically to all motor controllers and active subsystems. Treat it as an emergency hardware cut-off, never as routine braking; a rover that needs the E-stop to halt cleanly has a broken software stop path. Because resetting the E-stop must never resume motion on its own, the Teensy and drive path must detect when motor power drops and stay disarmed until the operator sends a separate start command.

## Requirements and competition rules

Subsystem requirements:

- Convert `/cmd_vel` commands in `base_link` into left and right skid-steer wheel setpoints.
- Operate the bucket ladder and dump bed on command within hardware end stops.
- Stop every motor and actuator when commands stop arriving, when the enable button is released, or on any fault.
- Require a separate, deliberate command before moving after an E-stop reset.
- Count wheel quadrature encoder pulses for wheel odometry.
- Route commands through a single selector so each motor or actuator has one command source at a time.

Applicable rules:

- [E-stop](../rules.md#e-stop): one push disconnects batteries from all controllers and active subsystems, and resetting the button must not restart motion automatically.
- [Hands-free rules](../rules.md#hands-free-rules): nobody in mission control may send commands to the rover during an autonomous attempt.
- [Rover safety](../safety.md): E-stop in reach, wheels on blocks or clear test area, agreed run duration, and a zero command at the end of every test.

## Open questions

1. How does the return serial frame from the Teensy to the Jetson pack cumulative encoder counts, armed state, fault flags and E-stop status alongside `DR` v1?
2. Does the onboard command selector combine `twist_mux` with a mechanism mode gate, or run as one unified arbiter node on the Jetson?
3. Which motor controller drives the 24 V excavation BLDC motor, and what signal does the Teensy send it?
4. What physical feedback do the bucket ladder and dump bed provide (limit switches, encoders or motor current), and how does software confirm a full load or completed dump?
5. How does the Teensy detect an E-stop cut and enforce the deliberate restart rule if compute stays powered on an isolated battery?

## Further reading

- [`innex_teleop` README](../../src/innex_teleop/README.md), [`innex_drive_bridge` README](../../src/innex_drive_bridge/README.md) and [`teensy_drive` PROTOCOL.md](../../firmware/teensy_drive/PROTOCOL.md)
- [Quality of service settings](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
- [ros2_control diff_drive_controller](https://control.ros.org/jazzy/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html)
- [Teensy USB serial](https://www.pjrc.com/teensy/td_serial.html)
- [PlatformIO unit testing](https://docs.platformio.org/en/latest/advanced/unit-testing/index.html)
- [teleop_twist_joy](https://index.ros.org/p/teleop_twist_joy/) and [twist_mux](https://index.ros.org/p/twist_mux/)
