# Decision log

One entry per decision. Newest at the bottom. A decision is reversed by a new entry, not by editing the old one.

Format: date, decision, why, consequences, evidence.

---

## D-001 Restart in a fresh repository; treat the 2026 repository as reference only

Date: 2026-09-19

Decision: Start `InnovaRobotics/innex-1` empty. Keep `KJdotIO/innex1-rover` read-only as a reference library.

Why: The 2026 stack was built against a simulated Leo Rover with different sensors, compute and kinematics, and grew tooling for a team that did not exist. The fail-closed safety design, hardware datasheets, June runbooks and the Teensy firmware are worth reading and re-deriving; the rest is not worth carrying.

Consequences: Nothing is copied without a decision-log entry naming what and why.

Evidence: Post-mortem discussion 2026-09-19; `docs/00-concept-of-operations.md`.

## D-002 Target score: teleop baseline first, autonomy in tiers

Date: 2026-09-19

Decision: Tier 0 inspections; Tier 1 teleop mission with zero arena cameras; Tier 2 excavation automation; Tier 3 dump automation; Tier 4 travel automation as stretch. No tier starts until the previous tier is demonstrated on the rover in sand.

Why: Berm productivity is ~80% of a good run. Zero arena cameras is 120 points per run for a working video link. Excavation and dump automation need no map. Travel automation (250) needs the full perception stack.

Consequences: Autonomy code is not written until Tier 1 is demonstrated.

Evidence: UK Lunabotics RuleBook 2026 v1.0, scoring section and example sheet.

## D-003 Platform: Ubuntu 22.04, ROS 2 Humble, pinned apt snapshot

Date: 2026-09-20

Decision: Humble on 22.04 on every machine including the Jetson (JetPack 6.x). Pin the ROS apt repository to a dated snapshot from snapshots.ros.org before the competition build. Do not migrate to Jazzy.

Why: The Jetson is on JetPack 6 (22.04). Humble EOL is May 2027 (REP-2000); EOL means no new packages, not breakage. A pinned snapshot makes the June 2027 build identical to the March 2027 build.

Consequences: `ROS_SNAPSHOT` build argument in `.devcontainer/Dockerfile`.

Evidence: REP-2000; Autoware's snapshot pinning pattern (autowarefoundation/autoware PR 6934).

## D-004 Development environment: one dev container on Ubuntu 22.04, per-host VM choice

Date: 2026-09-20

Decision: Every developer runs the same multi-arch dev image (`ghcr.io/innovarobotics/innex-1-dev`). Hosts: VMware Fusion Pro (free) with an arm64 Ubuntu 22.04 guest on Apple Silicon; WSL2 with WSLg on Windows; native on Linux. The Jetson is a deployment target, not a development machine.

Why: Fusion Pro is free for all use since 2025 and gives real GPU-backed OpenGL 4.3 in arm64 guests (kernel 5.19+, Mesa 22.1.1+; both available from 22.04 updates with the HWE kernel). Apple Silicon guests are arm64, the same architecture as the Jetson. `osrf/ros:humble-desktop` images are amd64-only, so the image is built from `ros:humble` plus `ros-humble-desktop`.

Consequences: `.devcontainer/`, `.github/workflows/dev-image.yml`, `docs/03-onboarding.md`.

Evidence: Broadcom KB 315602; Mesa svga3d docs; osrf/docker_images issue 729.

## D-005 Middleware: CycloneDDS everywhere, fixed domain ID, no multicast discovery over Wi-Fi

Date: 2026-09-20

Decision: `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`, `ROS_DOMAIN_ID=27` on every machine. Operator laptop and rover use unicast peer configuration or a discovery server; no multicast discovery over the competition Wi-Fi.

Why: Mismatched RMWs do not communicate. Multicast discovery is unreliable and chatty over Wi-Fi and counts against the 4,000 kbps budget.

Consequences: Set in the dev image; to be set in the Jetson environment and the operator laptop.

Evidence: Fast DDS "over Wi-Fi" guidance; NVIDIA forum reports of RMW mismatch with jetson-containers.

## D-006 Teleop video is encoded on the OAK-D cameras, not on the Jetson

Date: 2026-09-20

Decision: Use the DepthAI `VideoEncoder` (H.264 baseline, CBR ~1 Mbps, 720p, 15 fps, IDR every second) via `depthai-ros` (`i_low_bandwidth`, `i_publish_compressed`). The Jetson forwards the bitstream over RTP/UDP and republishes it as `foxglove_msgs/CompressedVideo` for recording and fallback display.

Why: The Jetson Orin Nano has no NVENC hardware encoder; software x264 would cost CPU cores. The camera encoder is free. Foxglove plays H.264 baseline natively and bags stay small.

Consequences: Primary operator view is a GStreamer RTP receiver (UDP); Foxglove over the WebSocket bridge is telemetry and fallback only.

Evidence: NVIDIA "Software Encode in Orin Nano"; Luxonis VideoEncoder docs; depthai-ros parameter docs (issue 718); Foxglove CompressedVideo docs.

## D-007 Firmware in C++ on Teensy 4.1 with PlatformIO; Jetson-side nodes in Python first

Date: 2026-09-20

Decision: Keep the Teensy 4.1. Firmware in Arduino-framework C++ built with PlatformIO, with protocol code unit-tested natively. ROS 2 nodes in Python (`rclpy`) unless a measured performance problem justifies C++.

Why: Teensy 4.1 has eight UARTs, CAN, and a friendly toolchain; 2026 failures were process, not hardware. Firmware is the right place to learn C++; `rclcpp` doubles the learning load for no gain at 50 Hz.

Consequences: `firmware/` uses PlatformIO. Pin map is one YAML that generates the C++ header and is read by the ROS bridge.

Evidence: 2026 `drivetrain_serial_firmware.ino`; PlatformIO Teensy docs.

## D-008 Organisation and tooling

Date: 2026-09-20

Decision: GitHub organisation `InnovaRobotics` (owner: KJdotIO; second owner to be added; ownership transfers on graduation). Linear for work tracking. Discord for communication. Bags and large evidence in the University OneDrive, never in git. Docs live in this repository only; the 2026 wikis are historical.

Why: Ownership must survive any one person leaving. One documentation home ends the 2026 problem of six disagreeing sources.

Consequences: This repository; Linear team INX; Discord channels `#getting-started`, `#software`, `#rover-log`, `#decisions`.

Evidence: Post-mortem discussion 2026-09-19.
