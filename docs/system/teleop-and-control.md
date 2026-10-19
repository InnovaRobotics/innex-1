# Teleop and rover control

Teleop turns commands into wheel and actuator motion. This page covers the path from the gamepad, or from the autonomy software, to the motors. It also covers how the rover stops.

## Requirements

- Turn a velocity command into left and right wheel speeds.
- Move the bucket ladder and the dump bed on command.
- Stop every output when commands stop arriving, when the operator releases the enable button, or when a fault occurs.
- Report wheel motion as encoder counts, so other software can estimate distance.
- Give each motor and actuator exactly one source of commands.

## Rules

- [E-stop](../rules.md#e-stop): one push stops all motion and disconnects the batteries from all controllers.
- [Hands-free rules](../rules.md#hands-free-rules): during an autonomous attempt, nobody can send commands to the rover.
- [Rover safety](../safety.md): the motor rules apply to all rover work.

## Command path

A command starts at the gamepad on the mission control laptop, or in the autonomy software on the Jetson. It reaches the Jetson as a `/cmd_vel` message. A node on the Jetson converts the message into left and right wheel setpoints. It sends the setpoints to the Teensy over USB serial. The Teensy signals the Sabertooth controllers, and they drive the motors.

Velocity commands use `/cmd_vel`, with the message type `geometry_msgs/msg/TwistStamped` and the frame `base_link`. A setpoint is an absolute target, such as a wheel speed or an actuator position. It is not a change from the last value.

Each motor and actuator has exactly one source of commands. If two sources command the same wheel, the rover follows whichever message arrived last. That behaviour is hard to predict or test. Something must choose between the gamepad and autonomy before the bridge. That choice is a command mux. Where it runs is an open question.

## Stop at three layers

Each layer that can fail must be able to stop the rover.

1. The laptop sends motion only while the operator holds the enable button. Releasing the button stops the rover. This layer needs no network.
2. The bridge on the Jetson sends zero if no command arrives for 500 ms. This layer catches a dead laptop, a dropped link or a crashed node.
3. The Teensy stops its motor outputs if no valid message arrives for 250 ms. This layer catches a crashed Jetson, a stalled bridge, a loose cable and corrupt messages.

On a fault, the outputs stop. They do not hold the last value. A watchdog is a timer that expects regular input and acts when the input stops. Do not lengthen or remove a timeout. See [Rover safety](../safety.md#during-a-run).

The sim works differently. Gazebo's `DiffDrive` plugin has no command timeout. It keeps the last command until a new one arrives, so a stopped publisher does not stop the sim rover. See [Simulation](simulation.md).

## Old commands must not arrive late

A command that arrives two seconds late describes where the operator wanted to go two seconds earlier. Queued commands make this worse. After a network stall, the rover would replay the backlog.

The bridge subscribes with a queue depth of 1. It acts only on the newest command. A sequence number on each serial message lets the Teensy drop a message that is older than one it has already used.

## Skid-steer turning

A skid-steer rover has no steering mechanism. The wheels on each side turn at one speed, and the rover turns by driving the two sides at different speeds. Equal speeds drive straight. Opposite speeds turn on the spot.

Left wheel speed is the forward speed minus half the track width times the turn rate. Right wheel speed is the forward speed plus the same amount. The wheel radius converts each speed into a rotation rate.

Dragging the wheels sideways across sand means the rover turns less than the arithmetic says. [Localisation](localisation.md) covers the effect on odometry.

## Encoders and wheel odometry

A quadrature encoder gives two pulse trains a quarter cycle apart. The Teensy counts the pulses and finds the direction of rotation. The counts per wheel revolution convert rotation into distance. Combining the left and right distances over time gives wheel odometry. Wheel odometry estimates how far the rover has moved and which way it faces. The estimate drifts when the wheels slip.

## Dig and dump

The bucket ladder lowers into the sand and raises again. The dump sequence has five steps:

1. The door opens.
2. The bed raises.
3. The bed holds its raised position.
4. The bed lowers.
5. The door closes.

The stop rules apply to the mechanisms too. If commands stop, the actuators stop.

## The E-stop

The E-stop disconnects the batteries from all controllers. Software must not depend on it. A rover that stops safely only because someone pressed the button has a fault in its software path. Resetting the E-stop must not restart the rover. A separate, deliberate command restarts it.

## Open questions

1. Does the Jetson side use `ros2_control` with `diff_drive_controller`, or a plain ROS node?
2. What is the serial message format between the Jetson and the Teensy? How does each side detect a corrupt or out-of-order message?
3. Where does the command mux run, and which command sources does it choose between?
4. Which controller drives the excavation BLDC motor, and how does the Teensy command it?
5. What feedback do the bucket ladder and the dump bed give: limit switches, encoders or motor current?
6. How does the rover know that the bucket ladder has collected enough, or that a dump has finished?
7. Does the Jetson stay powered when the E-stop is pressed? If it does, which battery powers it?

## Further reading

- [ros2_control diff_drive_controller](https://control.ros.org/jazzy/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html)
- [Quality of service settings](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
- [Teensy USB serial](https://www.pjrc.com/teensy/td_serial.html)
- [PlatformIO unit testing](https://docs.platformio.org/en/latest/advanced/unit-testing/index.html)
- [teleop_twist_joy](https://index.ros.org/p/teleop_twist_joy/) and [twist_mux](https://index.ros.org/p/twist_mux/)
