
import sys

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import String


class LadderJoy(Node):

    def __init__(self):
        super().__init__('ladder_joy')

        self.declare_parameter('rb_button', 10)
        self.declare_parameter('a_button', 0)
        self.declare_parameter('y_button', 3)
        self.declare_parameter('chain_button', 14)

        self.command_publisher = self.create_publisher(
            String,
            '/ladder/command',
            10
        )

        self.joy_subscription = self.create_subscription(
            Joy,
            '/joy',
            self.joy_callback,
            10
        )

        self.ladder_subscription = self.create_subscription(
            String,
            '/ladder/state',
            self.ladder_callback,
            10
        )

        self.chain_subscription = self.create_subscription(
            String,
            '/chain/state',
            self.chain_callback,
            10
        )

        self.ladder_state = 'unknown'
        self.chain_state = 'unknown'

    def joy_callback(self, msg):
        buttons = msg.buttons
        rb_index = self.get_parameter('rb_button').value
        a_index = self.get_parameter('a_button').value
        y_index = self.get_parameter('y_button').value
        chain_index = self.get_parameter('chain_button').value

        if len(buttons) <= max(rb_index, a_index, y_index, chain_index):
            return

        rb = buttons[rb_index]
        a = buttons[a_index]
        y = buttons[y_index]
        chain = buttons[chain_index]

        command = None

        if rb:
            if a:
                command = 'lower'
            elif y:
                command = 'raise'
            elif chain:
                command = 'chain'

        if command is not None:
            command_msg = String()
            command_msg.data = command
            self.command_publisher.publish(command_msg)

    def ladder_callback(self, msg):
        self.ladder_state = msg.data
        self.display_state()

    def chain_callback(self, msg):
        self.chain_state = msg.data
        self.display_state()

    def display_state(self):
        sys.stdout.write(
            f'\rladder: {self.ladder_state:<15} '
            f'chain: {self.chain_state:<12}'
        )
        sys.stdout.flush()


def main(args=None):
    rclpy.init(args=args)

    node = LadderJoy()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        print()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
