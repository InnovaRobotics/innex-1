"""Launch the bridge with an installed configuration file; dry-run by default."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Allow an explicitly selected parameter file without embedding device paths."""
    default = os.path.join(
        get_package_share_directory('innex_drive_bridge'), 'config', 'drive_bridge.yaml')
    return LaunchDescription([
        DeclareLaunchArgument('params_file', default_value=default),
        Node(package='innex_drive_bridge', executable='bridge_node',
             name='drive_bridge', parameters=[LaunchConfiguration('params_file')],
             output='screen'),
    ])
