# Launch the simulation and keyboard teleop on Windows

Use [launch_sim_teleop.bat](../launch_sim_teleop.bat) to start both the Gazebo Harmonic simulation and keyboard teleop in one step from Windows.

## Why a `.bat` launcher is needed

On Windows, ROS 2 Jazzy and Gazebo Harmonic run inside the `Ubuntu-24.04` WSL 2 distribution, while the Gazebo window is displayed on Windows through WSLg (`DISPLAY=:0`).

`teleop_twist_keyboard` reads raw keystrokes from standard input, so it requires an interactive terminal window attached to your desktop session. Background or non-interactive shells (such as an IDE agent task runner) cannot attach a live keyboard-input console to the desktop. Running `launch_sim_teleop.bat` from Windows Explorer, PowerShell, or Command Prompt spawns two separate interactive console windows—one for the simulation and one for keyboard control.

## What the launch sequence does

1. **Resolves the workspace path:** Converts the Windows folder containing `launch_sim_teleop.bat` (`%~dp0`) into its WSL mount path using `wslpath -u`, so the script works regardless of where the repository is cloned.
2. **Starts the simulation (`INNEX-1 Gazebo Sim` window):**
   - Sources `/opt/ros/jazzy/setup.bash`.
   - Runs `colcon build --symlink-install` if `install/setup.bash` does not exist yet.
   - Sources `install/setup.bash` and runs `ros2 launch innex_sim moon_yard.launch.py`.
3. **Waits 4 seconds**, then **starts keyboard teleop (`INNEX-1 Keyboard Teleop` window):**
   - Sources `/opt/ros/jazzy/setup.bash`.
   - Runs `ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true`.

Both windows end with `exec bash` so that if a process exits or reports an error, the window stays open for inspection instead of closing immediately.

## Why `stamped:=true` is required

`innex_sim` bridges `/cmd_vel` to Gazebo as `geometry_msgs/msg/TwistStamped` (see [src/innex_sim/README.md](../src/innex_sim/README.md)). In ROS 2 Jazzy, `teleop_twist_keyboard` publishes unstamped `geometry_msgs/msg/Twist` by default, which the bridge ignores. Passing `-p stamped:=true` switches it to `TwistStamped`.

## Controls

Focus the **INNEX-1 Keyboard Teleop** window and use:

| Key | Action |
|---|---|
| `i` / `,` | Drive forward / backward |
| `j` / `l` | Turn left / right |
| `k` | Stop (send zero velocity) |
| `q` / `z` | Increase / decrease max speeds |

Gazebo's `DiffDrive` plugin has no command timeout, so the rover keeps its last velocity until you press `k` to send a zero command.
