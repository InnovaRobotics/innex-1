# Set up a Windows PC for development

This guide installs Ubuntu 22.04, ROS 2 Humble, and Gazebo Fortress in Windows Subsystem for Linux (WSL), and Foxglove on Windows.

## Before you begin

Check that your PC meets these requirements:

| | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Free disk space | 50 GB | 80 GB |
| Windows | 10, build 19044 or later | 11 |

To check your Windows build, press Windows+R, enter `winver`, and press Enter.

Before you start:

1. Install all updates in **Settings** > **Windows Update**, including optional updates. Restart until no updates remain.
2. Update your graphics driver from the Intel, AMD, or NVIDIA website.

WSL uses up to half of your RAM and all of your CPU cores by default. You don't need to set these.

## 1. Install WSL and Ubuntu

1. Right-click **Start** and click **Terminal (Admin)**. On Windows 10, click **Windows PowerShell (Admin)**.
2. Install WSL and Ubuntu 22.04:

    ```
    wsl --install -d Ubuntu-22.04
    ```

3. If Windows asks you to restart, restart, and then run the command again.
4. When the Ubuntu window opens, enter a username and a password. Use lowercase letters for the username.
5. In the admin terminal, check that Ubuntu uses WSL 2:

    ```
    wsl -l -v
    ```

    The `VERSION` column for `Ubuntu-22.04` shows `2`.

If WSL was already installed, run `wsl --update` before step 2.

## 2. Open Ubuntu

To open an Ubuntu terminal, open **Terminal**, click the down arrow next to the tab, and click **Ubuntu 22.04 LTS**.

Run all remaining commands in an Ubuntu terminal unless a step says otherwise.

We recommend that you edit code in VS Code with the WSL extension. To open a folder in VS Code from Ubuntu, run `code .` in that folder.

## 3. Install ROS 2 Humble

1. Update Ubuntu:

    ```
    sudo apt update && sudo apt upgrade -y
    ```

2. Add the ROS 2 package repository:

    ```
    sudo apt install -y software-properties-common curl
    sudo add-apt-repository -y universe
    export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
    curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.jammy_all.deb"
    sudo dpkg -i /tmp/ros2-apt-source.deb
    sudo apt update
    ```

3. Install ROS 2, the build tools, Gazebo, and the Foxglove bridge:

    ```
    sudo apt install -y ros-humble-desktop ros-dev-tools ros-humble-ros-gz ros-humble-foxglove-bridge
    ```

4. Load ROS 2 and turn on software rendering in every new terminal:

    ```
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
    echo "export LIBGL_ALWAYS_SOFTWARE=1" >> ~/.bashrc
    source ~/.bashrc
    ```

Gazebo Fortress crashes on the WSL graphics driver. `LIBGL_ALWAYS_SOFTWARE=1` makes Gazebo and RViz render on the CPU.

## 4. Test ROS 2 and Gazebo

1. In one Ubuntu terminal, start a publisher:

    ```
    ros2 run demo_nodes_cpp talker
    ```

2. In a second Ubuntu terminal, start a subscriber:

    ```
    ros2 run demo_nodes_py listener
    ```

    The subscriber prints `I heard: [Hello World: N]` once per second.

3. Press Ctrl+C in both terminals.
4. Start Gazebo:

    ```
    ign gazebo shapes.sdf
    ```

    A window opens on your Windows desktop with four shapes. Drag in the window to rotate the view.

5. Close Gazebo.

Gazebo Fortress uses the `ign` command. Commands that start with `gz` are for newer Gazebo versions.

## 5. Install Foxglove

1. Download the Windows installer from [foxglove.dev/download](https://foxglove.dev/download) and run it.
2. In one Ubuntu terminal, start the Foxglove bridge:

    ```
    ros2 launch foxglove_bridge foxglove_bridge_launch.xml
    ```

3. In a second Ubuntu terminal, start the publisher:

    ```
    ros2 run demo_nodes_cpp talker
    ```

4. Open Foxglove and click **Open connection**.
5. Select **Foxglove WebSocket**, enter `ws://localhost:8765`, and click **Open**.
6. Click the **Topics** tab. The `/chatter` topic shows a rate of 1 Hz.
7. Press Ctrl+C in both Ubuntu terminals.

## Troubleshooting

| Problem | Fix |
|---|---|
| `wsl --install` says virtualisation isn't enabled | Restart into your BIOS or UEFI settings and turn on virtualisation. It's often called Intel VT-x, AMD-V, or SVM. |
| WSL says `This version of Windows does not support the packaged version` | Windows isn't fully updated. Install all updates, including optional updates, and restart. |
| Gazebo opens and closes with an `OGRE EXCEPTION` | Software rendering isn't on. Run `source ~/.bashrc`, or check that `~/.bashrc` contains `export LIBGL_ALWAYS_SOFTWARE=1`. |
| No window opens for Gazebo | In an admin terminal, run `wsl --update` and then `wsl --shutdown`. Open Ubuntu again. |
| Foxglove can't connect to `localhost` | In Ubuntu, run `hostname -I`. In Foxglove, use `ws://IP_ADDRESS:8765` with the first address. |
| Windows is slow while Ubuntu runs | Limit WSL memory. Create `C:\Users\YOUR_NAME\.wslconfig` with the lines `[wsl2]` and `memory=6GB`. In an admin terminal, run `wsl --shutdown`. |
