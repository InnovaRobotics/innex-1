# innex_teleop

Drive the INNEX-1 rover from a game controller plugged into the laptop.

## Launch

Plug in the controller. Build and source the workspace, then run this command.

```bash
ros2 launch innex_teleop joy.launch.py
```

The launch file starts two nodes:

- `game_controller_node` from `joy` reads the controller and publishes `/joy`.
- `teleop_node` from `teleop_twist_joy` turns `/joy` into velocity commands on `/cmd_vel`.

If either node exits, the launch stops both.

Plug in the controller before you start the launch. In a distrobox container, `game_controller_node` did not open a controller that was plugged in after it started. If the launch output has no `Opened game controller` line, stop the launch and start it again.

## Controls

| Control | What it does |
|---|---|
| Left shoulder button (LB or L1) | Enable. Hold it to drive. |
| Left stick, up and down | Drive forward and back. |
| Right stick, left and right | Turn left and right. |

The rover moves only while you hold the enable button. When you let go, `teleop_node` sends one zero command and then stops sending.

`game_controller_node` uses SDL's controller database, so the controls are the same on every controller that SDL recognises. To check that it found yours, look for `Opened game controller` in the launch output, or run:

```bash
ros2 run joy joy_enumerate_devices
```

## Speed limits

The limits live in `config/joy.yaml`. They are low starting values until the wheel test on blocks (INX-142).

| Parameter | Value | Meaning |
|---|---|---|
| `scale_linear.x` | 0.25 | Speed at full stick, in m/s |
| `scale_angular.yaw` | 0.4 | Turn rate at full stick, in rad/s |
| `enable_turbo_button` | -1 | No button raises the limits |

Rebuild the workspace after you change the file.

## Topics

| ROS topic | Type | Description |
|---|---|---|
| `/joy` | `sensor_msgs/msg/Joy` | Controller state. Sent on every change, and at 20 Hz while nothing changes. |
| `/cmd_vel` | `geometry_msgs/msg/TwistStamped` | Velocity command in `base_link`. Sent once for every `/joy` message while the enable button is held. |

The rover side must subscribe to `/cmd_vel` with best-effort QoS and a depth of 1, as INX-140 specifies. `teleop_node` publishes with reliable QoS and a depth of 10, and has no parameter to change that. A best-effort subscriber never gets a resent command, so it never acts on an old one.

## When commands stop

Letting go of the enable button is the only case that sends a zero command. In every other case the commands just stop:

- a node crashes
- the laptop loses its link to the rover
- the zero command is lost on the way

The rover side must then stop on its own. The Jetson bridge sends zero when no `/cmd_vel` arrives for 500 ms (INX-140).

Gazebo has no such timeout. If `/joy` stops while you hold the enable button, the simulated rover keeps its last command. To stop it, publish a zero command or restart the simulation.

Use a wired controller. If a wireless controller loses its connection, the driver keeps repeating the last stick position until the laptop notices that the controller has gone.

## Test

```bash
colcon build --packages-select innex_teleop
colcon test --packages-select innex_teleop
colcon test-result --verbose
```

The test needs no controller. It starts the launch file, publishes `/joy` messages itself and checks `/cmd_vel`.
