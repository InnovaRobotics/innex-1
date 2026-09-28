# Set up a Mac for development

This guide installs Ubuntu 24.04, ROS 2 Jazzy, and Gazebo Harmonic in a UTM virtual machine (VM), and Foxglove on macOS. It works on Apple silicon and Intel Macs.

## Before you begin

Check that your Mac meets these requirements:

| | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Free disk space | 50 GB | 80 GB |
| macOS | 13 (Ventura) | Latest |

It is recommended to keep the VM on the internal drive. A VM on an external drive runs slower, and the VM can become corrupted if the drive disconnects while the VM runs. UTM is relatively good with saving state and preventing corruption, however.

## Choose VM resources

Give the VM about half of your Mac's RAM and CPU cores:

| Mac RAM | VM memory |
|---|---|
| 8 GB | 4096 MiB |
| 16 GB or 18 GB | 8192 MiB |
| 24 GB or more | 12288 MiB |

For CPU cores, use half of your Mac's total cores, with a minimum of 4. To find your core count, click the Apple menu > **About This Mac** > **More Info** > **System Report** > **Hardware**, and read **Total Number of Cores**.

For example, an M3 Pro MacBook Pro with 18 GB of RAM and 11 cores uses 8192 MiB and 6 cores.

## 1. Download UTM and Ubuntu

1. Download UTM from [mac.getutm.app](https://mac.getutm.app) and move it to the **Applications** folder.
2. Download the Ubuntu 24.04 desktop image for your Mac:
    - Apple silicon: `ubuntu-24.04.5-desktop-arm64.iso` from [cdimage.ubuntu.com/releases/24.04/release](https://cdimage.ubuntu.com/releases/24.04/release/)
    - Intel: the latest `ubuntu-24.04.*-desktop-amd64.iso` from [releases.ubuntu.com/24.04](https://releases.ubuntu.com/24.04/)

## 2. Create the VM

1. Open UTM and click **Create a New Virtual Machine**.
2. Click **Virtualize**, and then click **Linux**.
3. Leave **Use Apple Virtualization** cleared.
4. Under **Boot ISO Image**, click **Browse** and select the Ubuntu image. Click **Continue**.
5. Enter the memory and CPU cores that you chose in [Choose VM resources](#choose-vm-resources).
6. Leave **Enable hardware OpenGL acceleration** cleared. Click **Continue**.
7. Set the storage size to `64` GB. Click **Continue**.
8. On the **Shared Directory** page, click **Continue**.
9. Enter `innex1-dev` as the name, and then click **Save**.

Caution: Don't turn on hardware OpenGL acceleration. Gazebo can't start its default renderer with it, and the other renderer flickers.

## 3. Install Ubuntu

1. Click the play button to start the VM.
2. Select **Try or Install Ubuntu** and press Enter.
3. Accept the defaults for language, accessibility, and keyboard.
4. On the network screen, leave **Use wired connection** selected. The VM uses your Mac's connection.
5. If the installer offers an update, click **Skip**.
6. Select **Install Ubuntu**, then **Interactive installation**, then **Default selection**.
7. On **How do you want to install Ubuntu?**, select **Erase disk and install Ubuntu**. This erases only the VM's virtual disk.
8. Enter your name, a computer name, a username, and a password. Use lowercase letters for the computer name and username.
9. Select your time zone, check the summary, and click **Install**.
10. When the installation finishes, click **Restart now**.
11. When the screen says `Please remove the installation medium, then press ENTER`, click the drive icon in the VM toolbar, and then click **Eject** for the CD/DVD drive. Click in the VM window and press Enter.
12. Log in to the desktop.
13. Open **Terminal** and install the SSH server:

    ```
    sudo apt update && sudo apt install -y openssh-server
    ```

If the VM starts the installer again after step 11, stop the VM, click **Edit** > **Drives**, clear the CD/DVD drive, and start the VM again.

## 4. Connect over SSH

We recommend that you run all remaining commands from a macOS terminal over SSH. You can copy and paste commands, and you can use VS Code with the Remote - SSH extension.

1. In the VM, find its IP address:

    ```
    hostname -I
    ```

    The address is usually `192.168.64.2` or `192.168.64.3`.

2. In a macOS terminal, connect to the VM:

    ```
    ssh USERNAME@IP_ADDRESS
    ```

    Replace `USERNAME` with your VM username and `IP_ADDRESS` with the address from step 1.

3. Type `yes` to accept the host key, and then enter your password.

Optional: To connect without a password, run `ssh-copy-id USERNAME@IP_ADDRESS` on your Mac.

## 5. Install ROS 2 Jazzy

1. Add the ROS 2 package repository:

    ```
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y software-properties-common curl
    sudo add-apt-repository -y universe
    export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
    curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.noble_all.deb"
    sudo dpkg -i /tmp/ros2-apt-source.deb
    sudo apt update
    ```

2. Install ROS 2, the build tools, Gazebo, and the Foxglove bridge:

    ```
    sudo apt install -y ros-jazzy-desktop ros-dev-tools ros-jazzy-ros-gz ros-jazzy-foxglove-bridge
    ```

3. Load ROS 2 in every new terminal:

    ```
    echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
    source ~/.bashrc
    ```

## 6. Test ROS 2 and Gazebo

1. In one SSH session, start a publisher:

    ```
    ros2 run demo_nodes_cpp talker
    ```

2. In a second SSH session, start a subscriber:

    ```
    ros2 run demo_nodes_py listener
    ```

    The subscriber prints `I heard: [Hello World: N]` once per second.

3. Press Ctrl+C in both sessions.
4. In the UTM window, open **Terminal** and start Gazebo:

    ```
    gz sim shapes.sdf
    ```

    A window opens with four shapes. Drag in the window to rotate the view.

5. Close Gazebo.

## 7. Install Foxglove

1. On your Mac, install Foxglove:

    ```
    brew install --cask foxglove-studio
    ```

    Alternatively, download it from [foxglove.dev/download](https://foxglove.dev/download).

2. In one SSH session, start the Foxglove bridge:

    ```
    ros2 launch foxglove_bridge foxglove_bridge_launch.xml
    ```

3. In a second SSH session, start the publisher:

    ```
    ros2 run demo_nodes_cpp talker
    ```

4. Open Foxglove and click **Open connection**.
5. Select **Foxglove WebSocket**, enter `ws://IP_ADDRESS:8765`, and click **Open**.
6. Click the **Topics** tab. The `/chatter` topic shows a rate of 1 Hz.
7. Press Ctrl+C in both SSH sessions.

## Troubleshooting

| Problem | Fix |
|---|---|
| The installer shows no network connection | Stop the VM. Click **Edit** > **Network**, set **Network Mode** to **Shared Network**, and start again. |
| The screen is black after installation | Stop the VM. Click **Edit** > **Display**, set **Emulated Display Card** to `virtio-ramfb`, and start again. |
| Gazebo flickers or shows black shapes | Stop the VM. Click **Edit** > **Display**, set **Emulated Display Card** to `virtio-gpu-pci`, and start again. |
| `ssh` says `Connection refused` or times out | The VM IP address changed, or the SSH server isn't installed. Run `hostname -I` in the VM and connect to the new address. |
| Gazebo opens and closes with an `OGRE EXCEPTION` | Hardware OpenGL is on. Set the display card to `virtio-gpu-pci`, as above. |
