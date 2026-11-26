# innex_description

URDF description of the rover, written as xacro.

The model has an enclosed, rounded-edge chassis (with front bucket-ladder overhang and a raised central Ouster platform) and six paddle wheels on continuous joints. Collision geometry uses plain boxes and smooth cylinders to keep Gazebo physics fast. `innex_1.gazebo.xacro` adds the Gazebo friction, drive and joint state plugins.

## Frames

`base_link` sits on the ground directly beneath the middle axle. The x axis points forward, the y axis points left and the z axis points up, following REP 103 and REP 105.

## Dimensions and masses

The dimensions come from the November 2026 INNEX-2 Master CAD (`0.02`), and the masses come from the Mechanical Team SDR (`58.5 kg` empty including sensors). Measurements of the assembled rover replace them.

## View the model

[Build and source the workspace](../../ONBOARDING.md#build-the-workspace-and-run-the-simulation), then run each command in its own terminal.

```bash
ros2 launch innex_description description.launch.xml
ros2 run joint_state_publisher joint_state_publisher
ros2 run foxglove_bridge foxglove_bridge
```

Connect Foxglove to `ws://localhost:8765`.

To drive the model in Gazebo, see the `innex_sim` README.
