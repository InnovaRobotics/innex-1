# Onboarding

This guide takes you from nothing to your first pull request.

## Contents

1. [Choose your path](#1-choose-your-path)
2. [Learn the basics](#2-learn-the-basics)
3. [Set up your computer](#3-set-up-your-computer)
4. [Check your setup](#4-check-your-setup)
5. [Build the workspace and run the sim](#5-build-the-workspace-and-run-the-sim)
6. [Read the safety rules](#6-read-the-safety-rules)
7. [Pick a task](#7-pick-a-task)
8. [Open your first pull request](#8-open-your-first-pull-request)
9. [Get help](#9-get-help)

## 1. Choose your path

| Path | What you work on | Sections |
|---|---|---|
| Software | ROS 2 nodes, teleoperation, simulation, perception | All |
| Firmware | The Teensy that controls the motors and actuators | 1, 2 and 6 to 9. For firmware setup, ask a lead. To use the sim, also do 3 to 5. |
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

## 5. Build the workspace and run the sim

Run these steps in your development environment: the VM on a Mac, or Ubuntu on Windows. On a Mac, use an SSH session to the VM.

1. Add an SSH key from your development environment to GitHub. You need it later to push your branch. Follow GitHub's guide to [adding a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account). To create the key and print the public key, run:

    ```
    ssh-keygen -t ed25519
    cat ~/.ssh/id_ed25519.pub
    ```

2. Set up rosdep, once per machine:

    ```
    sudo rosdep init
    rosdep update
    ```

    If `rosdep init` says the sources file already exists, carry on.

3. Create the workspace and clone the repo:

    ```
    mkdir -p ~/innex_ws/src
    cd ~/innex_ws/src
    git clone git@github.com:InnovaRobotics/innex-1.git
    ```

4. Install the dependencies from the workspace root:

    ```
    cd ~/innex_ws
    rosdep install --from-paths src --ignore-src -y
    ```

5. Build the workspace and load it:

    ```
    colcon build --symlink-install
    source install/setup.bash
    ```

    Add the workspace to your shell start-up file, so new terminals load it:

    ```
    echo "source ~/innex_ws/install/setup.bash" >> ~/.bashrc
    ```

    Run `colcon build` from `~/innex_ws` every time you change code. Never run it from inside `src`.

6. Run the tests:

    ```
    colcon test
    colcon test-result --verbose
    ```

    The summary line must show 0 errors and 0 failures.

7. Run the sim. On a Mac, run this in a terminal on the VM desktop (the UTM window). On Windows, run it in an Ubuntu terminal.

    ```
    ros2 launch innex_sim moon_yard.launch.py
    ```

    Gazebo opens with the arena and the rover in the start zone.

    From an SSH session, add `gui:=false`, because there is no display. In a second terminal, run `ros2 topic list` to check that the sim works. If the list shows only `/parameter_events` and `/rosout`, wait a few seconds and run it again.

8. Drive the rover. In a second terminal, run:

    ```
    ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -p frame_id:=base_link
    ```

    Press `i` to drive forward and `k` to stop. The sim rover keeps its last command until it gets another one, so press `k` before you close the window. Press Ctrl+C in each terminal to finish.

If a step fails, ask in Discord. Say which command you ran, and paste the exact error, as in [Get help](#9-get-help).

## 6. Read the safety rules

Read [docs/safety.md](docs/safety.md) before you work near the rover. This applies to software members too.

## 7. Pick a task

Tasks are in Linear. The [Start here](https://linear.app/kjdotio/document/start-here-workstreams-and-how-we-work-92932ab7323b) document explains how work is organised. Ask a lead to help you pick a task that fits your skills.

## 8. Open your first pull request

1. Go to the repo:

    ```
    cd ~/innex_ws/src/innex-1
    ```

2. Create a branch:

    ```
    git switch -c short-description
    ```

3. Make your change and commit it.
4. Push the branch.
5. Open a pull request on GitHub.

[CONTRIBUTING.md](CONTRIBUTING.md) tells you how to write the pull request, and how review and merging work. It also covers AI use.

## 9. Get help

Ask in the team Discord. Nobody expects you to know this already.

When you ask, say what you tried. Paste the exact error.
