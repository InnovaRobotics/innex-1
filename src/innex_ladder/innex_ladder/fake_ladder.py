"""A pretend motor that stands in for the real ladder motors."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

DRIVE_TIMEOUT_S = 0.25
UPDATE_PERIOD_S = 0.1


class FakeLadder(Node):
    """Moves a pretend position when told to. It has no rules."""

    def __init__(self):
        """Set up the parameter, topics and timer."""
        super().__init__('fake_ladder')

        self.declare_parameter('ladder_travel_time_s', 10.0)
        travel_time = self.get_parameter('ladder_travel_time_s').value
        self.travel_time = max(travel_time, 0.1)

        now = self.get_clock().now()
        self.position = 0.0
        self.ladder_drive = 'stop'
        self.ladder_drive_time = now
        self.chain_drive = 'stop'
        self.chain_drive_time = now
        self.last_update = now
        self.last_chain_running = False

        self.ladder_drive_subscription = self.create_subscription(
            String, '/ladder/drive', self.ladder_drive_callback, 10)
        self.chain_drive_subscription = self.create_subscription(
            String, '/chain/drive', self.chain_drive_callback, 10)
        self.position_publisher = self.create_publisher(
            Float32, '/ladder/position', 10)

        self.timer = self.create_timer(UPDATE_PERIOD_S, self.update)
        self.get_logger().info('Fake Ladder has started')

    def ladder_drive_callback(self, msg):
        """Remember the latest ladder drive word and when it arrived."""
        self.ladder_drive = msg.data
        self.ladder_drive_time = self.get_clock().now()

    def chain_drive_callback(self, msg):
        """Remember the latest chain drive word and when it arrived."""
        self.chain_drive = msg.data
        self.chain_drive_time = self.get_clock().now()

    def fresh(self, then, now):
        """Return True if a message from time 'then' is still recent."""
        return (now - then).nanoseconds / 1e9 <= DRIVE_TIMEOUT_S

    def update(self):
        """Move the pretend ladder and report its position."""
        now = self.get_clock().now()
        dt = (now - self.last_update).nanoseconds / 1e9
        self.last_update = now

        ladder_drive = 'stop'
        if self.fresh(self.ladder_drive_time, now):
            ladder_drive = self.ladder_drive

        direction = 0
        if ladder_drive == 'lower':
            direction = 1
        elif ladder_drive == 'raise':
            direction = -1

        self.position += direction * dt / self.travel_time
        self.position = max(0.0, min(1.0, self.position))
        self.position_publisher.publish(Float32(data=self.position))

        chain_running = (self.chain_drive == 'run'
                         and self.fresh(self.chain_drive_time, now))
        if chain_running != self.last_chain_running:
            self.get_logger().info(
                f'pretend chain: {"running" if chain_running else "stopped"}')
            self.last_chain_running = chain_running


def main(args=None):
    """Start the node and keep it running."""
    rclpy.init(args=args)
    node = FakeLadder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
