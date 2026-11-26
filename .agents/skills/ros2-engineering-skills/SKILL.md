---
name: ros2-engineering-skills
description: >
  ROS 2 Jazzy engineering guidance: rclcpp/rclpy, colcon/ament, XML/Python launch,
  QoS/DDS, tf2/URDF, Gazebo simulation, sensors, perception, Nav2, safety watchdogs,
  and testing. Use for ROS 2 development, code review, and debugging.
license: Apache-2.0
metadata:
  author: dbwls99706
  version: "1.9.1-trimmed"
  repository: "https://github.com/dbwls99706/ros2-engineering-skills"
---

# ROS 2 Engineering Skills

Trimmed from `dbwls99706/ros2-engineering-skills` (v1.9.1, Apache-2.0) to the references
that apply to INNEX-1 (Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic, JetPack 7.2.1).
Load only the reference file needed for the current task.

## Operating contract

1. Read `AGENTS.md` and `REVIEW.md` first; keep reviews read-only.
2. Verify installed package versions and upstream Jazzy docs before changing code.
3. Diagnose from observed endpoints (`ros2 topic info -v`, logs, tests) before editing.
4. Keep changes minimal: prefer built-in ROS 2 primitives (timers, QoS, XML launch) over custom wrappers.
5. Never describe unit or simulation passes as hardware-readiness proof; physical motion requires an operator and independent stop path.

## Reference router

| Task | Read |
|---|---|
| Cross-cutting principles, Jazzy distro table, QoS starting points | `references/engineering-principles.md` |
| Workspace, `package.xml`, `colcon`, `ament_cmake` / `ament_python` | `references/workspace-build.md` |
| Nodes, executors, callback groups, clean `SIGINT`/`SIGTERM` shutdown | `references/nodes-executors.md` |
| Topics, services, actions, custom interfaces, QoS/DDS | `references/communication.md` |
| Launch format selection (XML first), arguments, conditions | `references/launch-system.md` |
| `tf2`, URDF/xacro, `robot_state_publisher`, REP 103/105 frames | `references/tf2-urdf.md` |
| Gazebo Harmonic, `ros_gz_bridge`, `/clock` simulation time | `references/simulation.md` |
| Cameras, LiDAR, depth, AprilTags, perception pipelines | `references/perception.md` |
| Sensor drivers, clock sync, extrinsics | `references/sensor-integration.md` |
| Nav2, SLAM, costmaps, behaviour trees | `references/navigation.md` |
| Bring-up, `/dev/serial/by-id`, `udev`, watchdogs | `references/system-bringup.md` |
| E-stop, fail-closed stop paths, command arbitration | `references/safety-estop.md` |
| Unit tests, `pytest`, `launch_testing`, verification levels | `references/testing.md` |
