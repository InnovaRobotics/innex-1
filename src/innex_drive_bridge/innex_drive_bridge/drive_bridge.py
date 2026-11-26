"""Bridge /cmd_vel commands to the Teensy 4.1 over USB serial."""

import math
import signal
import termios
import time

from geometry_msgs.msg import TwistStamped
from innex_drive_bridge.protocol import encode, MAX_WHEEL_RAD_S, wheel_targets
from rcl_interfaces.msg import ParameterDescriptor
import rclpy
from rclpy.clock import Clock, ClockType
from rclpy.executors import ExternalShutdownException, SingleThreadedExecutor
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from rclpy.signals import SignalHandlerOptions
import serial

COMMAND_TIMEOUT_NS = 500_000_000
SHUTDOWN_DRAIN_S = 0.05
WRITE_TIMEOUT_S = 0.01


class DriveBridge(Node):
    """Convert fresh /cmd_vel commands into 18-byte Teensy frames at a steady rate."""

    def __init__(self):
        """Validate parameters and open the serial port unless running in dry-run mode."""
        super().__init__('drive_bridge')

        read_only = ParameterDescriptor(read_only=True)
        self.dry_run = self.declare_parameter('dry_run', True, read_only).value
        serial_port = self.declare_parameter('serial_port', '', read_only).value
        rate = self.declare_parameter('send_rate_hz', 50.0, read_only).value
        self.radius = self.declare_parameter('wheel_radius_m', 0.154, read_only).value
        self.track = self.declare_parameter('track_width_m', 0.614, read_only).value
        self.max_wheel_rad_s = self.declare_parameter(
            'max_wheel_rad_s', MAX_WHEEL_RAD_S, read_only).value
        self.command_frame = self.declare_parameter(
            'command_frame', 'base_link', read_only).value

        if not math.isfinite(rate) or not 20.0 <= rate <= 100.0:
            raise ValueError('send_rate_hz must be between 20 and 100 Hz')

        if not self.command_frame:
            raise ValueError('command_frame must not be empty')

        wheel_targets(0.0, 0.0, self.radius, self.track, self.max_wheel_rad_s)

        self.port = None
        if not self.dry_run:
            if self.get_parameter('use_sim_time').value:
                raise ValueError('Serial mode cannot use simulation time')

            if not serial_port:
                raise ValueError('serial_port is required when dry_run is false')

            self.port = serial.Serial(
                port=serial_port,
                timeout=0,
                write_timeout=WRITE_TIMEOUT_S,
                exclusive=True,
            )
            try:
                self.port.reset_input_buffer()
                self.port.reset_output_buffer()
            except (OSError, termios.error) as exc:
                self.port.close()
                raise serial.SerialException(str(exc)) from exc

        self.sequence = (time.monotonic_ns() // 1_000_000) & 0xFFFFFFFF
        self.target = (0, 0)
        self.deadline_ns = 0
        self.armed = False
        self.fault = None
        self.last_frame = None
        self.state = 'waiting_for_startup_zero'
        self.last_report = None

        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )
        self.subscription = self.create_subscription(
            TwistStamped, '/cmd_vel', self.on_command, qos)
        self.timer = self.create_timer(
            1.0 / rate, self.on_timer, clock=Clock(clock_type=ClockType.STEADY_TIME))

        self.get_logger().info(f'Drive bridge started; dry_run={self.dry_run}; watchdog=500 ms')

    def on_command(self, message):
        """Store the newest wheel target and reset the 500 ms arrival deadline."""
        if not self.armed or self.fault is not None:
            return

        if message.header.frame_id != self.command_frame:
            self._stop('invalid_frame')
            return

        twist = message.twist
        try:
            target = wheel_targets(
                twist.linear.x, twist.angular.z,
                self.radius, self.track, self.max_wheel_rad_s,
            )
        except ValueError:
            self._stop('invalid_velocity')
            return

        self.target = target
        self.deadline_ns = time.monotonic_ns() + COMMAND_TIMEOUT_NS
        self.state = 'active'

    def on_timer(self):
        """Send the active wheel target, or zero on startup and after 500 ms of silence."""
        if self.fault is not None:
            return

        now_ns = time.monotonic_ns()
        if not self.armed:
            target = (0, 0)
        elif now_ns >= self.deadline_ns:
            if self.deadline_ns:
                self._stop('command_timeout')
                self.get_logger().warning('No /cmd_vel for 0.5 s; stopping wheels.')
            target = (0, 0)
        else:
            target = self.target

        try:
            self._write_frame(*target)
        except (OSError, termios.error, serial.SerialException, ValueError) as exc:
            self.fault = str(exc)
            self.armed = False
            self._stop('serial_fault')
            self._discard_and_close_port()
            self.get_logger().error(f'Serial fault latched; restart after check: {self.fault}')
            return

        if not self.armed:
            self.armed = True
            self.state = 'startup_zero_sent'

        report = (target, self.state)
        if report != self.last_report:
            self.get_logger().info(f'Targets mrad/s={target}; state={self.state}')
            self.last_report = report

    def close(self):
        """Send one final zero frame and let it drain for up to 50 ms before closing."""
        self.timer.cancel()
        self._stop('shutdown')

        try:
            if self.fault is None:
                self._write_frame(0, 0)
                if self.port is not None and self.port.is_open:
                    deadline = time.monotonic() + SHUTDOWN_DRAIN_S
                    while time.monotonic() < deadline and self.port.out_waiting:
                        time.sleep(0.002)
        except (OSError, termios.error, serial.SerialException, ValueError):
            pass
        finally:
            if self.port is not None and self.port.is_open:
                try:
                    self.port.close()
                except OSError:
                    pass

    def _stop(self, reason):
        self.target = (0, 0)
        self.deadline_ns = 0
        self.state = reason

    def _write_frame(self, left_mrad_s, right_mrad_s):
        frame = encode(self.sequence, left_mrad_s, right_mrad_s)
        self.sequence = (self.sequence + 1) & 0xFFFFFFFF

        if self.port is not None:
            if self.port.out_waiting:
                raise serial.SerialTimeoutException('Previous frame is still queued')
            if self.port.write(frame) != len(frame):
                raise serial.SerialTimeoutException('Partial frame write')

        self.last_frame = frame

    def _discard_and_close_port(self):
        if self.port is None:
            return
        try:
            if self.port.is_open:
                self.port.reset_output_buffer()
        except (OSError, termios.error):
            pass
        finally:
            try:
                self.port.close()
            except OSError:
                pass


def main(args=None):
    """Spin on one thread and finish the active callback cleanly on SIGINT or SIGTERM."""
    stop_requested = False

    def request_stop(signum, frame):
        nonlocal stop_requested
        stop_requested = True

    previous = {
        signum: signal.signal(signum, request_stop)
        for signum in (signal.SIGINT, signal.SIGTERM)
    }
    node = None
    executor = None
    try:
        rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
        node = DriveBridge()
        executor = SingleThreadedExecutor()
        executor.add_node(node)
        while rclpy.ok() and not stop_requested:
            executor.spin_once(timeout_sec=0.05)
    except ExternalShutdownException:
        pass
    finally:
        if executor is not None and node is not None:
            executor.remove_node(node)
        if node is not None:
            try:
                node.close()
            finally:
                node.destroy_node()
        rclpy.try_shutdown()
        for signum, handler in previous.items():
            signal.signal(signum, handler)


if __name__ == '__main__':
    main()
