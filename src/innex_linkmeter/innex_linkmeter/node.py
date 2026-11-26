"""Show, once a second, how many kbps each topic sends over the link."""

from functools import partial
import time

from innex_linkmeter.meter import format_reading, LinkMeter
import rclpy
from rclpy.exceptions import ParameterUninitializedException
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from rosidl_runtime_py.utilities import get_message
from std_msgs.msg import Float32


class LinkMeterNode(Node):

    def __init__(self):
        super().__init__('link_meter')
        self.declare_parameter('topics', Parameter.Type.STRING_ARRAY)
        limit_kbps = self.declare_parameter('limit_kbps', 3600.0).value
        try:
            topics = self.get_parameter('topics').value
        except ParameterUninitializedException:
            raise SystemExit(
                'Set the topics parameter, for example: '
                "--ros-args -p topics:='[/oak_front/rgb/image_raw]'")

        self._topics = [self.resolve_topic_name(t) for t in topics]
        self._meter = LinkMeter(self._topics, limit_kbps, time.monotonic())
        self._subscriptions_by_topic = {}
        self._kbps_pub = self.create_publisher(Float32, '/link/kbps', 10)
        self._average_pub = self.create_publisher(Float32, '/link/average_kbps', 10)
        self.create_timer(1.0, self._tick)

    def _subscribe_to_new_topics(self):
        types = dict(self.get_topic_names_and_types())
        for topic in self._topics:
            if topic in self._subscriptions_by_topic or topic not in types:
                continue
            type_names = types[topic]
            if len(type_names) > 1:
                self.get_logger().warning(
                    f'{topic} has more than one type, {type_names}. Using {type_names[0]}.')
            # raw=True hands the callback the serialised bytes, so no message is deserialised.
            self._subscriptions_by_topic[topic] = self.create_subscription(
                get_message(type_names[0]), topic,
                partial(self._on_message, topic), qos_profile_sensor_data, raw=True)

    def _on_message(self, topic, data):
        self._meter.add(topic, len(data))

    def _tick(self):
        self._subscribe_to_new_topics()
        reading = self._meter.read(time.monotonic())
        waiting = [t for t in self._topics if t not in self._subscriptions_by_topic]
        print('\n'.join(format_reading(reading, waiting)) + '\n', flush=True)
        self._kbps_pub.publish(Float32(data=reading.total_kbps))
        self._average_pub.publish(Float32(data=reading.average_kbps))


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = LinkMeterNode()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()
