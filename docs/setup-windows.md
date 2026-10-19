# Set up Windows with WSL

Run Ubuntu 24.04 inside Windows Subsystem for Linux (WSL). Then install ROS 2 in Ubuntu.

## Check your PC

| | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Free disk space | 50 GB | 80 GB |
| Windows | 10, version 2004 (build 19041) or later, or 11 | 11 |

To check your Windows build, press Windows+R, enter `winver`, and press Enter.

Before you start:

1. Install all updates in **Settings** > **Windows Update**, including optional updates. Restart until no updates remain.
2. Update your graphics driver from the Intel, AMD or NVIDIA website.

By default, WSL uses up to half of your RAM and all of your CPU cores. You do not need to change this. Limit the memory only if Windows slows down while Ubuntu runs.

## Install WSL and Ubuntu

1. Right-click **Start**. Click **Terminal (Admin)**. On Windows 10, click **Windows PowerShell (Admin)**.
2. Install WSL and Ubuntu 24.04:
   ```
   wsl --install -d Ubuntu-24.04
   ```
3. If Windows asks you to restart, restart. Then run the command again.
4. When the Ubuntu window opens, enter a username and a password. Use lowercase letters for the username.
5. In the admin terminal, check that Ubuntu uses WSL 2:
   ```
   wsl -l -v
   ```
   The `VERSION` column for `Ubuntu-24.04` shows `2`.

If WSL is already installed, run `wsl --update` before step 2.

## Limit WSL memory (optional)

Use this only if Windows runs slowly while Ubuntu runs.

1. Create the file `C:\Users\YOUR_NAME\.wslconfig`. Add these lines:
   ```
   [wsl2]
   memory=6GB
   ```
2. In an admin terminal, run `wsl --shutdown`. Then open Ubuntu again.

## Open Ubuntu

To open an Ubuntu terminal, open **Terminal**. Click the down arrow next to the tab. Click **Ubuntu 24.04 LTS**.

Run the remaining commands in an Ubuntu terminal. To edit code, use VS Code with the WSL extension. To open a folder in VS Code from Ubuntu, run `code .` in that folder.

## Install ROS 2 and Gazebo

Continue with [Install ROS 2 on Ubuntu](setup-ubuntu.md). Then come back here to set up Foxglove.

## Set up Foxglove on Windows

1. Download the Windows installer from [foxglove.dev/download](https://foxglove.dev/download). Run it.
2. In Ubuntu, start the bridge and the talker. Follow steps 1 and 2 in [Test the Foxglove bridge](setup-ubuntu.md#test-the-foxglove-bridge).
3. Open Foxglove. Click **Open connection**.
4. Select **Foxglove WebSocket**. Enter `ws://localhost:8765`. Click **Open**.
5. Click the **Topics** tab. The `/chatter` topic shows 1 Hz.
6. In Ubuntu, press Ctrl+C in both terminals.

## Troubleshooting

| Problem | Fix |
|---|---|
| `wsl --install` says virtualisation is not enabled | Restart into your BIOS or UEFI settings. Turn on virtualisation. It may be called Intel VT-x, AMD-V or SVM. |
| WSL says `This version of Windows does not support the packaged version` | Install all Windows updates, including optional updates. Restart. |
| Gazebo opens and closes with an `OGRE EXCEPTION` | Software rendering is off. Run `source ~/.bashrc`. Check that `~/.bashrc` contains `export LIBGL_ALWAYS_SOFTWARE=1`. |
| No window opens for Gazebo | In an admin terminal, run `wsl --update`, then `wsl --shutdown`. Open Ubuntu again. |
| Foxglove cannot connect to `localhost` | In Ubuntu, run `hostname -I`. In Foxglove, use `ws://IP_ADDRESS:8765` with the first address. |
| Windows is slow while Ubuntu runs | Limit the WSL memory, as described above. |
