# INNEX-1

University of Leicester (Innova UoL) rover for UK Lunabotics 2027.

This repository is the single home for the 2027 software, firmware, documentation, runbooks and decisions. The 2026 repository ([KJdotIO/innex1-rover](https://github.com/KJdotIO/innex1-rover)) is a reference library, not a base.

## Status

Concept and planning. No rover software yet. Start with:

- [Concept of operations](docs/00-concept-of-operations.md): target score, mission, teleop concept, risks.
- [Decision log](docs/01-decisions.md): what we decided and why.
- [Current facts](docs/02-facts.md): hardware, versions and rules we build to.
- [Onboarding](docs/03-onboarding.md): set up a development machine in 30 minutes.

## Platform

| Item | Choice |
|---|---|
| OS / ROS | Ubuntu 22.04, ROS 2 Humble (pinned apt snapshot) |
| Compute | NVIDIA Jetson Orin Nano Super, JetPack 6.x |
| Microcontroller | Teensy 4.1 (PlatformIO, Arduino framework) |
| Simulation | Gazebo Fortress, kinematic stand-in only |
| Visualisation | Foxglove |
| Dev environment | Dev container (`.devcontainer/`) on Ubuntu 22.04: VMware Fusion on Apple Silicon, WSL2 on Windows, native on Linux |
| Tracking | Linear (work), GitHub (code, reviews), Discord (comms) |

## Rules of the repo

1. One owner per actuator. One launcher. Typed messages only.
2. No hardware claim without a bag or a bench reference.
3. Rulebook version and clause with every derived requirement.
4. Agents do not flash firmware, enable motors, merge, or touch the Jetson. See [AGENTS.md](AGENTS.md).
5. No credentials in the repo, in Discord, or in prompts.

## Licence

Apache-2.0. See [LICENSE](LICENSE). Vendored skills under `skills/` keep their upstream Apache-2.0 licence.
