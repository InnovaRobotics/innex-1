# Onboarding

## Choose your path

| Path | You work on | Sections to read |
|---|---|---|
| Software | ROS 2 code, teleop, simulation and perception | All sections |
| Firmware | Teensy code for the motors and actuators | Get access, Learn the basics, Read the safety rules, Pick a task, Open your first pull request, and Get help. Ask a lead for firmware setup. To use the simulation, also read the setup sections. |
| Rover access | Code that runs on the Jetson or the rover | All sections, then [Jetson](docs/jetson.md) |

The software path needs no hardware.

## Get access

Ask a lead for each of these before you start.

- Membership of the InnovaRobotics GitHub organisation. You need it to push a branch.
- An invitation to the INNEX1 Rover team in Linear.
- An invitation to the team Discord. This repo does not hold the invite link.
- For rover access only: a Tailscale account, and a lead who shares the Jetson with you.

Then create an SSH key for GitHub. Follow GitHub's guide to [adding a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).

1. Create the key:
   ```bash
   ssh-keygen -t ed25519
   ```
2. Print the public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
3. Add the public key in GitHub under **Settings** > **SSH and GPG keys**.

## Learn the basics

Learn what your first task needs. Leave the rest until later.

| Skill | Start with |
|---|---|
| Git and GitHub | [GitHub's Git guide](https://docs.github.com/en/get-started/getting-started-with-git) |
| The Linux command line | [Ubuntu's command line tutorial](https://ubuntu.com/tutorials/command-line-for-beginners) |
| Python | [The Python tutorial](https://docs.python.org/3.12/tutorial/) |
| ROS 2 | [ROS 2 Jazzy tutorials](https://docs.ros.org/en/jazzy/Tutorials.html). Start with the beginner command line tools. |
| Gazebo | [Gazebo Harmonic tutorials](https://gazebosim.org/docs/harmonic/tutorials) |

Use only ROS 2 Jazzy and Gazebo Harmonic material. Material for ROS 2 Humble or Gazebo Fortress often does not work with this project.

## Set up your computer

Follow the guide for your computer:

- Mac: [Set up a Mac](docs/setup-mac.md)
- Windows: [Set up Windows with WSL](docs/setup-windows.md)
- Ubuntu 24.04: [Install ROS 2 on Ubuntu](docs/setup-ubuntu.md)

On a Mac or a Windows PC, you should install Ubuntu first. Then continue with the Ubuntu guide inside the virtual machine or WSL.

## Check your setup

The Ubuntu guide includes three checks. You should see:

- The listener prints the talker's messages.
- Gazebo shows shapes.
- The `/chatter` topic appears in Foxglove.

If a check fails, use the troubleshooting table in the guide. If the table does not solve the problem, [ask for help](#get-help).

## Build the workspace and run the simulation

Run these steps in your Ubuntu environment. On a Mac, use an SSH session to the virtual machine. On Windows, use an Ubuntu terminal.

1. Set up rosdep. Do this once for each computer.
   ```bash
   sudo rosdep init
   rosdep update
   ```
   If `rosdep init` says the sources file already exists, go to the next step.

2. Create the workspace and clone the repo.
   ```bash
   mkdir -p ~/innex_ws/src
   cd ~/innex_ws/src
   git clone git@github.com:InnovaRobotics/innex-1.git
   ```

3. Install the dependencies from the workspace root.
   ```bash
   cd ~/innex_ws
   rosdep install --from-paths src --ignore-src -y
   ```

4. Build the workspace and load it.
   ```bash
   colcon build --symlink-install
   source install/setup.bash
   ```
   Add the workspace to your start-up file, so every new terminal loads it:
   ```bash
   echo "source ~/innex_ws/install/setup.bash" >> ~/.bashrc
   ```
   Run `colcon build` from `~/innex_ws` each time you change code. Do not run it from inside `src`.

5. Run the tests.
   ```bash
   colcon test
   colcon test-result --verbose
   ```
   The summary line must show 0 errors and 0 failures.

6. Start the simulation. On a Mac, run this command in a terminal on the VM desktop, which is the UTM window. On Windows, run it in an Ubuntu terminal.
   ```bash
   ros2 launch innex_sim moon_yard.launch.py
   ```
   Gazebo opens with the arena. The rover is in the start zone.

   From an SSH session, add `gui:=false`. An SSH session has no display. In a second terminal, run `ros2 topic list`. If the list shows only `/parameter_events` and `/rosout`, wait a few seconds and run the command again.

When the simulation runs, read [System design](docs/system-design.md) to see how the parts fit together.

## Read the safety rules

Read [Rover safety](docs/safety.md) before you work near the rover.

## Pick a task

Tasks are in Linear. [Start here](https://linear.app/kjdotio/document/start-here-workstreams-and-how-we-work-92932ab7323b) explains the workstreams, milestones and sprints. Ask a lead which workstream to join. Then ask its owner for a first issue.

## Open your first pull request

1. Change to the repo:
   ```bash
   cd ~/innex_ws/src/innex-1
   ```
2. Create a branch:
   ```bash
   git switch -c short-description
   ```
3. Make your change. Commit it.
4. Push the branch.
5. Open a pull request on GitHub. Fill in both headings of the template.

[CONTRIBUTING.md](CONTRIBUTING.md) explains how to write the description, how review works, and how to use AI tools.

## Get help

Ask in the team Discord. Say which command you ran and what you tried. Paste the exact error.
