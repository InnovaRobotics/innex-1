import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.launch_description_sources import (
    AnyLaunchDescriptionSource,
    PythonLaunchDescriptionSource,
)
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


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
    bridge_launch = PathJoinSubstitution([
        FindPackageShare('foxglove_bridge'),
        'launch',
        'foxglove_bridge_launch.xml',
    ])

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
            parameters=[{'config_file': os.path.join(
                get_package_share_directory('innex_sim'), 'config', 'bridge.yaml')}],
            output='screen',
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='keyboard_cmd_vel_bridge',
            parameters=[{'config_file': os.path.join(
                get_package_share_directory('innex_sim'), 'config', 'bridge_twist.yaml')}],
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
        Node(
            package='innex_sim',
            executable='sim_video_relay',
            name='front_sim_video_relay',
            output='screen',
            parameters=[{
                'input_topic': '/oak_front/rgb/image_raw',
                'output_topic': '/oak_front/video',
                'frame_id': 'oak_front_rgb_camera_optical_frame',
            }],
        ),
        Node(
            package='innex_sim',
            executable='sim_video_relay',
            name='rear_sim_video_relay',
            output='screen',
            parameters=[{
                'input_topic': '/oak_rear/rgb/image_raw',
                'output_topic': '/oak_rear/video',
                'frame_id': 'oak_rear_rgb_camera_optical_frame',
            }],
        ),
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(bridge_launch),
            launch_arguments={'port': '8765'}.items(),
        ),
    ])
