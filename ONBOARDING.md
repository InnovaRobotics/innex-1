# Onboarding

This guide takes you from nothing to your first pull request.

## Contents

1. [Choose your path](#1-choose-your-path)
2. [Learn the basics](#2-learn-the-basics)
3. [Set up your computer](#3-set-up-your-computer)
4. [Check your setup](#4-check-your-setup)
5. [Read the safety rules](#5-read-the-safety-rules)
6. [Pick a task](#6-pick-a-task)
7. [Open your first pull request](#7-open-your-first-pull-request)
8. [Get help](#8-get-help)

## 1. Choose your path

| Path | What you work on | Sections |
|---|---|---|
| Software | ROS 2 nodes, teleoperation, simulation, perception | All |
| Firmware | The Teensy that controls the motors and actuators | 1, 2 and 5 to 8. For firmware setup, ask a lead. |
| Rover access | Code that runs on the Jetson and the rover | All, then [docs/jetson.md](docs/jetson.md) |

The software path needs no hardware.

## 2. Learn the basics

Learn what your first task needs. You can learn the rest later.

| Skill | Where to learn |
|---|---|
| Git and GitHub | [GitHub's Git guide](https://docs.github.com/en/get-started/getting-started-with-git) |
| The Linux command line | [Ubuntu's command line tutorial](https://ubuntu.com/tutorials/command-line-for-beginners) |
| Python | [The Python tutorial](https://docs.python.org/3.12/tutorial/) |
| ROS 2 | [ROS 2 Jazzy tutorials](https://docs.ros.org/en/jazzy/Tutorials.html). Start with the beginner CLI tools. |
| Gazebo | [Gazebo Harmonic tutorials](https://gazebosim.org/docs/harmonic/tutorials) |

Use material for ROS 2 Jazzy and Gazebo Harmonic. Material for ROS 2 Humble or Gazebo Fortress often doesn't work. [AGENTS.md](AGENTS.md#versions) lists the versions the project uses.

## 3. Set up your computer

Follow the guide for your computer:

- [Mac](docs/setup-mac.md)
- [Windows](docs/setup-windows.md)

On Ubuntu 24.04, follow sections 3 to 5 of the Windows guide. Leave out the `LIBGL_ALWAYS_SOFTWARE` line, because it's only for WSL.

## 4. Check your setup

The last sections of your setup guide test your setup. When they pass, you see:

- The listener print the talker's messages
- The shapes world in Gazebo
- The `/chatter` topic in Foxglove

If a check fails, use the troubleshooting table at the end of your guide. If that doesn't fix it, ask for help.

## 5. Read the safety rules

Read [docs/safety.md](docs/safety.md) before you work near the rover. This applies to software members too.

## 6. Pick a task

Tasks are in Linear. Ask a lead to help you pick a task that fits your skills.

## 7. Open your first pull request

1. Clone the repo:

    ```
    git clone git@github.com:InnovaRobotics/innex-1.git
    ```

2. Create a branch:

    ```
    git switch -c short-description
    ```

3. Make your change and commit it.
4. Push the branch.
5. Open a pull request on GitHub.

[CONTRIBUTING.md](CONTRIBUTING.md) tells you how to write the pull request, and how review and merging work. It also covers AI use.

## 8. Get help

Ask in the team Discord. Nobody expects you to know this already.

When you ask, say what you tried. Paste the exact error.
