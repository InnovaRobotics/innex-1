# innex_drive_bridge

Initial Python ROS 2 Jazzy node skeleton for INX-140.

The node logs `Drive bridge started.`, waits for ROS callbacks and releases
resources when interrupted. It does not subscribe to `/cmd_vel`, convert wheel
speeds, open USB serial or command motors. The 500 ms watchdog is not implemented.

## Build and run

From the Ubuntu 24.04 workspace root:

```bash
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -y
colcon build --symlink-install --packages-select innex_drive_bridge
source install/setup.bash
ros2 run innex_drive_bridge bridge_node
```

Expect `Drive bridge started.`. Stop with Ctrl+C.

## Test

```bash
colcon test --packages-select innex_drive_bridge
colcon test-result --verbose
```

The generated tests check copyright, formatting and docstrings. They do not
verify bridge behaviour because this PR introduces only the node lifecycle.

## Remaining INX-140 work

- Agree the architecture and serial protocol with the firmware owner.
- Subscribe to fresh TwistStamped commands with best-effort QoS and depth 1.
- Convert body velocity into wheel targets using configurable geometry.
- Add the independent 500 ms command timeout and corresponding unit tests.
- Implement bounded serial writes, sequence numbers and safe session recovery.
- Add launch/parameter files and perform the required USB bench validation.

No hardware access is needed to run this skeleton.

Package structure follows the [ROS 2 Jazzy package tutorial](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html).
