# innex_sim

Gazebo Harmonic worlds for the INNEX-1 rover, based on the Lunabotics arena.

## World

`moon_yard` has a terrain mesh with three craters, nine rocks, walls, zone markers and the AprilTag beacon.

The world uses the `gz-sim-physics-system`, sensors (ogre2) and IMU systems, so a rover can be added later.

## Launch

Build and source the workspace, then run one of these commands.

```bash
ros2 launch innex_sim moon_yard.launch.py
ros2 launch innex_sim moon_yard.launch.py gui:=false
```

The launch file also starts a `ros_gz_bridge` for `/clock`.

To run the world without ROS, source the workspace so the environment hook sets `GZ_SIM_RESOURCE_PATH`, then run `gz sim -r -s <path to world>.sdf` for a headless server.

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

## Open the GUI from an SSH or Zed terminal

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
