"""Relay Gazebo camera images as Foxglove-compatible H.264 video."""

import threading

from foxglove_msgs.msg import CompressedVideo
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from innex_sim.sim_source import SimSource


class SimVideoRelay(Node):
    """Subscribe to one simulated image topic and publish encoded video."""

    def __init__(self):
        super().__init__('sim_video_relay')

        self.declare_parameter('input_topic', '/oak_front/rgb/image_raw')
        self.declare_parameter('output_topic', '/oak_front/video')
        self.declare_parameter('frame_id', 'oak_front_rgb_camera_optical_frame')
        self.declare_parameter('fps', 20)
        self.declare_parameter('bitrate', 1000)
        self.declare_parameter('video_size', [864, 480])

        self.frame_id = self.get_parameter('frame_id').value
        output_topic = self.get_parameter('output_topic').value
        self.publisher_ = self.create_publisher(
            CompressedVideo, output_topic, qos_profile_sensor_data)

        self.source = SimSource(
            node=self,
            input_topic=self.get_parameter('input_topic').value,
            fps=int(self.get_parameter('fps').value),
            bitrate=int(self.get_parameter('bitrate').value),
            video_size=self.get_parameter('video_size').value,
        )

        self.frame_thread = threading.Thread(
            target=self._publish_frames, daemon=True)
        self.frame_thread.start()
        self.get_logger().info(
            f'Publishing simulated Foxglove video on {output_topic}')

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
            self.get_logger().error(f'Simulated video source stopped: {exc}')

    def destroy_node(self):
        if hasattr(self, 'source'):
            self.source.close()
        if hasattr(self, 'frame_thread'):
            self.frame_thread.join(timeout=2.0)
        super().destroy_node()


def main():
    rclpy.init()
    node = SimVideoRelay()
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
