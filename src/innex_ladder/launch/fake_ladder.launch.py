
import os

from ament_index_python.packages import (
    get_package_share_directory
)
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    package_dir = get_package_share_directory(
        'innex_ladder'
    )

    config_file = os.path.join(
        package_dir,
        'config',
        'fake_ladder.yaml'
    )
    joy_config = os.path.join(
        package_dir,
        'config',
        'ladder_joy.yaml'
    )
    joy_argument = DeclareLaunchArgument(
        'joy',
        default_value='true',
        description='Start game_controller_node'
    )

    return LaunchDescription([
        joy_argument,
        Node(
            package='joy',
            executable='game_controller_node',
            name='game_controller_node',
            parameters=[
                {'autorepeat_rate': 20.0}
            ],
            condition=IfCondition(LaunchConfiguration('joy')),
        ),

        Node(
            package='innex_ladder',
            executable='fake_ladder',
            name='fake_ladder',
            parameters=[config_file],
            output='screen'
        ),

        Node(
            package='innex_ladder',
            executable='ladder_joy',
            name='ladder_joy',
            parameters=[joy_config],
            output='screen',
        )

    ])
