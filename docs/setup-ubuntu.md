# Install ROS 2 on Ubuntu

Install ROS 2 Jazzy, Gazebo Harmonic and the Foxglove bridge on Ubuntu 24.04. Use this guide on a VM from [Set up a Mac](setup-mac.md), in WSL from [Set up Windows with WSL](setup-windows.md), or on Ubuntu directly.

Use the Ubuntu 24.04 desktop. Gazebo opens its window on the desktop.

## Add the ROS 2 package source

1. Update Ubuntu and enable the Universe repository:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y software-properties-common curl
   sudo add-apt-repository -y universe
   ```
2. Add the ROS 2 package source:
   ```bash
   export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
   curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.noble_all.deb"
   sudo dpkg -i /tmp/ros2-apt-source.deb
   sudo apt update
   ```

## Install ROS 2

1. Install ROS 2 Jazzy, the build tools, Gazebo and the Foxglove bridge:
   ```bash
   sudo apt install -y ros-jazzy-desktop ros-dev-tools ros-jazzy-ros-gz ros-jazzy-foxglove-bridge
   ```
   - `ros-jazzy-desktop` installs ROS 2 Jazzy with its GUI tools.
   - `ros-dev-tools` installs the tools for building ROS packages.
   - `ros-jazzy-ros-gz` installs Gazebo Harmonic, the version that Jazzy uses.
   - `ros-jazzy-foxglove-bridge` installs the Foxglove bridge.
2. Load ROS 2 in every new terminal:
   ```bash
   echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
   source ~/.bashrc
   ```
3. If you use WSL, also turn on software rendering. Gazebo can crash or show a black window on the WSL graphics driver. This setting makes Gazebo and RViz draw on the CPU.
   ```bash
   echo "export LIBGL_ALWAYS_SOFTWARE=1" >> ~/.bashrc
   source ~/.bashrc
   ```

## Test ROS 2

1. In one terminal, start a publisher:
   ```bash
   ros2 run demo_nodes_cpp talker
   ```
2. In a second terminal, start a subscriber:
   ```bash
   ros2 run demo_nodes_py listener
   ```
   The subscriber prints `I heard: [Hello World: N]` once per second.
3. Press Ctrl+C in both terminals.

## Test Gazebo

1. Start Gazebo:
   ```bash
   gz sim shapes.sdf
   ```
   A window opens and shows shapes. Drag in the window to rotate the view.

   On a Mac, run this command in a terminal on the VM desktop, which is the UTM window. On Windows, the window opens on your Windows desktop.
2. Close Gazebo.

## Test the Foxglove bridge

1. In one terminal, start the bridge:
   ```bash
   ros2 launch foxglove_bridge foxglove_bridge_launch.xml
   ```
2. In a second terminal, start the publisher:
   ```bash
   ros2 run demo_nodes_cpp talker
   ```
3. Open Foxglove. If you do not have it yet, install it from [foxglove.dev/download](https://foxglove.dev/download). Click **Open connection** and select **Foxglove WebSocket**.
   - If Foxglove runs on this machine, enter `ws://localhost:8765`.
   - If Foxglove runs on another computer, enter `ws://IP_ADDRESS:8765`. Use the address from `hostname -I` on this machine.
4. Click **Open**. Click the **Topics** tab. The `/chatter` topic shows 1 Hz.
5. Press Ctrl+C in both terminals.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ros-dev-tools` fails with dependency conflicts | Check the `Suites:` line in `/etc/apt/sources.list.d/ubuntu.sources`. It must include `noble-updates` and `noble-backports`. If it does not, change the line to `Suites: noble noble-updates noble-backports`. Then run `sudo apt clean && sudo apt update && sudo apt full-upgrade -y`. Install the packages again. |
| `ros2 topic list` shows only `/parameter_events` and `/rosout` | Wait a few seconds. Run the command again. |
| Gazebo opens and closes with an `OGRE EXCEPTION` | On WSL, check that `~/.bashrc` contains `export LIBGL_ALWAYS_SOFTWARE=1`. In a VM, check the display card setting in [Set up a Mac](setup-mac.md#troubleshooting). |
