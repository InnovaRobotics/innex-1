# Agents

## Before you change anything

1. Read the official documentation for the exact version you use. Cite it.
2. If the documentation does not answer the question, search upstream issues and forums.
3. State what you confirmed and what you could not confirm.
4. State what done means for the task before you start.
5. Done includes a build and the relevant tests.

## Versions

- Ubuntu 24.04, ROS 2 Jazzy, Python 3.12.
- Gazebo Harmonic. The command is `gz`, not `ign`.
- Jetson: JetPack 7.2.1, Jetson Linux R39.2.1.

Do not use answers written for Humble, Fortress or JetPack 6.

## Jetson

- Deploy a known commit to the Jetson.
- Do not edit code on the Jetson. Do not install packages on it.
- Keep the Jetson in 25 W mode.
- Do not select MAXN SUPER (`nvpmodel -m 2`).
- Do not upgrade or unhold `nvidia-l4t-*` packages.
- Do not install firmware capsules.
- Flash the Jetson or the Teensy only when a person asks and is present.

## Motors and actuators

You can send velocity commands to the real rover only when all of these are true:

1. A person is present with the E-stop in reach.
2. The rover is on blocks with its wheels off the ground, or the test area is clear.
3. The run has a fixed duration. Ask for it. If nobody gives one, use 5 seconds.

During a run:

- Resend commands faster than the rover-side timeout.
- Never send one command and leave it running.
- Send a zero command when the run ends.
- Do not disable or lengthen the rover-side timeout.

## Always

- Open a pull request. Do not push to `main`.
- Follow [CONTRIBUTING.md](CONTRIBUTING.md) for branches, pull requests and commit messages.
- Ask before destructive actions: wiping storage, force pushing, deleting branches or files.
- Do not commit credentials. Do not put credentials in Discord or in prompts.
