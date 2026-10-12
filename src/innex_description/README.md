# innex_description

URDF description of the INNEX-1 rover, written as xacro.

The model has a chassis and four wheels on continuous joints. `innex_1.gazebo.xacro` adds the Gazebo friction, drive and joint state plugins.

## Frames

`base_link` sits on the ground midway between the wheels. The x axis points forward, the y axis points left and the z axis points up, following REP 103 and REP 105.

## Dimensions and masses

The dimensions come from the June 2026 CAD. INX-138 replaces them with measurements of the rover. The masses are estimates until the rover is weighed.

## View the model

Build and source the workspace, then run each command in its own terminal.

```bash
ros2 launch innex_description description.launch.py
ros2 run joint_state_publisher joint_state_publisher
ros2 run foxglove_bridge foxglove_bridge
```

Connect Foxglove to `ws://localhost:8765`.

To drive the model in Gazebo, see the `innex_sim` README.
