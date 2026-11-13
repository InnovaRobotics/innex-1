"""A pretend bucket ladder that stands in for the real motors."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class FakeLadder(Node):
    """A fake ladder node for testing without hardware."""

    def __init__(self):
        """Set up the node and its command subscriber."""
        super().__init__('fake_ladder')
        self.get_logger().info('Fake Ladder has started')

        self.command_subscription = self.create_subscription(
            String,
            '/ladder/command',
            self.command_callback,
            10)

    def command_callback(self, msg):
        """Handle one incoming command."""
        self.get_logger().info('Heard: ' + msg.data)


def main(args=None):
    """Start the node and keep it running."""
    rclpy.init(args=args)
    node = FakeLadder()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
