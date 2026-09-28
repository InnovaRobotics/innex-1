# Set up a Mac for development

This guide installs Ubuntu 22.04, ROS 2 Humble, and Gazebo Fortress in a UTM virtual machine (VM), and Foxglove on macOS. It works on Apple silicon and Intel Macs. Steps that differ for Intel Macs are marked.

## Before you begin

Check that your Mac meets these requirements:

| | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Free disk space | 50 GB | 80 GB |
| macOS | 13 (Ventura) | Latest |

Put the VM on the internal drive. A VM on an external drive runs slower, and the VM can become corrupted if the drive disconnects while the VM runs.

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
2. Download the Ubuntu 22.04.5 image for your Mac:
    - Apple silicon: `ubuntu-22.04.5-live-server-arm64.iso` from [cdimage.ubuntu.com/releases/22.04/release](https://cdimage.ubuntu.com/releases/22.04/release/)
    - Intel: `ubuntu-22.04.5-desktop-amd64.iso` from [releases.ubuntu.com/22.04](https://releases.ubuntu.com/22.04/)

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

### Apple silicon

1. Click the play button to start the VM.
2. Select **Try or Install Ubuntu Server** and press Enter.
3. Accept the defaults until you reach **Guided storage configuration**.
4. Clear **Set up this disk as an LVM group**. Click **Done**, and then click **Continue**.
5. Enter your name, a hostname, a username, and a password. Use lowercase letters for the hostname and username.
6. Skip Ubuntu Pro.
7. On **SSH configuration**, select **Install OpenSSH server**.
8. On **Featured server snaps**, click **Done** without selecting anything.
9. When the installation finishes, click **Reboot Now**.
10. When the screen stays black, click the drive icon in the VM toolbar, and then click **Eject** for the CD/DVD drive.
11. Stop the VM with the power button, and then start it again.
12. Log in at the text prompt.

If you leave LVM selected in step 4, the root partition uses only half of the disk.

### Intel

1. Click the play button to start the VM.
2. Select **Try or Install Ubuntu** and press Enter.
3. Click **Install Ubuntu** and accept the defaults.
4. Enter your name, a computer name, a username, and a password. Use lowercase letters for the computer name and username.
5. When the installation finishes, click **Restart Now**.
6. If the VM asks you to remove the installation medium, click the drive icon in the VM toolbar, click **Eject** for the CD/DVD drive, and then press Enter in the VM.
7. Log in to the desktop.
8. Open **Terminal** and run:

    ```
    sudo apt install -y openssh-server
    ```

## 4. Connect over SSH

We recommend that you run all remaining commands from a macOS terminal over SSH. You can copy and paste commands, and you can use VS Code with the Remote - SSH extension.

1. In the VM, find its IP address:

    ```
    hostname -I
    ```

    The address is usually `192.168.64.2`.

2. In a macOS terminal, connect to the VM:

    ```
    ssh USERNAME@IP_ADDRESS
    ```

    Replace `USERNAME` with your VM username and `IP_ADDRESS` with the address from step 1.

3. Type `yes` to accept the host key, and then enter your password.

Optional: To connect without a password, run `ssh-copy-id USERNAME@IP_ADDRESS` on your Mac.

## 5. Install the desktop (Apple silicon only)

Skip this section on an Intel Mac.

1. Install the desktop and the UTM guest agent:

    ```
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y ubuntu-desktop-minimal spice-vdagent
    sudo systemctl set-default graphical.target
    sudo reboot
    ```

2. In the UTM window, log in to the desktop.

After this, the VM display resizes with the window, and you can copy and paste between macOS and the VM.

## 6. Install ROS 2 Humble

1. Add the ROS 2 package repository:

    ```
    sudo apt install -y software-properties-common curl
    sudo add-apt-repository -y universe
    export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
    curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.jammy_all.deb"
    sudo dpkg -i /tmp/ros2-apt-source.deb
    sudo apt update
    ```

2. Install ROS 2, the build tools, Gazebo, and the Foxglove bridge:

    ```
    sudo apt install -y ros-humble-desktop ros-dev-tools ros-humble-ros-gz ros-humble-foxglove-bridge
    ```

3. Load ROS 2 in every new terminal:

    ```
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
    source ~/.bashrc
    ```

## 7. Test ROS 2 and Gazebo

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
    ign gazebo shapes.sdf
    ```

    A window opens with four shapes. Drag in the window to rotate the view.

5. Close Gazebo.

Gazebo Fortress uses the `ign` command. Commands that start with `gz` are for newer Gazebo versions.

## 8. Install Foxglove

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
| The installer says `autoconfiguration failed` on the network screen | Stop the VM. Click **Edit** > **Network**, set **Network Mode** to **Shared Network**, and start again. |
| The screen is black after the desktop installs | Stop the VM. Click **Edit** > **Display**, set **Emulated Display Card** to `virtio-ramfb`, and start again. |
| Gazebo flickers or shows black shapes | Stop the VM. Click **Edit** > **Display**, set **Emulated Display Card** to `virtio-gpu-pci`, and start again. |
| `ssh` says `Connection refused` or times out | The VM IP address changed. Run `hostname -I` in the VM and connect to the new address. |
| `apt` says `No space left on device` | LVM was selected during installation. Delete the VM and repeat from [Create the VM](#2-create-the-vm). |
