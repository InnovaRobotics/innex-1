@echo off
setlocal

set "REPO_WIN=%~dp0"
if "%REPO_WIN:~-1%"=="\" set "REPO_WIN=%REPO_WIN:~0,-1%"

for /f "usebackq delims=" %%I in (`wsl -d Ubuntu-24.04 -- wslpath -u "%REPO_WIN%"`) do set "REPO_WSL=%%I"
if "%REPO_WSL%"=="" (
    echo Failed to resolve WSL path for "%REPO_WIN%". Make sure Ubuntu-24.04 is installed.
    pause
    exit /b 1
)

echo Starting INNEX-1 Gazebo simulation from %REPO_WSL%...
start "INNEX-1 Gazebo Sim" wsl -d Ubuntu-24.04 -- bash -lc "cd '%REPO_WSL%' && source /opt/ros/jazzy/setup.bash && ([ -f install/setup.bash ] || colcon build --symlink-install) && source install/setup.bash && ros2 launch innex_sim moon_yard.launch.py; exec bash"

timeout /t 4 /nobreak >nul

echo Starting keyboard teleop (TwistStamped on /cmd_vel)...
start "INNEX-1 Keyboard Teleop" wsl -d Ubuntu-24.04 -- bash -lc "source /opt/ros/jazzy/setup.bash && ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true; exec bash"
