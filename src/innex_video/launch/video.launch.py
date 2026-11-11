from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    camera_config = LaunchConfiguration('camera_config')

    bridge_launch = PathJoinSubstitution([
        FindPackageShare('foxglove_bridge'),
        'launch',
        'foxglove_bridge_launch.xml'])

    front_relay = Node(
        package='innex_video',
        executable='video_relay',
        name='front_video_relay',
        output='screen',
        parameters=[camera_config, {
            'output_topic': '/oak_front/video',
            'frame_id': 'oak_front_rgb_camera_optical_frame',
            'camera_role': 'front',
        }]
    )

    rear_relay = Node(
        package='innex_video',
        executable='video_relay',
        name='rear_video_relay',
        output='screen',
        parameters=[camera_config, {
            'output_topic': '/oak_rear/video',
            'frame_id': 'oak_rear_rgb_camera_optical_frame',
            'camera_role': 'rear',
        }]
    )

    foxglove_bridge = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(bridge_launch),
        launch_arguments={'port': '8765'}.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'camera_config',
            default_value=PathJoinSubstitution([
                FindPackageShare('innex_video'), 'config', 'camera_ids.yaml']),
            description='YAML file containing front and rear OAK device IDs.'),
        front_relay,
        rear_relay,
        foxglove_bridge
    ])
