"""Launch video relays only for configured OAK cameras that are connected."""

from pathlib import Path

from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            LogInfo, OpaqueFunction)
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import yaml


def _camera_relays(context):
    """Discover cameras once and start only their assigned relay nodes."""
    import depthai as dai

    config_path = Path(LaunchConfiguration('camera_config').perform(context))
    with config_path.open(encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file) or {}

    roles = ('front', 'rear')
    configured_ids = {
        role: str(config.get(f'{role}_video_relay', {})
                  .get('ros__parameters', {}).get('device_id', '') or '')
        for role in roles
    }
    explicit_ids = [device_id for device_id in configured_ids.values()
                    if device_id]
    if len(explicit_ids) != len(set(explicit_ids)):
        raise RuntimeError(
            'Front and rear camera IDs must be different; refusing to start '
            'two relays on the same OAK camera.')

    devices = sorted(
        (str(device.deviceId) for device in dai.Device.getAllAvailableDevices()))

    assigned = {role: None for role in roles}
    connected = set(devices)
    claimed = set()
    messages = []

    for role in roles:
        device_id = configured_ids[role]
        if not device_id:
            continue
        if device_id in connected:
            assigned[role] = device_id
            claimed.add(device_id)
        else:
            messages.append(
                f'Configured {role} OAK ID {device_id} is not connected.')

    unconfigured_roles = [
        role for role in roles if not configured_ids[role]]
    unclaimed_devices = [device_id for device_id in devices
                         if device_id not in claimed]

    if len(unclaimed_devices) == 1 and unconfigured_roles:
        # With one bench camera, use front unless front has an explicit ID.
        role = 'front' if 'front' in unconfigured_roles else unconfigured_roles[0]
        assigned[role] = unclaimed_devices[0]
    else:
        for role, device_id in zip(unconfigured_roles, unclaimed_devices):
            assigned[role] = device_id

    nodes = []
    for role in roles:
        device_id = assigned[role]
        if not device_id:
            continue
        nodes.append(Node(
            package='innex_video',
            executable='video_relay',
            name=f'{role}_video_relay',
            output='screen',
            parameters=[{
                'output_topic': f'/oak_{role}/video',
                'frame_id': f'oak_{role}_rgb_camera_optical_frame',
                'device_id': device_id,
                'fps': 15,
                'bitrate': 1000,
            }]))
        messages.append(f'Starting {role} video relay for OAK {device_id}.')

    if not nodes:
        messages.append(
            'No assigned OAK cameras are connected; no video relays started.')

    return [LogInfo(msg=message) for message in messages] + nodes


def generate_launch_description():
    bridge_launch = PathJoinSubstitution([
        FindPackageShare('foxglove_bridge'),
        'launch',
        'foxglove_bridge_launch.xml'])

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
        OpaqueFunction(function=_camera_relays),
        foxglove_bridge,
    ])
