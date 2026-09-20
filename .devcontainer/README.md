# Dev container

One image for every machine. The image is built for amd64 and arm64, so it is the same on a Windows laptop (WSL2), an Apple Silicon Mac (arm64 VM) and the Jetson (arm64).

## Notes

- Base image is `ros:humble-ros-base-jammy` plus `ros-humble-desktop`. The `osrf/ros:humble-desktop` images are amd64-only; do not use them.
- `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` and `ROS_DOMAIN_ID=27` are set in the image. Every machine on the rover network, including the Jetson, uses the same values.
- `--network=host` is required for DDS discovery between the container and other machines.
- `--volume=/dev:/dev --privileged` exposes USB devices (Teensy, OAK-D) that the host or VM already sees. Pass the device to the VM first on macOS (Fusion: Virtual Machine > USB & Bluetooth) or attach it to WSL first on Windows (`usbipd attach --wsl --busid <id>`).
- GUI apps (RViz, `rqt`) display through the host X11 or WSLg socket. Foxglove runs natively on the host, not in the container.
- Set `ROS_SNAPSHOT` in `devcontainer.json` to a date from <http://snapshots.ros.org/humble/> to freeze the ROS apt repository. Do this before the competition build.

## CUDA on the Jetson

This image is CPU-only. Nodes that need CUDA (Isaac ROS, GPU AprilTag) run outside this container on the Jetson or in a separate L4T-based image. Keep `RMW_IMPLEMENTATION` identical across both.
