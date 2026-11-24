"""Stream H.264 video from an OAK camera as Foxglove CompressedVideo."""

import time

from foxglove_msgs.msg import CompressedVideo
from innex_video.video_messages import make_compressed_video
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data


def select_device_id(available_ids, configured_id='', allow_auto_device=False):
    """Return (device_id, None) to open, or (None, reason) to skip."""
    available = [str(device_id) for device_id in available_ids]
    configured = str(configured_id).strip()

    if configured:
        if configured in available:
            return configured, None
        found = ', '.join(available) or 'none'
        return None, (
            f'Configured OAK {configured} is not connected '
            f'(found: {found}).')

    if not allow_auto_device:
        return None, 'No device_id configured; skipping this camera relay.'

    if len(available) == 1:
        return available[0], None
    if not available:
        return None, 'No OAK cameras are connected.'

    found = ', '.join(sorted(available))
    return None, (
        f'Multiple OAK cameras connected ({found}); '
        'set front and rear device_id in camera_ids.yaml.')


class VideoRelay(Node):
    """Open one OAK camera H.264 encoder and publish CompressedVideo."""

    def __init__(self):
        super().__init__('video_relay')

        self.declare_parameter('output_topic', '/oak_front/video')
        self.declare_parameter(
            'frame_id', 'oak_front_rgb_camera_optical_frame')
        self.declare_parameter('fps', 15)
        self.declare_parameter('bitrate', 1000)
        self.declare_parameter('video_size', [864, 480])
        self.declare_parameter('device_id', '')
        self.declare_parameter('allow_auto_device', True)

        self.device = None
        self.pipeline = None
        self.active = False

        self._open_camera()

    def _open_camera(self):
        import depthai as dai

        available_ids = [
            str(device.deviceId)
            for device in dai.Device.getAllAvailableDevices()
        ]
        selected_id, reason = select_device_id(
            available_ids,
            configured_id=self.get_parameter('device_id').value,
            allow_auto_device=bool(
                self.get_parameter('allow_auto_device').value),
        )
        if selected_id is None:
            self.get_logger().info(reason)
            return

        fps = int(self.get_parameter('fps').value)
        bitrate = int(self.get_parameter('bitrate').value)
        width, height = (
            int(value) for value in self.get_parameter('video_size').value)
        self.frame_id = self.get_parameter('frame_id').value
        output_topic = self.get_parameter('output_topic').value

        self.device = dai.Device(dai.DeviceInfo(selected_id))
        self.pipeline = dai.Pipeline(self.device)

        camera = self.pipeline.create(dai.node.Camera).build(
            dai.CameraBoardSocket.CAM_A)
        video = camera.requestOutput(
            size=(width, height),
            type=dai.ImgFrame.Type.NV12,
            fps=fps)
        encoder = self.pipeline.create(dai.node.VideoEncoder).build(
            video,
            frameRate=fps,
            profile=dai.VideoEncoderProperties.Profile.H264_BASELINE,
            keyframeFrequency=fps)
        encoder.setBitrateKbps(bitrate)
        self.output_queue = encoder.out.createOutputQueue(
            maxSize=15, blocking=False)

        self.publisher_ = self.create_publisher(
            CompressedVideo, output_topic, qos_profile_sensor_data)
        self.pipeline.start()
        self.timer = self.create_timer(0.01, self._poll_frames)
        self.active = True
        self.get_logger().info(
            f'Streaming OAK {selected_id} on {output_topic} '
            f'({width}x{height} at {fps} fps, {bitrate} kbps).')

    def _poll_frames(self):
        while (packet := self.output_queue.tryGet()) is not None:
            self.publisher_.publish(make_compressed_video(
                time.time_ns(), bytes(packet.getData()), self.frame_id))

    def destroy_node(self):
        """Stop the DepthAI pipeline and release the OAK camera."""
        if self.pipeline is not None:
            self.pipeline.stop()
            self.pipeline.wait()
            self.pipeline = None
        if self.device is not None:
            self.device.close()
            self.device = None
        super().destroy_node()


def main():
    """Run the OAK H.264 video relay node."""
    rclpy.init()
    node = None
    try:
        node = VideoRelay()
        if node.active:
            rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
