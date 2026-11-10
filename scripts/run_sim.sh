#!/usr/bin/env bash
source /opt/ros/jazzy/setup.bash
source /mnt/c/Users/chandra/Downloads/innex1/install/setup.bash

ros2 launch innex_sim moon_yard.launch.py gui:=true
