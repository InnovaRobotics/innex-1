# Set up a Mac

Run Ubuntu 24.04 in a virtual machine (VM) on your Mac. Then install ROS 2 in the VM.

## Check your Mac

| | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Free disk space | 50 GB | 80 GB |
| macOS | 13 (Ventura) | Latest |

We recommend keeping the VM on the internal drive. An external drive is slower, and a disconnect while the VM runs can corrupt it. UTM saves state well, so an external drive does work.

## Choose the VM resources

| Mac RAM | Recommended VM memory |
|---|---|
| 8 GB | 4096 MiB |
| 16 GB or 18 GB | 8192 MiB |
| 24 GB or more | 12288 MiB |

We recommend half of your Mac's total cores, with a minimum of 4. To find the core count, click the Apple menu, then **About This Mac**. Click **More Info**, then **System Report**. Open **Hardware** and read **Total Number of Cores**.

## Download UTM and Ubuntu

1. Download UTM from [mac.getutm.app](https://mac.getutm.app). Move it to the Applications folder.
2. Download the Ubuntu 24.04 desktop image for your Mac.
   - Apple silicon: the latest `ubuntu-24.04.*-desktop-arm64.iso` from [cdimage.ubuntu.com](https://cdimage.ubuntu.com/ubuntu/releases/24.04/release/).
   - Intel: the latest `ubuntu-24.04.*-desktop-amd64.iso` from [releases.ubuntu.com/24.04](https://releases.ubuntu.com/24.04/).

## Create the VM

1. Open UTM. Click **Create a New Virtual Machine**.
2. Click **Virtualize**, then click **Linux**.
3. Keep **Use Apple Virtualization** cleared.
4. Under **Boot ISO Image**, click **Browse** and select the Ubuntu image. Click **Continue**.
5. Enter the memory and CPU cores from [Choose the VM resources](#choose-the-vm-resources).
6. Keep **Enable hardware OpenGL acceleration** cleared. Click **Continue**.
7. Set the storage size to 64 GB. Click **Continue**.
8. On the **Shared Directory** page, click **Continue**.
9. Enter `innex1-dev` as the name. Click **Save**.

Do not turn on hardware OpenGL acceleration. Gazebo cannot start its default renderer with it, and the other renderer flickers.

## Install Ubuntu

1. Click the play button to start the VM.
2. Select **Try or Install Ubuntu**, then press Enter.
3. Accept the defaults for language, accessibility and keyboard.
4. On the network screen, keep **Use wired connection** selected. The VM uses your Mac's connection.
5. If the installer offers an update, click **Skip**.
6. Select **Install Ubuntu**, then **Interactive installation**, then **Default selection**.
7. On **How do you want to install Ubuntu?**, select **Erase disk and install Ubuntu**. This erases only the VM's virtual disk.
8. Enter your name, a computer name, a username and a password. Use lowercase letters for the computer name and the username.
9. Select your time zone and check the summary. Click **Install**.
10. When the installation finishes, click **Restart now**.
11. When the screen says `Please remove the installation medium, then press ENTER`, click the drive icon in the VM toolbar. Click **Eject** for the CD/DVD drive. Click in the VM window, then press Enter.
12. Log in to the desktop.
13. Open **Terminal**. Install the SSH server:
    ```bash
    sudo apt update && sudo apt install -y openssh-server
    ```

If the VM starts the installer again after step 11, stop the VM. Click **Edit**, then **Drives**. Clear the CD/DVD drive, and start the VM again.

## Connect over SSH

Run the remaining commands from a macOS terminal over SSH. You can copy and paste commands there. VS Code with the Remote - SSH extension also works.

1. In the VM, find its IP address:
   ```bash
   hostname -I
   ```
   The address is usually `192.168.64.2` or `192.168.64.3`.
2. In a macOS terminal, connect to the VM. Replace `USERNAME` with your VM username. Replace `IP_ADDRESS` with the address from step 1.
   ```bash
   ssh USERNAME@IP_ADDRESS
   ```
3. Type `yes` to accept the host key. Enter your password.

To connect without a password, run `ssh-copy-id USERNAME@IP_ADDRESS` on your Mac.

## Install ROS 2 and Gazebo

Continue with [Install ROS 2 on Ubuntu](setup-ubuntu.md) in the VM. Then come back here to set up Foxglove.

## Set up Foxglove

1. Install Foxglove on your Mac:
   ```bash
   brew install --cask foxglove-studio
   ```
   Or download it from [foxglove.dev/download](https://foxglove.dev/download).
2. In the VM, start the bridge and the talker. Follow steps 1 and 2 in [Test the Foxglove bridge](setup-ubuntu.md#test-the-foxglove-bridge).
3. On your Mac, open Foxglove. Click **Open connection**.
4. Select **Foxglove WebSocket**. Enter `ws://IP_ADDRESS:8765`, using the VM address from [Connect over SSH](#connect-over-ssh). Click **Open**.
5. Click the **Topics** tab. The `/chatter` topic shows 1 Hz.
6. In the VM, press Ctrl+C in both terminals.

## Troubleshooting

| Problem | Fix |
|---|---|
| The installer shows no network connection | Stop the VM. Click **Edit**, then **Network**. Set **Network Mode** to **Shared Network**. Start the VM again. |
| The screen is black after installation | Stop the VM. Click **Edit**, then **Display**. Set **Emulated Display Card** to `virtio-ramfb`. Start the VM again. |
| Gazebo flickers or shows black shapes | Stop the VM. Click **Edit**, then **Display**. Set **Emulated Display Card** to `virtio-gpu-pci`. Start the VM again. |
| `ssh` says `Connection refused` or times out | The VM IP address changed, or the SSH server is not installed. Run `hostname -I` in the VM, and connect to the new address. |
| Gazebo opens and closes with an `OGRE EXCEPTION` | Hardware OpenGL is on. Set **Emulated Display Card** to `virtio-gpu-pci`, as above. |
