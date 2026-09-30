# Agents

## Before you propose or change anything

- Read the official documentation for the exact version you're working with. Cite it.
- If the docs don't answer the question, search upstream issues and forums. Say what you confirmed and what you couldn't.
- Say what done means for the task before you start. Done always includes a build and the relevant tests.

## Versions

- Ubuntu 24.04, ROS 2 Jazzy, Python 3.12
- Gazebo Harmonic. The command is `gz`, not `ign`.
- Jetson: JetPack 7.2.1, Jetson Linux R39.2.1

Don't use answers written for Humble, Fortress or JetPack 6.

## Jetson

- Deploy a known commit to the Jetson. Don't edit code or install packages on it.
- Keep it in 25 W mode. Don't select MAXN SUPER (`nvpmodel -m 2`).
- Don't upgrade or unhold `nvidia-l4t-*` packages. Don't install firmware capsules.
- Flash the Jetson or the Teensy only when a person asks and is present.

## Motors and actuators

You can send velocity commands to the real rover only when all of these are true:

1. A person is present with the E-stop in reach.
2. The rover is on blocks with its wheels off the ground, or the test area is clear.
3. The run has a fixed duration. Ask for it. If nobody gives one, use 5 seconds.

During a run:

- Resend commands faster than the rover-side timeout. Never send one command and leave it running.
- Send a zero command when the run ends.
- Don't disable or lengthen the rover-side timeout.

## Always

- Open a pull request. Don't push to `main`.
- Follow `CONTRIBUTING.md` for branches, pull requests and commit messages.
- Ask before destructive actions: wiping storage, force pushing, deleting branches or files.
- Don't commit credentials, or put them in Discord or prompts.
