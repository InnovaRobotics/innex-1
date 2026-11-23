import threading

from foxglove_msgs.msg import CompressedVideo
from innex_video.video_messages import make_compressed_video
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data


class VideoRelay(Node):
    def __init__(self):
        super().__init__('video_relay')

        self.declare_parameter('output_topic', '/camera/video')
        self.declare_parameter('frame_id', 'oak_front_rgb_optical_frame')
        self.declare_parameter('fps', 15)
        self.declare_parameter('bitrate', 1000)
        self.declare_parameter('video_size', [864, 480])
        self.declare_parameter('device_id', '')

        fps = int(self.get_parameter('fps').value)
        bitrate = int(self.get_parameter('bitrate').value)
        video_size = self.get_parameter('video_size').value

        from innex_video.oak_h264 import OakH264

        self.source = OakH264(
            device_id=self.get_parameter('device_id').value or None,
            width=int(video_size[0]),
            height=int(video_size[1]),
            fps=fps,
            bitrate_kbps=bitrate,
            keyframe_every=fps)

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

                self.publisher_.publish(make_compressed_video(
                    timestamp_ns, data, self.frame_id))

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
