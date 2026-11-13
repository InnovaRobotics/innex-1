
import os

from ament_index_python.packages import (
    get_package_share_directory
)
from launch import LaunchDescription
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

    return LaunchDescription([

        Node(
            package='joy',
            executable='game_controller_node',
            name='game_controller_node',
            parameters=[
                {'autorepeat_rate': 20.0}
            ]
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
            output='screen'
        )

    ])
