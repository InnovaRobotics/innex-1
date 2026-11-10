#!/usr/bin/env python3
"""Interactive keyboard teleop node for the INNEX-1 rover.

Requires continuous key holding (deadman behavior): velocity returns to zero
when keys are released. Features progressive acceleration and smooth stopping.
"""

import os
import select
import sys
import termios
import time
import tty

import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.node import Node

# Speed limits
SPEED_LIMIT_MAX = 0.6  # m/s absolute ceiling
DEFAULT_MAX_SPEED = 0.4  # m/s
DEFAULT_TURN_RATE = 0.5  # rad/s

# Acceleration rates (m/s^2 and rad/s^2)
ACCEL_LINEAR = 0.35  # Progressive ramp-up (~1.1s to full speed)
DECEL_LINEAR = 0.70  # Progressive, confident stop
ACCEL_ANGULAR = 0.60
DECEL_ANGULAR = 1.20

KEY_TIMEOUT = 0.35  # seconds: if no key repeat within this time, consider released
LOOP_RATE = 20.0  # Hz


class ProgressiveKeyboardTeleop(Node):
    def __init__(self):
        super().__init__('keyboard_teleop')
        self.publisher_ = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        
        self.max_speed = DEFAULT_MAX_SPEED
        self.max_turn = DEFAULT_TURN_RATE
        
        self.target_linear = 0.0
        self.target_angular = 0.0
        self.current_linear = 0.0
        self.current_angular = 0.0
        
        self.last_key_time = 0.0
        self.is_active = False

    def ramp(self, current, target, accel, decel, dt):
        if target > current:
            rate = accel if current >= 0 else decel
            return min(target, current + rate * dt)
        elif target < current:
            rate = accel if current <= 0 else decel
            return max(target, current - rate * dt)
        return current

    def update_velocity(self, dt):
        # Deadman check: if no key pressed within KEY_TIMEOUT, target is 0
        now = time.monotonic()
        if now - self.last_key_time > KEY_TIMEOUT:
            self.target_linear = 0.0
            self.target_angular = 0.0

        self.current_linear = self.ramp(
            self.current_linear, self.target_linear, ACCEL_LINEAR, DECEL_LINEAR, dt)
        self.current_angular = self.ramp(
            self.current_angular, self.target_angular, ACCEL_ANGULAR, DECEL_ANGULAR, dt)

        # Snap to zero if negligible
        if abs(self.current_linear) < 1e-3 and self.target_linear == 0.0:
            self.current_linear = 0.0
        if abs(self.current_angular) < 1e-3 and self.target_angular == 0.0:
            self.current_angular = 0.0

        # Publish command
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.twist.linear.x = float(self.current_linear)
        msg.twist.angular.z = float(self.current_angular)
        self.publisher_.publish(msg)

    def handle_key(self, key):
        now = time.monotonic()
        self.last_key_time = now

        # Forward
        if key in ('i', 'w', 'A'):  # 'A' is Up arrow in escape sequence
            self.target_linear = self.max_speed
        # Backward
        elif key in (',', 's', 'B'):  # 'B' is Down arrow
            self.target_linear = -self.max_speed * 0.75  # Moderate reverse
        # Turn Left
        elif key in ('j', 'a', 'D'):  # 'D' is Left arrow
            self.target_angular = self.max_turn
        # Turn Right
        elif key in ('l', 'd', 'C'):  # 'C' is Right arrow
            self.target_angular = -self.max_turn
        # Stop
        elif key in ('k', ' '):
            self.target_linear = 0.0
            self.target_angular = 0.0
            self.current_linear = 0.0
            self.current_angular = 0.0
        # Speed adjustments
        elif key == '+':
            self.max_speed = min(SPEED_LIMIT_MAX, self.max_speed + 0.05)
            print(f"\rSpeed limit: {self.max_speed:.2f} m/s", end='', flush=True)
        elif key == '-':
            self.max_speed = max(0.1, self.max_speed - 0.05)
            print(f"\rSpeed limit: {self.max_speed:.2f} m/s", end='', flush=True)


def getKey(settings):
    # Non-blocking check with 50 ms timeout
    rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
    if rlist:
        ch = sys.stdin.read(1)
        # Handle escape sequence for arrow keys (\x1b[A, \x1b[B, etc.)
        if ch == '\x1b':
            rlist, _, _ = select.select([sys.stdin], [], [], 0.02)
            if rlist:
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    rlist, _, _ = select.select([sys.stdin], [], [], 0.02)
                    if rlist:
                        ch3 = sys.stdin.read(1)
                        return ch3  # 'A', 'B', 'C', 'D'
        return ch
    return None


BANNER = """
============================================================
  INNEX-1 Progressive Keyboard Teleop (Deadman Control)
============================================================
  HOLD key to drive (stops automatically when released):
    [W] or [I] or [Up]    : Drive Forward (progressively ramps)
    [S] or [,] or [Down]  : Drive Backward
    [A] or [J] or [Left]  : Pivot Turn Left
    [D] or [L] or [Right] : Pivot Turn Right
    [Space] or [K]        : Immediate Emergency Stop

  Speed Control (Max limit: 0.60 m/s):
    [+] : Increase Max Speed (+0.05 m/s)
    [-] : Decrease Max Speed (-0.05 m/s)

  Press [Ctrl+C] to Exit
============================================================
"""


def main(args=None):
    rclpy.init(args=args)
    node = ProgressiveKeyboardTeleop()

    print(BANNER)
    print(f"Current Max Speed: {node.max_speed:.2f} m/s (Capped at {SPEED_LIMIT_MAX:.2f} m/s)\n")

    old_settings = None
    if sys.stdin.isatty():
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())

    dt = 1.0 / LOOP_RATE
    try:
        while rclpy.ok():
            key = getKey(old_settings)
            if key == '\x03':  # Ctrl+C
                break
            elif key:
                node.handle_key(key)

            node.update_velocity(dt)
            time.sleep(dt)
    finally:
        # Publish final zero command
        msg = TwistStamped()
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        node.publisher_.publish(msg)

        if old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
