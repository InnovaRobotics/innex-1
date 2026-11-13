# innex_sim

Gazebo Harmonic worlds for the INNEX-1 rover, based on the Lunabotics arena.

## World

`moon_yard` has a terrain mesh, craters, rocks, walls, zone markers and the AprilTag beacon.

The world uses the `gz-sim-physics-system`, sensors (ogre2) and IMU systems. The launch file spawns the INNEX-1 rover from `innex_description` into the start zone.

## Launch

[Build and source the workspace](../../ONBOARDING.md#build-the-workspace-and-run-the-simulation), then run one of these commands.

```bash
ros2 launch innex_sim moon_yard.launch.py
ros2 launch innex_sim moon_yard.launch.py gui:=false
```

The launch file also starts `robot_state_publisher`, spawns the rover, and starts `cmd_vel_watchdog` and a `ros_gz_bridge` configured by `config/bridge.yaml`. If `cmd_vel_watchdog` or `ros_gz_bridge` exits, the launch stops the whole simulation.

To run the world without ROS, [source the workspace](../../ONBOARDING.md#build-the-workspace-and-run-the-simulation) so the environment hook sets `GZ_SIM_RESOURCE_PATH`, then run `gz sim -r -s <path to world>.sdf` for a headless server.

## Rover

The rover spawns at the centre of the start zone, facing east. Set the spawn pose with the `x`, `y` and `yaw` launch arguments. The values are in the arena frame, in metres and radians.

```bash
ros2 launch innex_sim moon_yard.launch.py x:=1.5 y:=3.0 yaw:=0.5
```

The Gazebo `DiffDrive` system drives all four wheels as a skid steer. It limits the rover to 0.4 m/s and 0.8 rad/s. The limiter acts on changes in velocity, so speeding up forwards and slowing down in reverse are limited to 0.3 m/s², and slowing down forwards and speeding up in reverse to 0.5 m/s². Turning is limited to 0.6 rad/s². These are starting values until a wheel test on blocks measures the real rover.

The wheels have dry friction with no slip compliance, so the rover holds its position on a slope and when it stands still. The friction coefficient is 1 in the rolling direction and 0.5 along the axle. A skid steer drags its wheels sideways to turn, and the lower sideways friction lets the wheels drag. The model's mass sits forward of the wheel centre, so the rover turns on the spot about its front axle. It turns 3 to 4 per cent less than the wheel odometry reports.

The `/odom` topic starts at zero where the rover spawns, so it's relative to the spawn pose, not the arena frame.

Drive the rover by publishing `geometry_msgs/msg/TwistStamped` on `/cmd_vel`.

| ROS topic | Type | Direction | Description |
|---|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/TwistStamped` | to `cmd_vel_watchdog` | Velocity command in `base_link`. |
| `/cmd_vel_watchdog/cmd_vel` | `geometry_msgs/msg/TwistStamped` | to Gazebo | The commands that reach Gazebo. Only `cmd_vel_watchdog` publishes here. `ros_gz_bridge` keeps only the latest command. |
| `/odom` | `nav_msgs/msg/Odometry` | from Gazebo | Wheel odometry in the `odom` frame. |
| `/tf` | `tf2_msgs/msg/TFMessage` | from Gazebo | The `odom` to `base_link` transform. |
| `/joint_states` | `sensor_msgs/msg/JointState` | from Gazebo | Wheel joint positions and velocities. |
| `/clock` | `rosgraph_msgs/msg/Clock` | from Gazebo | Simulation time. |

`robot_state_publisher` publishes the transforms from `base_link` to the wheels, using the simulation clock.

## When commands stop

`DiffDrive` has no command timeout. It keeps the last command until a new one arrives. So `cmd_vel_watchdog` sits between `/cmd_vel` and Gazebo, as the drive bridge on the Jetson does on the rover (INX-140):

- It forwards each `/cmd_vel` message to `/cmd_vel_watchdog/cmd_vel`, which `ros_gz_bridge` sends to Gazebo.
- If no `/cmd_vel` arrives for 500 ms, it sends zero, and sends it again every 500 ms until commands return.
- It subscribes with best-effort QoS and a depth of 1, so it acts only on the newest command.
- It times the 500 ms on the wall clock, not the simulation clock, because the commands come from the laptop.

The rover starts to slow down 500 ms after the last command. The `DiffDrive` limits then set how long it takes to stop. From 0.25 m/s it takes another 0.5 s forwards, or 0.8 s in reverse.

Publish only on `/cmd_vel`. Anything that publishes on `/cmd_vel_watchdog/cmd_vel` bypasses the timeout.

## Arena frame

The origin is the south-west interior corner of the arena, at the sand surface. The x axis points east along the 7.9 m length. The y axis points north along the 4.4 m width. The z axis points up. The arena interior covers x 0 to 7.9 and y 0 to 4.4.

This x axis matches the X axis in rulebook Figure 2. The rulebook measures Y down from the beacon corner, so `y = 4.4 - Y_rulebook`.

## Zones

| Zone | Centre (x, y) | Size (x by y) | Colour |
|---|---|---|---|
| Start | 1.0, 3.4 | 2.0 by 2.0 | green |
| Construction | 1.3, 0.75 | 2.6 by 1.5 | blue |
| Berm target | 1.3, 0.75 | 1.5 by 0.9 | red |
| Excavation | 6.525, 2.2 | 2.75 by 4.4 | pink |

The markers are visual only and have no collision. The obstacle zone has no marker. We assume it is the area between the start and construction zones and the excavation zone.

## Rocks and craters

The rock and crater positions approximate rulebook Figure 2. The judges randomise them, so treat the layout as an example. The tests keep every rock inside the arena and outside the start zone.

The AprilTag beacon position and height are not confirmed with the organisers.

## Walls

The walls are simulation geometry only. The rules forbid using them for mapping, navigation or collision avoidance.

## Regenerate the meshes

The terrain and rock meshes are not in git. `colcon build` runs `scripts/generate_assets.py`, which uses only the Python standard library, and writes them to the build directory. The install step then copies them to `share/innex_sim/models`. The script uses fixed seeds, so each run writes identical files.

To change the craters or rocks, edit the lists in the script and rebuild.

To inspect the meshes, run the script with an output directory:

```bash
python3 src/innex_sim/scripts/generate_assets.py --output-dir /tmp/innex_models
```

## Open the GUI from an SSH or VS Code terminal

These terminals have no display. Someone must be logged in to the VM desktop first, because the `XAUTHORITY` file exists only for a desktop session. Set these variables, then launch. The window opens on the VM desktop (the UTM window).

```bash
export DISPLAY=:0
export XAUTHORITY=$(ls /run/user/1000/.mutter-Xwaylandauth.* | head -1)
ros2 launch innex_sim moon_yard.launch.py
```

You can also run the launch from a terminal on the VM desktop.

## Test

```bash
colcon build --packages-select innex_sim
colcon test --packages-select innex_sim
colcon test-result --verbose
```

The tests need `gz` on the path, so source the ROS 2 Jazzy setup first.
