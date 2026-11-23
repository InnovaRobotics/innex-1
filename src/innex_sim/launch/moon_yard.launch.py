import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            OpaqueFunction, Shutdown)
from launch.conditions import IfCondition
from launch.launch_description_sources import (AnyLaunchDescriptionSource,
                                               PythonLaunchDescriptionSource)
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
    video_enabled = IfCondition(LaunchConfiguration('video'))
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
            'video', default_value='false',
            description='Start simulated camera encoders and Foxglove bridge.'),
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
        # Gazebo keeps the last command it received. If the watchdog or ros_gz_bridge exits, stop
        # the whole simulation, so the rover cannot keep driving on that command.
        Node(
            package='innex_sim',
            executable='cmd_vel_watchdog',
            output='screen',
            on_exit=Shutdown(),
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            parameters=[{'config_file': os.path.join(
                get_package_share_directory('innex_sim'), 'config', 'bridge.yaml')}],
            output='screen',
            on_exit=Shutdown(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('innex_description'),
                             'launch', 'description.launch.py')),
            launch_arguments={
                'use_sim_time': 'true',
                'sim_cameras': LaunchConfiguration('video'),
            }.items(),
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
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='camera_image_bridge',
            condition=video_enabled,
            parameters=[{'config_file': os.path.join(
                get_package_share_directory('innex_sim'), 'config',
                'bridge_cameras.yaml')}],
            output='screen',
        ),
        Node(
            package='innex_sim',
            executable='sim_video_relay',
            name='front_sim_video_relay',
            condition=video_enabled,
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
            condition=video_enabled,
            output='screen',
            parameters=[{
                'input_topic': '/oak_rear/rgb/image_raw',
                'output_topic': '/oak_rear/video',
                'frame_id': 'oak_rear_rgb_camera_optical_frame',
            }],
        ),
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(bridge_launch),
            condition=video_enabled,
            launch_arguments={
                'port': '8765',
                'topic_whitelist': "['^/oak_(front|rear)/video$']",
            }.items(),
        ),
    ])
