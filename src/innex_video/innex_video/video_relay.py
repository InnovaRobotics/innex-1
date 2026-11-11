import threading

from foxglove_msgs.msg import CompressedVideo
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data


class VideoRelay(Node):
    def __init__(self):
        super().__init__('video_relay')

        self.declare_parameter('output_topic', '/camera/video')
        self.declare_parameter('frame_id', 'oak_front_rgb_optical_frame')
        self.declare_parameter('fps', 20)
        self.declare_parameter('bitrate', 1000)
        self.declare_parameter('video_size', [864, 480])
        self.declare_parameter('device_id', '')
        self.declare_parameter('camera_role', 'front')

        fps = int(self.get_parameter('fps').value)
        bitrate = int(self.get_parameter('bitrate').value)
        video_size = self.get_parameter('video_size').value

        from innex_video.oakH264 import OakH264Recorder

        self.source = OakH264Recorder(
            fps=fps,
            bitrate_Kbps=bitrate,
            video_size=tuple(video_size),
            device_id=self.get_parameter('device_id').value,
            camera_role=self.get_parameter('camera_role').value)

        self.frame_id = self.get_parameter('frame_id').value
        output_topic = self.get_parameter('output_topic').value
        self.publisher_ = self.create_publisher(
            CompressedVideo, output_topic, qos_profile_sensor_data)

        self.frame_thread = threading.Thread(target=self._publish_frames, daemon=True)
        self.frame_thread.start()
        self.get_logger().info(
            'Using OAK source, publishing Foxglove video on '
            f'{output_topic}')

    def _publish_frames(self):
        try:
            for timestamp_ns, data in self.source.frames():
                if not rclpy.ok():
                    break

                msg = CompressedVideo()
                msg.timestamp.sec = timestamp_ns // 1_000_000_000
                msg.timestamp.nanosec = timestamp_ns % 1_000_000_000
                msg.frame_id = self.frame_id
                msg.format = 'h264'
                msg.data = data

                self.publisher_.publish(msg)

        except Exception as exc:
            self.get_logger().error(f'Video source stopped: {exc}')

    def destroy_node(self):
        if hasattr(self, 'source') and hasattr(self.source, 'close'):
            self.source.close()

        if hasattr(self, 'frame_thread'):
            self.frame_thread.join(timeout=2.0)

        super().destroy_node()


def main():
    rclpy.init()
    node = VideoRelay()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
