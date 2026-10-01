import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('innex_sim')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    world = LaunchConfiguration('world')
    gui = LaunchConfiguration('gui')

    world_path = PathJoinSubstitution([
        TextSubstitution(text=os.path.join(share, 'worlds') + os.sep),
        [world, TextSubstitution(text='.sdf')],
    ])

    def gazebo(server_only):
        flags = '-r -s ' if server_only else '-r '
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')),
            launch_arguments={
                'gz_args': [TextSubstitution(text=flags), world_path],
                'on_exit_shutdown': 'true',
            }.items(),
            condition=UnlessCondition(gui) if server_only else IfCondition(gui),
        )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world', default_value='moon_yard',
            description='World name: moon_yard or moon_yard_flat'),
        DeclareLaunchArgument(
            'gui', default_value='true',
            description='Start the Gazebo GUI. Use false for server only.'),
        AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH', os.path.join(share, 'models')),
        gazebo(server_only=False),
        gazebo(server_only=True),
        bridge,
    ])
