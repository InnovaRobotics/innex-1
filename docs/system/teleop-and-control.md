# Teleop and rover control

Every command that moves a wheel, lowers the bucket ladder or tips the dump bed passes through this subsystem. Teleop and rover control turn high-level motion commands from either the operator's gamepad or the autonomy software into physical motor and actuator signals, read wheel encoder counts back for [Localisation](localisation.md), and guarantee that the rover stops safely whenever anything goes wrong.

## Requirements

- Convert a rover velocity command into left and right skid-steer wheel setpoints.
- Operate the bucket ladder and dump bed mechanisms on command while respecting physical end stops.
- Stop every motor and actuator whenever commands stop arriving, the operator releases the enable button, or a fault occurs.
- Never restart motion automatically after an E-stop reset.
- Count wheel motor encoder pulses so other subsystems can compute wheel odometry.
- Route commands so every motor and actuator accepts input from one source at a time.

## Competition rules

- [E-stop](../rules.md#e-stop): one push disconnects the batteries from all controllers and active subsystems, and resetting the button must not restart the rover without a separate start command.
- [Hands-free rules](../rules.md#hands-free-rules): during an autonomous attempt, nobody in mission control can send commands to the rover.
- [Rover safety](../safety.md): the motor testing rules (E-stop in reach, wheels off the ground or clear area, fixed run duration, final zero command) apply to every rover test.

## How a command reaches the wheels

A motion command begins either at the operator's gamepad on the mission control laptop or inside the autonomy software on the Jetson. Both express motion the same way: a `geometry_msgs/msg/TwistStamped` message on `/cmd_vel` in the `base_link` frame, giving forward speed (in m/s) and turn rate (in rad/s).

Before commands reach the drive bridge, an onboard **command multiplexer (mux)** chooses which source has control. If the gamepad and navigation both published straight to the drive bridge at the same time, the wheels would snap back and forth between whichever message arrived last. Having a single onboard selector prevents conflicting commands, lets an operator stop override autonomy immediately, and blocks stray gamepad packets during hands-free runs.

From the selector, the Jetson drive bridge converts the velocity command into left and right wheel **setpoints** and sends them to the Teensy 4.1 over USB serial. A setpoint is an absolute target ("spin at 0.20 m/s"), not a relative change ("spin 0.05 m/s faster"). Absolute setpoints keep the rover predictable even if a packet drops, because the next message states the exact speed wanted without compounding missed increments. The Teensy turns those setpoints into control signals for the Sabertooth motor controllers, which power the four wheel motors.

## Stop at three layers

Never trust one computer to catch every failure. If a software bug freezes the Jetson, a timeout sitting inside the Jetson can't save you; if the Wi-Fi drops, releasing a button on the laptop never reaches the rover. That's why INNEX-1 stops at three independent layers, where each layer catches failures in everything upstream of it:

1. Enable button on the laptop: the gamepad node publishes motion only while the operator holds the dead-man enable button. Letting go immediately publishes a zero command. This layer stops the rover during normal driving without waiting on any timeout.
2. Drive bridge on the Jetson (500 ms watchdog): if no command arrives for 500 ms, the bridge sends zero setpoints to the Teensy. This catches a dead laptop, a dropped Wi-Fi link or a crashed gamepad node.
3. Teensy 4.1 firmware (250 ms watchdog): if no valid serial message arrives for 250 ms, the Teensy disables all motor and actuator outputs immediately. This catches a frozen Jetson, a crashed bridge, a loose USB cable or corrupt serial bytes.

A timer that expects regular input and shuts outputs off the moment input goes quiet is called a **watchdog**. On any fault or timeout, every layer forces outputs to zero; nothing ever holds the last commanded speed. Never disable or lengthen a watchdog timeout (see [Rover safety](../safety.md#during-a-run)). Because serial transit and controller deceleration follow the 500 ms bridge timeout, stopping from the last valid command takes roughly 600 ms (at 0.25 m/s, the rover travels about 15 cm before braking starts).

Watch out for one difference in [Simulation](simulation.md): Gazebo's `DiffDrive` plugin has no command timeout and keeps spinning at the last velocity forever if a publisher stops. Always test real stop behaviour on the bench and on blocks.

## Why old commands must not arrive late

Suppose Wi-Fi stalls for two seconds while the operator is steering away from a boulder, and the network queues up twenty velocity messages while waiting to reconnect. When the link recovers, replaying that two-second backlog drives the rover along commands from a moment that has already passed, straight into the wall.

To prevent stale replay, the drive bridge subscribes with a queue depth of 1, discarding older waiting messages and acting only on the newest command. The bridge measures command freshness using arrival time on the Jetson's local monotonic clock instead of comparing laptop and Jetson wall-clock timestamps, which avoids false dropouts when the two computers' clocks differ by a few milliseconds.

## Skid-steer turning

INNEX-1 has no steerable front wheels. Like a tracked vehicle, a **skid-steer** rover steers by spinning its left and right sides at different speeds. Equal speeds drive straight ahead; equal and opposite speeds spin the rover on the spot.

Given a forward speed `v`, a turn rate `omega` (positive turning left under REP 103) and the sideways distance `track` between the left and right wheels, each side's target linear speed is:

```text
left wheel speed  = v - (track / 2) * omega
right wheel speed = v + (track / 2) * omega
```

Dividing each speed by the wheel radius converts linear speed into wheel rotation rate. Turning a rigid four-wheel chassis forces the tyres to drag sideways across the sand, so the rover turns less than those equations predict. [Localisation](localisation.md) explains how that slip affects odometry and how the gyroscope and LiDAR compensate for it.

## Encoders and wheel odometry

To measure how far each wheel turned, the drive motors carry **quadrature encoders**. Suppose an encoder produced only a single stream of pulses as the wheel rotated: counting pulses would tell you how fast the wheel spun, never whether it rotated forwards or backwards.

A quadrature encoder solves this by producing two pulse trains offset by a quarter of a cycle (90 degrees). When the wheel spins forwards, channel A rises before channel B; when it reverses, channel B rises before channel A. The Teensy counts every edge in hardware, tracks direction automatically and sends cumulative counts back to the Jetson. Combining left and right wheel distances gives **wheel odometry**, an estimate of distance travelled and heading change that stays smooth over short intervals even though tyre slip makes it drift on sand.

## Dig and dump

The bucket ladder lowers into the sand, runs its chain to collect sand, and raises clear of the ground. Dumping follows a fixed five-step sequence:

1. Open the dump door.
2. Raise the dump bed.
3. Hold the raised position so sand clears the bed.
4. Lower the dump bed.
5. Close the dump door.

All watchdog and stop rules apply to the excavation and dump actuators too: if commands stop arriving, every actuator halts immediately. The proposed architecture lets the Teensy enforce hardware end stops and actuator safety limits while the mission node on the Jetson coordinates the five-step sequence.

## The E-stop

The red E-stop button disconnects battery power physically from all motor controllers and active subsystems. Treat it as a hard safety backstop, never as a normal way to stop the rover. A rover that needs someone to hit the E-stop to stop cleanly has a defect in its software stop path. Because resetting the E-stop must never resume motion on its own, the Teensy needs to know when power was cut and stay disarmed until a deliberate restart command arrives.

## Open questions

1. Does the Jetson side stay a standalone ROS 2 bridge node, or move to `ros2_control` with `diff_drive_controller`?
2. What exact binary serial protocol carries wheel setpoints, mechanism commands, encoder counts and Teensy armed/fault/E-stop state between the Jetson and Teensy?
3. Does the command mux extend `twist_mux` with a separate mechanism arbiter, or run as one unified mode node on the Jetson?
4. Which motor controller drives the 24 V excavation BLDC motor, and what control signal does the Teensy send it?
5. What physical feedback do the bucket ladder and dump bed provide (limit switches, encoders or motor current), and how does the rover confirm a full load or completed dump?
6. How does the Teensy detect an E-stop press and enforce the deliberate restart requirement when the Jetson stays powered on a separate battery?

## Further reading

- [ros2_control diff_drive_controller](https://control.ros.org/jazzy/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html)
- [Quality of service settings](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
- [Teensy USB serial](https://www.pjrc.com/teensy/td_serial.html)
- [PlatformIO unit testing](https://docs.platformio.org/en/latest/advanced/unit-testing/index.html)
- [teleop_twist_joy](https://index.ros.org/p/teleop_twist_joy/) and [twist_mux](https://index.ros.org/p/twist_mux/)
