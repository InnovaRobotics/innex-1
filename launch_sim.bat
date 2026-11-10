@echo off
echo ========================================================
echo   Launching INNEX-1 Rover Simulation and Teleop
echo ========================================================
echo.

echo Cleaning up any previous instances...
wsl.exe -d Ubuntu-24.04 bash -c "killall -9 gz-sim gz sim parameter_bridge robot_state_publisher teleop_twist_keyboard 2>/dev/null; ros2 daemon stop 2>/dev/null"

echo Starting Gazebo Simulation with GUI...
start "INNEX-1 Gazebo Simulation" wsl.exe -d Ubuntu-24.04 bash /mnt/c/Users/chandra/Downloads/innex1/scripts/run_sim.sh

echo Waiting for Gazebo to initialize (approx 8 seconds)...
ping 127.0.0.1 -n 9 >nul

echo Starting Teleop Keyboard Controller...
start "INNEX-1 Teleop Controller" drive.bat

echo.
echo Gazebo GUI and Teleop windows launched!
echo Look for the Gazebo 3D simulation window on your desktop or taskbar.
