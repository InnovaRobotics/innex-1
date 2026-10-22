# Copyright 2026 Leo-P-1109
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
