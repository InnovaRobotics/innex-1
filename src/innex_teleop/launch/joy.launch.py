import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import Shutdown
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(get_package_share_directory('innex_teleop'), 'config', 'joy.yaml')
    return LaunchDescription([
        Node(
            package='joy',
            executable='game_controller_node',
            parameters=[config],
            output='screen',
            on_exit=Shutdown(),
        ),
        Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            parameters=[config],
            output='screen',
            on_exit=Shutdown(),
        ),
    ])
