# Teleop and rover control

This page answers how a command becomes wheel or mechanism motion, and how the rover stops. It covers the command path from the gamepad or the autonomy software to the motors and actuators. See [System design](../system-design.md) for where it sits in the whole rover.

## What it must do

- Turn a velocity command into left and right wheel speeds.
- Move the bucket ladder and the dump bed on command.
- Stop every output when commands stop arriving, when the operator releases the enable button, or when something faults.
- Report wheel motion back as encoder counts, so other software can estimate how far the rover moved.
- Give each motor and actuator exactly one source of commands.

## Inputs and outputs

The operator's gamepad and [Navigation and mission](navigation-and-mission.md) both send commands into this subsystem. [Comms and mission control](comms.md) carries the operator's commands across the link.

Velocity commands travel on `/cmd_vel`, as `geometry_msgs/msg/TwistStamped` with `frame_id` `base_link`. The Jetson turns them into setpoints for the Teensy. A setpoint is an absolute target, such as a wheel velocity or an actuator position. It isn't a change from the last value.

The subsystem gives [Localisation](localisation.md) wheel encoder counts, which become wheel odometry.

## Rules that apply

- [E-stop](../rules.md#e-stop): one push stops all motion and disconnects the batteries from all controllers.
- [Hands-free rules](../rules.md#hands-free-rules): during an autonomous attempt, nobody can send commands to the rover.
- [Autonomy conditions](../rules.md#autonomy-conditions): the hands-free boundary decides when teleop hands over to autonomy.
- [Rover safety](../safety.md) and [AGENTS.md](../../AGENTS.md#motors-and-actuators): the motor rules apply to all rover work.

## Hardware

- Jetson Orin Nano Super: runs the Robot Operating System 2 (ROS 2) side of the command path.
- Teensy 4.1: counts encoder pulses, sends motor controller signals and stops its outputs when commands stop.
- Four Gimson GR-WM4 worm gear motors with Hall-effect quadrature encoders, driven by two Sabertooth 2x32 motor controllers.
- A StepperOnline 24 V geared brushless DC (BLDC) motor for the bucket ladder.
- 24 V linear actuators on Cytron MD10C or MDD10A drivers for the dump bed and its door.

## The chain from command to wheels

A command starts at the gamepad on the mission control laptop, or in the autonomy software on the Jetson. It reaches the Jetson as a `/cmd_vel` message. A node on the Jetson converts it to left and right wheel setpoints and sends them over USB serial to the Teensy. The Teensy signals the Sabertooth controllers, and the controllers drive the motors.

Each motor or actuator has exactly one node or task that commands it. If two sources could command the same wheel, the rover would follow whichever message arrived last, and that behaviour is hard to predict or test. Something must therefore choose between the gamepad and autonomy before the command reaches the bridge. That choice is a command mux (multiplexer). Where it runs is an open question.

## Why the rover stops at three layers

Every layer that can fail needs a way to stop the rover when it fails.

- The laptop sends motion only while the operator holds the gamepad's enable button. Releasing the button stops the rover. This catches the operator letting go, and it needs no network.
- The bridge on the Jetson sends zero if no further command arrives for 500 ms. This catches a dead laptop, a dropped link or a crashed node.
- The Teensy stops its motor outputs if no valid message arrives for 250 ms. This catches a crashed Jetson, a bridge that stalls, a cable that comes loose, and corrupt messages.

On a fault, outputs stop. They don't hold the last value. A watchdog, which is a timer that expects regular input and acts when the input stops, implements the timeouts. Never lengthen or remove a timeout, as [rover safety](../safety.md#during-a-run) says.

The sim behaves differently. Gazebo's `DiffDrive` keeps the last command until the next one arrives, so a stopped publisher doesn't stop the sim rover. See [Robot model and simulation](simulation.md).

## Why old commands must never arrive late

A command that arrives 2 seconds late describes where the operator wanted to go 2 seconds ago. Queueing commands makes this worse, because the rover replays a backlog after a network stall. Command topics use a quality of service (QoS) setting that keeps only the newest command, and the bridge acts on the latest message only. The Jazzy page on [quality of service settings](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html) explains the options. A sequence number on each serial message is one way to let the Teensy drop a message that is older than one it already used.

## Skid steer turning

A skid-steer rover has no steering mechanism. The wheels on each side turn at the same speed, and the rover turns by driving the left and right sides at different speeds. Equal speeds drive straight. Opposite speeds turn on the spot. The conversion from `/cmd_vel` has two terms. Left wheel speed is the forward speed minus half the track width times the turn rate. Right wheel speed is the forward speed plus the same amount. Wheel radius converts each speed to a rotation rate.

Skid-steer turning drags the wheels sideways across the sand, so the rover usually turns less than the arithmetic says. [Localisation](localisation.md) covers what this does to odometry.

## Encoders and wheel odometry

A quadrature encoder gives two pulse trains offset by a quarter cycle, so the Teensy can count the pulses and tell which direction the wheel turned. Counts per wheel revolution convert wheel rotation into distance. Combining the left and right distances over time gives wheel odometry: an estimate of where the rover has moved and which way it faces. The estimate drifts when the wheels slip.

## Dig and dump

The bucket ladder lowers into the sand and raises again. The dump bed sequence has five steps:

1. The door opens.
2. The bed raises.
3. The bed holds its raised position.
4. The bed lowers.
5. The door closes.

The same rules for stopping apply to the mechanisms. If commands stop, the actuators stop.

## The E-stop

The E-stop disconnects the batteries from all controllers. Software must not depend on it, and the E-stop doesn't replace software stops. A rover that stops safely only because someone pressed the button has a fault in its software path. Resetting the E-stop must not restart the rover. Restarting needs a separate, deliberate command.

## Open questions

1. Does the Jetson side use `ros2_control` with `diff_drive_controller`, or a plain ROS node?
2. What is the serial message format between the Jetson and the Teensy, and how does each side detect a corrupt or out-of-order message?
3. Where does the command mux run, and which command sources does it choose between?
4. Which controller drives the excavation BLDC motor, and how does the Teensy command it?
5. What feedback do the bucket ladder and the dump bed give: limit switches, encoders or motor current?
6. How does the rover know the bucket ladder has collected enough, or that a dump has finished?
7. Does the Jetson stay powered when the E-stop is pressed, and if so, from which battery?

## Read more

- [ros2_control diff_drive_controller](https://control.ros.org/jazzy/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html)
- [Quality of service settings](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
- [Teensy USB serial](https://www.pjrc.com/teensy/td_serial.html)
- [PlatformIO unit testing](https://docs.platformio.org/en/latest/advanced/unit-testing/index.html)
- [teleop_twist_joy](https://index.ros.org/p/teleop_twist_joy/) and [twist_mux](https://index.ros.org/p/twist_mux/)
- [QPL drive mux configuration](https://github.com/jsmith-exe/lunabotics/blob/main/qpl_ws/src/qpl_rover/config/drive_mux.yaml)
- [Iowa State net-adapter](https://github.com/Cardinal-Space-Mining/lance-2026/tree/main/net-adapter)
