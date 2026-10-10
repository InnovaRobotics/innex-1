# innex_sim

Gazebo Harmonic worlds for the INNEX-1 rover, based on the Lunabotics arena.

## World

`moon_yard` has a terrain mesh with three craters, nine rocks, walls, zone markers and the AprilTag beacon.

The world uses the `gz-sim-physics-system`, sensors (ogre2) and IMU systems. The launch file spawns the INNEX-1 rover from `innex_description` into the start zone.

## Launch

Build and source the workspace, then run one of these commands.

```bash
ros2 launch innex_sim moon_yard.launch.py
ros2 launch innex_sim moon_yard.launch.py gui:=false
```

The launch file also starts `robot_state_publisher`, spawns the rover and starts a `ros_gz_bridge` configured by `config/bridge.yaml`.

To run the world without ROS, source the workspace so the environment hook sets `GZ_SIM_RESOURCE_PATH`, then run `gz sim -r -s <path to world>.sdf` for a headless server.

## Rover

The rover spawns at the centre of the start zone, facing east. Set the spawn pose with the `x`, `y` and `yaw` launch arguments. The values are in the arena frame, in metres and radians.

```bash
ros2 launch innex_sim moon_yard.launch.py x:=1.5 y:=3.0 yaw:=0.5
```

The Gazebo `DiffDrive` system drives all four wheels as a skid steer. It limits the rover to 0.4 m/s and 0.8 rad/s. Forward acceleration is limited to 0.3 m/s², braking and reversing to 0.5 m/s², and turning to 0.6 rad/s². These are starting values until the wheel test on blocks (INX-142) measures the real rover.

To drive the rover from the keyboard, run this command in another terminal.

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -p frame_id:=base_link -p speed:=0.25 -p turn:=0.4
```

| ROS topic | Type | Direction | Description |
|---|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/TwistStamped` | to Gazebo | Velocity command. The bridge keeps only the latest command. |
| `/odom` | `nav_msgs/msg/Odometry` | from Gazebo | Wheel odometry in the `odom` frame. |
| `/tf` | `tf2_msgs/msg/TFMessage` | from Gazebo | The `odom` to `base_link` transform. |
| `/joint_states` | `sensor_msgs/msg/JointState` | from Gazebo | Wheel joint positions and velocities. |
| `/clock` | `rosgraph_msgs/msg/Clock` | from Gazebo | Simulation time. |

`robot_state_publisher` publishes the transforms from `base_link` to the wheels, using the simulation clock.

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

These terminals have no display. Set these variables first, then launch. The window opens on the VM desktop (the UTM window).

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
