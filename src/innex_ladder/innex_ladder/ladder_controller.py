"""The brain: decides what the ladder and chain should do."""

from innex_ladder.ladder_logic import COMMAND_TIMEOUT_S, decide_drive
from innex_ladder.ladder_rules import ChainState, LadderState
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

UPDATE_PERIOD_S = 0.1
VALID_COMMANDS = ('lower', 'raise', 'chain')


class LadderController(Node):
    """Decides what to tell the motors, and reports the state."""

    def __init__(self):
        """Set up the memory, the four topics and the timer."""
        super().__init__('ladder_controller')

        self.command = None
        self.command_time = self.get_clock().now()
        self.position = 0.0
        self.ladder = LadderState.UP
        self.last_ladder = None
        self.last_chain = None

        self.command_subscription = self.create_subscription(
            String, '/ladder/command', self.command_callback, 10)
        self.position_subscription = self.create_subscription(
            Float32, '/ladder/position', self.position_callback, 10)

        self.ladder_drive_publisher = self.create_publisher(
            String, '/ladder/drive', 10)
        self.chain_drive_publisher = self.create_publisher(
            String, '/chain/drive', 10)
        self.ladder_state_publisher = self.create_publisher(
            String, '/ladder/state', 10)
        self.chain_state_publisher = self.create_publisher(
            String, '/chain/state', 10)

        self.timer = self.create_timer(UPDATE_PERIOD_S, self.update)
        self.get_logger().info('Ladder controller has started')

    def command_callback(self, msg):
        """Remember the latest command and when it arrived."""
        if msg.data not in VALID_COMMANDS:
            self.get_logger().warning(f'Unknown command ignored: {msg.data}')
            return
        self.command = msg.data
        self.command_time = self.get_clock().now()

    def position_callback(self, msg):
        """Remember the latest position reported by the motor."""
        self.position = msg.data

    def update(self):
        """Decide, publish the drive words, then work out and publish state."""
        now = self.get_clock().now()
        age = (now - self.command_time).nanoseconds / 1e9

        ladder_drive, chain_drive = decide_drive(
            self.command, age, self.ladder)

        if (self.command == 'chain' and age <= COMMAND_TIMEOUT_S
                and chain_drive == 'stop'):
            self.get_logger().warning(
                'Chain command ignored: ladder is not in position.',
                throttle_duration_sec=1.0)

        if ladder_drive == 'lower' and self.position < 1.0:
            self.ladder = LadderState.LOWERING
        elif ladder_drive == 'raise' and self.position > 0.0:
            self.ladder = LadderState.RAISING
        elif self.position >= 1.0:
            self.ladder = LadderState.IN_POSITION
        elif self.position <= 0.0:
            self.ladder = LadderState.UP
        else:
            self.ladder = LadderState.STOPPED

        if chain_drive == 'run':
            chain = ChainState.TURNING
        else:
            chain = ChainState.STOPPED

        self.ladder_drive_publisher.publish(String(data=ladder_drive))
        self.chain_drive_publisher.publish(String(data=chain_drive))
        self.ladder_state_publisher.publish(String(data=self.ladder.value))
        self.chain_state_publisher.publish(String(data=chain.value))

        if self.ladder != self.last_ladder or chain != self.last_chain:
            self.get_logger().info(
                f'ladder: {self.ladder.value}, chain: {chain.value}')
            self.last_ladder = self.ladder
            self.last_chain = chain


def main(args=None):
    """Start the node and keep it running."""
    rclpy.init(args=args)
    node = LadderController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
