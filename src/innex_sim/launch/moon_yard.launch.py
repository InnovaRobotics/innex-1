import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def launch_gazebo(context):
    gui = LaunchConfiguration('gui').perform(context).lower() in ('true', '1')
    world = os.path.join(get_package_share_directory('innex_sim'), 'worlds', 'moon_yard.sdf')
    gz_args = f'-r {"" if gui else "-s "}{world}'
    return [IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': gz_args, 'on_exit_shutdown': 'true'}.items(),
    )]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'gui', default_value='true',
            description='Start the Gazebo GUI. Use false for server only.'),
        DeclareLaunchArgument(
            'x', default_value='1.0',
            description='Rover spawn x in the arena frame, in metres.'),
        DeclareLaunchArgument(
            'y', default_value='3.4',
            description='Rover spawn y in the arena frame, in metres.'),
        DeclareLaunchArgument(
            'yaw', default_value='0.0',
            description='Rover heading in radians. 0 faces east, towards the excavation zone.'),
        OpaqueFunction(function=launch_gazebo),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
            output='screen',
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('innex_description'),
                             'launch', 'description.launch.py')),
            launch_arguments={'use_sim_time': 'true'}.items(),
        ),
        Node(
            package='ros_gz_sim',
            executable='create',
            parameters=[{
                'world': 'moon_yard',
                'topic': 'robot_description',
                'name': 'innex_1',
                'x': ParameterValue(LaunchConfiguration('x'), value_type=float),
                'y': ParameterValue(LaunchConfiguration('y'), value_type=float),
                'z': 0.05,
                'Y': ParameterValue(LaunchConfiguration('yaw'), value_type=float),
            }],
            output='screen',
        ),
    ])
