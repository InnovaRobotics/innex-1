
import sys

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import String


class LadderJoy(Node):

    def __init__(self):
        super().__init__("ladder_joy")

        self.command_publisher = self.create_publisher(
            String,
            "/ladder/command",
            10
        )

        self.joy_subscription = self.create_subscription(
            Joy,
            "/joy",
            self.joy_callback,
            10
        )

        self.ladder_subscription = self.create_subscription(
            String,
            "/ladder/state",
            self.ladder_callback,
            10
        )

        self.chain_subscription = self.create_subscription(
            String,
            "/chain/state",
            self.chain_callback,
            10
        )

        self.ladder_state = "unknown"
        self.chain_state = "unknown"

    def joy_callback(self, msg):
        buttons = msg.buttons

        if len(buttons) <= 10:
            return

        lb = buttons[9]
        a = buttons[0]
        y = buttons[3]
        rb = buttons[10]

        command = None

        if lb:
            if a:
                command = "lower"
            elif y:
                command = "raise"
            elif rb:
                command = "chain"

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
            f"\rladder: {self.ladder_state:<15} "
            f"chain: {self.chain_state:<12}"
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


if __name__ == "__main__":
    main()
