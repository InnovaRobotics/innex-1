# INNEX-1

INNEX-1 is the University of Leicester rover for UK Lunabotics 2027. The rover digs sand in the excavation zone, carries it to the construction zone and dumps it on the berm.

New to the team? Start with [ONBOARDING.md](ONBOARDING.md). It takes you from a clean computer to your first pull request.

## Find what you need

| If you want to | Read |
|---|---|
| Set up a computer and run the simulation | [ONBOARDING.md](ONBOARDING.md) |
| Learn how the rover works | [System design](docs/system-design.md) |
| Work safely near the rover | [Rover safety](docs/safety.md) |
| Get access to the Jetson | [Jetson](docs/jetson.md) |
| Check the competition rules | [Competition rules](docs/rules.md) |
| Look up a term | [Glossary](docs/glossary.md) |
| Open a pull request | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Choose a task | [Start here](https://linear.app/kjdotio/document/start-here-workstreams-and-how-we-work-92932ab7323b) in Linear |

## Packages

| Path | What it does |
|---|---|
| [`src/innex_description`](src/innex_description/README.md) | Six-wheel URDF/xacro robot model, sensor mounts and Gazebo plugins |
| [`src/innex_sim`](src/innex_sim/README.md) | Gazebo Harmonic Moon Yard arena, simulated sensors and `500 ms` `/cmd_vel` watchdog |
| [`src/innex_teleop`](src/innex_teleop/README.md) | Gamepad driver and `/cmd_vel` publisher with dead-man enable button |
| [`src/innex_drive_bridge`](src/innex_drive_bridge/README.md) | Jetson node translating `/cmd_vel` into `18`-byte USB serial wheel frames with a `500 ms` watchdog |
| [`src/innex_video`](src/innex_video/README.md) | Hardware H.264 camera streaming from front and rear OAK-D Pro units to Foxglove |
| [`firmware/teensy_drive`](firmware/teensy_drive/README.md) | Teensy 4.1 serial receiver, sequence checker and `250 ms` hardware watchdog |
