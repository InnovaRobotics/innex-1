"""A pretend bucket ladder that stands in for the real motors."""

from innex_ladder.ladder_rules import can_run_chain, ChainState, LadderState
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

COMMAND_TIMEOUT_S = 0.25
UPDATE_PERIOD_S = 0.1
VALID_COMMANDS = ('lower', 'raise', 'chain')


class FakeLadder(Node):
    """A fake ladder node for testing without hardware."""

    def __init__(self):
        """Set up the parameter, publishers, subscriber and timer."""
        super().__init__('fake_ladder')

        self.declare_parameter('ladder_travel_time_s', 10.0)
        travel_time = self.get_parameter('ladder_travel_time_s').value
        self.travel_time = max(travel_time, 0.1)

        self.position = 0.0
        self.command = None
        self.command_time = self.get_clock().now()
        self.last_update = self.get_clock().now()
        self.last_ladder = None
        self.last_chain = None

        self.command_subscription = self.create_subscription(
            String,
            '/ladder/command',
            self.command_callback,
            10)
        self.ladder_publisher = self.create_publisher(
            String, '/ladder/state', 10)
        self.chain_publisher = self.create_publisher(
            String, '/chain/state', 10)
        self.timer = self.create_timer(UPDATE_PERIOD_S, self.update)

        self.get_logger().info('Fake Ladder has started')

    def command_callback(self, msg):
        """Remember the latest command and when it arrived."""
        if msg.data not in VALID_COMMANDS:
            self.get_logger().warn(f'Unknown command ignored: {msg.data}')
            return
        self.command = msg.data
        self.command_time = self.get_clock().now()

    def active_command(self, now):
        """Return the current command, or None if it has timed out."""
        if self.command is None:
            return None
        age = (now - self.command_time).nanoseconds / 1e9
        if age > COMMAND_TIMEOUT_S:
            return None
        return self.command

    def update(self):
        """Move the ladder, apply the chain rule and publish both states."""
        now = self.get_clock().now()
        dt = (now - self.last_update).nanoseconds / 1e9
        self.last_update = now

        command = self.active_command(now)

        direction = 0
        if command == 'lower' and self.position < 1.0:
            direction = 1
        elif command == 'raise' and self.position > 0.0:
            direction = -1

        self.position += direction * dt / self.travel_time
        self.position = max(0.0, min(1.0, self.position))

        if direction == 1:
            ladder = LadderState.LOWERING
        elif direction == -1:
            ladder = LadderState.RAISING
        elif self.position >= 1.0:
            ladder = LadderState.IN_POSITION
        elif self.position <= 0.0:
            ladder = LadderState.UP
        else:
            ladder = LadderState.STOPPED

        chain = ChainState.STOPPED
        if command == 'chain':
            if can_run_chain(ladder):
                chain = ChainState.TURNING
            else:
                self.get_logger().warn(
                    'Chain command ignored: ladder is not in position.',
                    throttle_duration_sec=1.0)

        self.ladder_publisher.publish(String(data=ladder.value))
        self.chain_publisher.publish(String(data=chain.value))

        if ladder != self.last_ladder or chain != self.last_chain:
            self.get_logger().info(
                f'ladder: {ladder.value}, chain: {chain.value}')
            self.last_ladder = ladder
            self.last_chain = chain


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
