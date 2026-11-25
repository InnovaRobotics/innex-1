"""Check installed launch startup and repeated SIGINT cleanup in dry-run mode."""

import os
import selectors
import signal
import subprocess
import time


def test_installed_launch_ctrl_c():
    """Let launch forward Ctrl+C without interrupting the child's cleanup."""
    process = subprocess.Popen(
        ['ros2', 'launch', 'innex_drive_bridge', 'drive_bridge.launch.py'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        start_new_session=True)
    output = ''
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    try:
        deadline = time.monotonic() + 10
        while 'state=startup_zero_sent' not in output and time.monotonic() < deadline:
            if selector.select(timeout=0.1):
                line = process.stdout.readline()
                if not line:
                    break
                output += line
        assert 'dry_run=True' in output, output
        assert 'state=startup_zero_sent' in output, output
        os.killpg(process.pid, signal.SIGINT)
        tail, _ = process.communicate(timeout=10)
        output += tail
        assert process.returncode == 0, output
        assert 'Traceback' not in output, output
        assert 'process has finished cleanly' in output, output
    finally:
        selector.close()
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
