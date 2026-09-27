# Repo-local agent skills

Vendored from <https://github.com/arpitg1304/robotics-agent-skills/tree/main/skills> at commit `f9bc5467ff9ee3d23f1a1b0b29a649843bb6ad11` (2026-08-11). Upstream licence: Apache-2.0, kept in `ROBOTICS_AGENT_SKILLS_LICENSE`.

The ROS 1 skill is excluded. This is a ROS 2 Humble repository.

| Skill | Use for |
|---|---|
| `ros2` | Nodes, launch files, parameters, QoS, actions, lifecycle, Nav2, DDS, `colcon`, `package.xml`, rosdep |
| `robot-bringup` | Jetson bring-up, systemd, startup ordering, udev, watchdogs, log rotation |
| `robot-perception` | OAK-D, calibration, depth, AprilTags, Ouster/LiDAR, TF and extrinsics, sensor timing |
| `robotics-design-patterns` | State machines, heartbeats, fail-closed behaviour, hardware abstraction, sim-to-real |
| `robotics-software-principles` | Module boundaries, hardware interfaces, error handling, refactors that affect robot behaviour |
| `robotics-testing` | Unit, launch and integration tests, mock hardware, bag replay, HIL plans |
| `robotics-security` | SSH, router hardening, secrets, DDS security, E-stop, competition network exposure |
| `docker-ros2-development` | Dev container, CI images, DDS in containers, device passthrough |
| `ros2-web-integration` | Foxglove bridge, WebSockets, gamepad in browser, WebRTC/MJPEG |

Project-specific skills (hardware bring-up, rulebook compliance, evidence bags, conventions) will be added under `skills/innex-*` as the corresponding contracts and runbooks exist.

To refresh: clone upstream, copy the listed directories, update the commit hash above.
